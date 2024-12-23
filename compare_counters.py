import json
import numpy as np
import os
from frequent_counter import ALL_K
from approximate_counter import N_TRIALS


def obtain_exact_counters(title):

    with open("counters/exact_counter/" + title + ".txt", "r", encoding="utf8") as file:
        line = file.readline()
        counters = dict(json.loads(line))

        return dict(sorted(counters.items(), key=lambda item: item[1], reverse=True))


def compare_approximate_counters(title, exact_counters):
    for trials in N_TRIALS:
        # Inicializar métricas de comparação
        total_words = []
        words = {}
        most_frequent_words = {}

        # Ler contadores aproximados do arquivo
        with open(
            f"counters/approximate_counter/{title}_{trials}.txt", "r", encoding="utf8"
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

        # Cálculo dos valores médios de contadores
        avg_counts = {word: np.mean(counts) for word, counts in words.items()}
        avg_counts = dict(
            sorted(avg_counts.items(), key=lambda item: item[1], reverse=True)
        )

        # Valores esperados com base no algoritmo aproximado
        prob = 1 / 16
        expected_value_dict = {
            word: count * prob for word, count in exact_counters.items()
        }
        expected_value = sum(expected_value_dict.values())

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
        ) = calculate_errors(total_words, expected_value)

        # Extrair as 10 palavras mais frequentes dos contadores aproximados
        approx_top_10 = list(avg_counts.keys())[:10]

        # Extrair as 10 palavras mais frequentes da ordem real (exact_counters)
        real_top_10 = list(
            dict(
                sorted(exact_counters.items(), key=lambda item: item[1], reverse=True)
            ).keys()
        )[:10]

        # Comparar as 10 palavras mais frequentes
        matched_words = set(approx_top_10).intersection(set(real_top_10))
        top_10_accuracy = (
            len(matched_words) / 10 * 100
        )  # Percentagem de palavras coincidentes

        # Comparar as 10 palavras mais frequentes considerando a ordem
        order_matches = sum(
            1
            for i, word in enumerate(approx_top_10)
            if i < len(real_top_10) and word == real_top_10[i]
        )
        freq_word_accuracy = (
            order_matches / 10
        ) * 100  # Percentagem de correspondências na ordem exata

        # Escrever estatísticas em um arquivo
        with open(
            f"statistics/approximate_counter/{title}_{trials}.txt", "w", encoding="utf8"
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

            stats.write("\nMost Frequent Words (Top 10):\n")
            stats.write(f"Real Order: {', '.join(real_top_10)}\n")
            stats.write(f"Approx Order: {', '.join(approx_top_10)}\n")
            stats.write(f"Top 10 Accuracy: {top_10_accuracy:.2f}%\n")
            stats.write(
                f"Word Match Accuracy (with order): {freq_word_accuracy:.2f}%\n"
            )


def calculate_errors(counters, expected_value):
    counters = np.array(counters)
    real_variance = expected_value / 2
    real_standard_deviation = np.sqrt(real_variance)
    mean = counters.mean()
    variance = counters.var()
    standard_deviation = counters.std()
    mean_absolute_deviation = np.mean(np.abs(counters - mean))
    maximum_deviation = np.max(np.abs(counters - mean))

    # Corrigir cálculos de erro absoluto médio e relativo médio
    mean_absolute_error = np.mean(np.abs(counters - expected_value))
    mean_relative_error = (
        np.mean(np.abs(counters - expected_value) / expected_value) * 100
    )

    # Razão de acurácia média
    mean_accuracy_ratio = (
        1 - np.mean(np.abs(counters - expected_value) / expected_value)
    ) * 100

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
    for k in ALL_K:
        with open(
            f"counters/frequent_counter/{title}_K{k}.txt", "r", encoding="utf8"
        ) as file:
            counters = json.loads(file.readline())

        top_k_words = sorted(exact_counters.items(), key=lambda x: x[1], reverse=True)[
            :k
        ]

        with open(
            f"statistics/frequent_counter/{title}_K{k}.txt", "w", encoding="utf8"
        ) as stats:
            stats.write(f"Top {k} words (Exact Counter):\n")
            for word, count in top_k_words:
                stats.write(f"{word}: {count}\n")

            stats.write(f"\nTop {k}words (Frequent-Counter):\n")
            for word, count in sorted(
                counters.items(), key=lambda x: x[1], reverse=True
            ):
                stats.write(f"{word}: {count}\n")

            accurate_words = len([word for word, _ in top_k_words if word in counters])
            accuracy = accurate_words / k

            stats.write(f"\nAccurate words: {accurate_words}/{k}\n")
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
        # compare_approximate_counters(book, exact_counters)

        # Compare data stream counters
        compare_frequent_counters(book, exact_counters)
