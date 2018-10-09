from scorelib import load
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("First argument should be path to library file!")

    filename = sys.argv[1]

    try:
        list_of_prints = load(filename)

        for print_object in list_of_prints:
            print_object.format()

    except FileNotFoundError:
        print("Bad path to library file")
