import time
import csv
import os


def record_rounds(filename, fieldnames):
    rounds_data = []
    file_exists = os.path.isfile(filename)
    prompts = ["Start Ball", "Lap 1", "Lap 2", "Start Wheel", "Wheel Lap"]
    try:
        while True:
            timestamps = []
            print("\n")
            for i, prompt in enumerate(prompts):
                input(f"{i + 1} {prompt}...")
                timestamps.append(time.time())

            sector = input(f"{fieldnames[2]}: ")
            rounds_data.append(
                {
                    fieldnames[0]: timestamps[1] - timestamps[0],
                    fieldnames[1]: timestamps[2] - timestamps[1],
                    fieldnames[2]: sector,
                    fieldnames[3]: timestamps[4] - timestamps[3],
                }
            )

            cont = input("<Enter> to continue ")
            if cont != "":
                break

    except KeyboardInterrupt:
        print("Interrupted by the user")

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerows(rounds_data)


if __name__ == "__main__":
    filename = input("Enter the filename: ")
    column = input("Enter column name: ")
    fieldnames = ["First Lap", "Second Lap", column, "Wheel Lap"]
    record_rounds(filename, fieldnames)
