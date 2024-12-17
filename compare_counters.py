import json
import numpy as np
import os


def obtain_exact_counters(title):

    with open("counters/exact_counter/" + title + ".txt", "r", encoding="utf8") as file:
        line = file.readline()
        counters = dict(json.loads(line))

        return dict(sorted(counters.items(), key=lambda item: item[1], reverse=True))


def compare_approximate_counters(title, exact_counters):
    """
    Compara contadores aproximados de palavras com contadores exatos.

    Args:
        title (str): Nome do arquivo que contém os contadores aproximados.
        exact_counters (dict): Contadores exatos de palavras.

    Returns:
        None
    """
    # Inicializar métricas de comparação
    total_words = []
    words = {}
    total_orders = {}
    first_3_words = {}
    most_frequent_words = {}

    # Ler contadores aproximados do arquivo
    with open(
        "counters/approximate_counter/" + title + ".txt", "r", encoding="utf8"
    ) as file:
        while True:
            line = file.readline()

            # Se EOF, parar
            if not line:
                break

            # Obter contadores aproximados
            counters = dict(json.loads(line))
            counters = dict(
                sorted(counters.items(), key=lambda item: item[1], reverse=True)
            )

            # Obter número total de palavras
            total = sum(counters.values())
            total_words.append(total)

            # Atualizar contagens de palavras
            for word, count in counters.items():
                if word not in words:
                    words[word] = []
                words[word].append(count)

            # Atualizar ordens de palavras
            order = " ".join(counters)
            if order not in total_orders:
                total_orders[order] = 0
            total_orders[order] += 1

            # Atualizar ordem das 3 primeiras palavras
            order = order.split()[:3]
            if " ".join(order) not in first_3_words:
                first_3_words[" ".join(order)] = 0
            first_3_words[" ".join(order)] += 1

            # Atualizar palavra mais frequente
            most_frequent_word = list(counters.keys())[0]
            if most_frequent_word not in most_frequent_words:
                most_frequent_words[most_frequent_word] = 0
            most_frequent_words[most_frequent_word] += 1

    # Cálculo dos valores médios de contadores
    avg_counts = {word: sum(count) / len(count) for word, count in words.items()}
    avg_counts = dict(
        sorted(avg_counts.items(), key=lambda item: item[1], reverse=True)
    )

    # Ordem real (baseada nos contadores exatos)
    real_order = " ".join(exact_counters.keys())

    # Valores esperados com base no algoritmo aproximado
    prob = 1 / 16
    expected_value_dict = {word: count * prob for word, count in exact_counters.items()}

    # Valor esperado total
    expected_value = sum(expected_value_dict.values())

    # Valor real total
    real_value = sum(exact_counters.values())

    # Calcular erros
    (
        real_variance,
        real_standard_deviation,
        mean_absolute_error,
        mean_relative_error,
        mean_accuracy_ratio,
        smallest_value,
        largest_value,
        mean,
        mean_absolute_deviation,
        standard_deviation,
        maximum_deviation,
        variance,
    ) = calculate_errors(real_value, total_words, expected_value)

    # Ordens ordenadas por frequência
    total_orders = {
        word: count
        for word, count in sorted(
            total_orders.items(), key=lambda item: item[1], reverse=True
        )
    }

    # Valores esperados ordenados por frequência
    expected_value_dict = {
        word: count
        for word, count in sorted(
            expected_value_dict.items(), key=lambda item: item[1], reverse=True
        )
    }

    # Primeiras 3 palavras ordenadas por frequência
    first_3_words = {
        word: count
        for word, count in sorted(
            first_3_words.items(), key=lambda item: item[1], reverse=True
        )
    }

    # Palavras mais frequentes ordenadas por frequência
    most_frequent_words = {
        word: count
        for word, count in sorted(
            most_frequent_words.items(), key=lambda item: item[1], reverse=True
        )
    }

    # Precisão da ordem completa
    order_accuracy = (
        total_orders[real_order] / sum(total_orders.values())
        if real_order in total_orders
        else 0
    )

    # Precisão das primeiras 3 palavras
    first_3_words_accuracy = (
        first_3_words[" ".join(real_order.split()[:3])] / sum(first_3_words.values())
        if " ".join(real_order.split()[:3]) in first_3_words
        else 0
    )

    # Escrever estatísticas em um arquivo
    with open(
        "statistics/approximate_counter/" + title + ".txt", "w", encoding="utf8"
    ) as stats:

        stats.write(f"Expected value: {expected_value}\n")
        stats.write(f"Variance: {real_variance}\n")
        stats.write(f"Standard deviation: {real_standard_deviation}\n\n")

        stats.write(f"Mean absolute error: {mean_absolute_error}\n")
        stats.write(f"Mean relative error: {mean_relative_error * 100}%\n")
        stats.write(f"Mean accuracy ratio: {mean_accuracy_ratio * 100}%\n\n")

        stats.write(f"Smallest counter value: {smallest_value}\n")
        stats.write(f"Largest counter value: {largest_value}\n\n")

        stats.write(f"Mean counter value: {mean}\n")
        stats.write(f"Mean absolute deviation: {mean_absolute_deviation}\n")
        stats.write(f"Standard deviation: {standard_deviation}\n")
        stats.write(f"Maximum deviation: {maximum_deviation}\n")
        stats.write(f"Variance: {variance}\n\n")

        stats.write(f"Real Word Frequency Order: {real_order}\n")
        stats.write(f"Word Order Accuracy: {order_accuracy * 100}%\n")
        stats.write("10 Most Common Orders:\n")

        for i, order in enumerate(total_orders):
            if i >= 10:
                break
            stats.write(f"{order}: {total_orders[order]}\n")

        stats.write("\n")

        stats.write(f"Top 3 Word Order Accuracy: {first_3_words_accuracy * 100}%\n")
        stats.write("10 Most Common Word Orders:\n")
        for i, order in enumerate(first_3_words):
            if i >= 10:
                break
            stats.write(f"{order}: {first_3_words[order]}\n")

        stats.write("\n")

        stats.write("Mean Counter Values per Word:\n")
        stats.write(f"Word : Counter Value : Expected Value\n")
        for word, counter in avg_counts.items():
            stats.write(f"{word:<15} : {counter:<13} : {expected_value_dict[word]}\n")

        stats.write("\n")

        stats.write(f"Most Frequent Word: {real_order.split()[0]}\n")
        stats.write(
            f"Word Accuracy: {most_frequent_words[real_order.split()[0]]/sum(most_frequent_words.values()) * 100}%\n"
        )
        stats.write("10 Most Frequent Words:\n")

        for i, word in enumerate(most_frequent_words):
            if i >= 10:
                break
            stats.write(f"{word} ")

        stats.write("\n")


def calculate_errors(real_value, counters, expected_value):

    # Real Variance
    real_variance = expected_value / 2

    # Real standard deviation
    real_standard_deviation = np.sqrt(real_variance)

    # -----------------------------

    n = len(counters)
    mean = sum(counters) / n

    # Maximum deviation
    maximum_deviation = max([abs(total - mean) for total in counters])

    # Mean absolute deviation
    mean_absolute_deviation = sum([abs(total - mean) for total in counters]) / n

    # Variance
    variance = sum([(count - mean) ** 2 for count in counters]) / n

    # Standard deviation (variance ** 0.5)
    standard_deviation = np.sqrt(sum([(count - mean) ** 2 for count in counters]) / n)

    # Mean absolute error
    mean_absolute_error = sum([abs(count - real_value) for count in counters]) / n

    # Mean relative error
    mean_relative_error = (
        sum([abs(count - real_value) / real_value * 100 for count in counters]) / n
    )

    # Mean accuracy ratio
    # mean_accuracy_ratio = len([total for total in total_letters if total == real_total]) / n
    mean_accuracy_ratio = mean / expected_value

    # -----------------------------

    # Smallest counter value
    smallest_value = min(counters)

    # Largest counter value
    largest_value = max(counters)

    return (
        real_variance,
        real_standard_deviation,
        mean_absolute_error,
        mean_relative_error,
        mean_accuracy_ratio,
        smallest_value,
        largest_value,
        mean,
        mean_absolute_deviation,
        standard_deviation,
        maximum_deviation,
        variance,
    )


def compare_data_stream_counters(title, exact_counters):

    # Set all possible k
    all_k = [5, 10, 15, 20]

    for k in all_k:

        with open(
            "counters/frequent_counter/" + title + "_K" + str(k) + ".txt",
            "r",
            encoding="utf8",
        ) as file:
            line = file.readline()
            counters = dict(json.loads(line))

        top_k_letters = sorted(
            exact_counters.items(), key=lambda x: x[1], reverse=True
        )[: k - 1]

        with open(
            "statistics/frequent_counter/" + title + "_K" + str(k) + ".txt",
            "w",
            encoding="utf8",
        ) as stats:

            stats.write(f"Top {k-1} letters (Exact Counter):\n")
            for letter, counter in top_k_letters:
                stats.write(f"{letter}: {counter}\n")

            stats.write("\n")

            stats.write(f"Top {k-1} letters (Frequent-Count):\n")
            for letter, counter in counters.items():
                stats.write(f"{letter}: {counter}\n")

            stats.write("\n")

            # Accurate letters
            accurate_letters = len(
                [letter for letter, counter in top_k_letters if letter in counters]
            )

            # Accuracy
            accuracy = accurate_letters / (k - 1)

            stats.write(f"Accurate letters: {accurate_letters}/{k-1}\n")
            stats.write(f"Accuracy: {accuracy * 100}%\n")


if __name__ == "__main__":

    # All books
    books = [
        book.replace(".txt", "")[:-3]
        for book in os.listdir("Project_Gutenberg")
        if book != ".gitkeep"
    ]

    for book in books:

        exact_counters = obtain_exact_counters(book)

        # Compare approximate counters
        compare_approximate_counters(book, exact_counters)

        # Compare data stream counters
        compare_data_stream_counters(book, exact_counters)
