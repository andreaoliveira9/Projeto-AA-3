from utils import process_files
import random
import time
import json

N_TRIALS = [1, 10, 100, 1000]


def approximate_counter(stream):

    # Start timer
    start = time.time()

    words = stream.split()

    # Initialize the counter
    counter = {}

    for word in words:

        if word not in counter:
            counter[word] = 0

        # Fixed probability counter : 1 / 16
        prob = 1 / 16

        # Increment with previous probability
        if random.random() <= prob:
            counter[word] += 1

    return counter, time.time() - start


if __name__ == "__main__":

    # Open file to store time statistics
    stats = open("statistics/time_approximate_counter.txt", "w", encoding="utf-8")
    stats.write(f'{"Title":<80} {"Time":<25}\n')

    streams = process_files()
    for title in streams:
        for trials in N_TRIALS:
            file = open(
                "counters/approximate_counter/" + title + "_" + str(trials) + ".txt",
                "w",
                encoding="utf-8",
            )
            avg_time = 0

            for trial in range(trials):

                # Obtain approximate counters
                counter, processing_time = approximate_counter(streams[title])

                # Store the approximate counters
                file.write(json.dumps(counter) + "\n")

                # Update average processing time
                avg_time += processing_time

            # Store average processing time
            stats.write(
                f'{title + "_" + str(trials) + ":":<80} {avg_time / trials:<25}\n'
            )

            file.close()

    stats.close()
