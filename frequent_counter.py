from utils import process_files
import time
import json


def frequent_counter(stream, k):

    # Start timer
    start = time.time()

    words = stream.split()

    # Initialize the counter
    counter = {}

    # Count the frequency of each element
    for word in words:

        # If the letter is in the counter
        if word in counter:
            # Increment the counter
            counter[word] += 1

        # If the letter is not in the counter
        elif len(counter) < k - 1:
            counter[word] = 1

        else:
            # Decrement all counters
            for key in list(counter.keys()):
                counter[key] -= 1

                # Remover palavras com contagem 0
                if counter[key] == 0:
                    del counter[key]

    return counter, time.time() - start


if __name__ == "__main__":

    # Open file to store time statistics
    stats = open("statistics/time_frequent_counter.txt", "w", encoding="utf-8")
    stats.write(f'{"Title":<40} {"Time":<25} {"k":<10}\n')

    # Set all possible k
    all_k = [5, 10, 15, 20]

    streams = process_files()
    for title in streams:

        counters = []

        for k in all_k:

            counter, processing_time = frequent_counter(streams[title], k)
            stats.write(f'{title + ":":<40} {processing_time:<25} {k:<10}\n')

            # Store the data stream counters
            with open(
                "counters/frequent_counter/" + title + "_K" + str(k) + ".txt",
                "w",
                encoding="utf8",
            ) as file:
                file.write(json.dumps(counter))

            counters.append(counter)
