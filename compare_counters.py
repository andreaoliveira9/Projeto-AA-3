import json
import numpy as np
import os


def obtain_exact_counters(title):

    with open("counters/exact_counter/" + title + ".txt", "r", encoding="utf8") as file:
        line = file.readline()
        counters = dict(json.loads(line))

        return dict(sorted(counters.items(), key=lambda item: item[1], reverse=True))


def compare_approximate_counters(title, exact_counters):
    # Inicializar métricas de comparação
    total_words = []
    words = {}
    most_frequent_words = {}

    # Ler contadores aproximados do arquivo
    with open(
        f"counters/approximate_counter/{title}.txt", "r", encoding="utf8"
    ) as file:
        for line in file:
            # Obter contadores aproximados
            counters = json.loads(line)
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

            # Atualizar palavra mais frequente
            most_frequent_word = list(counters.keys())[0]
            most_frequent_words[most_frequent_word] = (
                most_frequent_words.get(most_frequent_word, 0) + 1
            )

    # Cálculo dos valores médios de contadores
    avg_counts = {word: np.mean(counts) for word, counts in words.items()}
    avg_counts = dict(
        sorted(avg_counts.items(), key=lambda item: item[1], reverse=True)
    )

    # Valores esperados com base no algoritmo aproximado
    prob = 1 / 16
    expected_value_dict = {word: count * prob for word, count in exact_counters.items()}
    expected_value = sum(expected_value_dict.values())
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

    # Ordenar palavras mais frequentes
    most_frequent_words = dict(
        sorted(most_frequent_words.items(), key=lambda item: item[1], reverse=True)
    )

    # Escrever estatísticas em um arquivo
    with open(
        f"statistics/approximate_counter/{title}.txt", "w", encoding="utf8"
    ) as stats:
        stats.write(f"Expected value: {expected_value}\n")
        stats.write(f"Variance: {real_variance}\n")
        stats.write(f"Standard deviation: {real_standard_deviation}\n\n")

        stats.write(f"Mean absolute error: {mean_absolute_error}\n")
        stats.write(f"Mean relative error: {mean_relative_error:.2f}%\n")
        stats.write(f"Mean accuracy ratio: {mean_accuracy_ratio:.2f}%\n\n")

        stats.write(f"Smallest counter value: {smallest_value}\n")
        stats.write(f"Largest counter value: {largest_value}\n\n")

        stats.write(f"Mean counter value: {mean}\n")
        stats.write(f"Mean absolute deviation: {mean_absolute_deviation}\n")
        stats.write(f"Standard deviation: {standard_deviation}\n")
        stats.write(f"Maximum deviation: {maximum_deviation}\n")
        stats.write(f"Variance: {variance}\n\n")

        stats.write("Mean Counter Values per Word:\n")
        stats.write("Word : Counter Value : Expected Value\n")
        for word, counter in avg_counts.items():
            stats.write(
                f"{word:<15} : {counter:<13.2f} : {expected_value_dict.get(word, 0):.2f}\n"
            )

        stats.write("\nMost Frequent Word: {real_order.split()[0]}\n")
        most_freq_word = max(
            most_frequent_words, key=most_frequent_words.get, default=None
        )
        if most_freq_word:
            freq_word_accuracy = (
                most_frequent_words[most_freq_word] / sum(most_frequent_words.values())
            ) * 100
            stats.write(f"Word Accuracy: {freq_word_accuracy:.2f}%\n")
        stats.write("10 Most Frequent Words:\n")
        for i, word in enumerate(most_frequent_words):
            if i >= 10:
                break
            stats.write(f"{word} ")


def calculate_errors(real_value, counters, expected_value):
    counters = np.array(counters)
    real_variance = expected_value / 2
    real_standard_deviation = np.sqrt(real_variance)
    mean = counters.mean()
    variance = counters.var()
    standard_deviation = counters.std()
    mean_absolute_deviation = np.mean(np.abs(counters - mean))
    maximum_deviation = np.max(np.abs(counters - mean))
    mean_absolute_error = np.mean(np.abs(counters - real_value))
    mean_relative_error = np.mean(np.abs(counters - real_value) / real_value) * 100
    mean_accuracy_ratio = mean / expected_value if expected_value != 0 else 0
    smallest_value = counters.min()
    largest_value = counters.max()

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


def compare_frequent_counters(title, exact_counters):
    all_k = [5, 10, 15, 20]

    for k in all_k:
        with open(
            f"counters/frequent_counter/{title}_K{k}.txt", "r", encoding="utf8"
        ) as file:
            counters = json.loads(file.readline())

        top_k_words = sorted(exact_counters.items(), key=lambda x: x[1], reverse=True)[
            : k - 1
        ]

        with open(
            f"statistics/frequent_counter/{title}_K{k}.txt", "w", encoding="utf8"
        ) as stats:
            stats.write(f"Top {k-1} words (Exact Counter):\n")
            for word, count in top_k_words:
                stats.write(f"{word}: {count}\n")

            stats.write("\nTop {k-1} words (Frequent-Counter):\n")
            for word, count in sorted(
                counters.items(), key=lambda x: x[1], reverse=True
            ):
                stats.write(f"{word}: {count}\n")

            accurate_words = len([word for word, _ in top_k_words if word in counters])
            accuracy = accurate_words / (k - 1)

            stats.write(f"\nAccurate words: {accurate_words}/{k-1}\n")
            stats.write(f"Accuracy: {accuracy * 100:.2f}%\n")


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
        compare_frequent_counters(book, exact_counters)
