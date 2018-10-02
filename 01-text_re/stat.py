import re
import sys
from collections import Counter

# composers

def get_composer(raw_name):
    return raw_name.split("(")[0].strip()


def count_composers():
    counter = Counter()

    with open(path, "r") as file:
        composer_pattern = re.compile("(Composer: )(.*)")

        for line in file:
            parsed_names = parse_line(composer_pattern, line)
            if not parsed_names or parsed_names.strip() == "":
                continue
            if "&" in parsed_names:
                for parsed_name in parsed_names.split("&"):
                    name = get_composer(parsed_name)
                    counter[name] += 1
            elif "r/F" in parsed_names:
                for parsed_name in parsed_names.split("/"):
                    name = get_composer(parsed_name)
                    counter[name] += 1
            else:
                for parsed_name in parsed_names.split(";"):
                    name = get_composer(parsed_name)
                    counter[name] += 1

    return counter


def print_composers_counts(composers):
    for name, count in composers.most_common():
        print("%s: %d" % (name, count))

# composed centuries

def count_comosation_centurie():
    counter = Counter()

    with open(path, "r") as file:
        composation_pattern = re.compile("(Composition Year: )(.*)")

        for line in file:
            parsed_year_or_century = parse_line(composation_pattern, line)
            if not parsed_year_or_century or parsed_year_or_century.strip() == "":
                continue
            if "century" in parsed_year_or_century:
                century = int(parsed_year_or_century.split("th")[0])
            else:
                year_pattern = re.compile(r"(\d{4})")
                year = search_line(year_pattern, parsed_year_or_century)
                century = int(str(int(year)-1)[:2])+1
            counter[century] += 1

    return counter


def print_centuries(composed_at):
    for name, count in sorted(composed_at.items()):
        print("%dth century: %d" % (name, count))


def count_c_minor():
    """
    Info about c minor key is under Key or in Title, but never in both.
    Stupid simple solution.
    :return:
    """
    with open(path, "r") as file:
        all_occurences = re.findall("c minor", file.read())
        return len(all_occurences)

# parsers
def parse_line(pattern, line):
    parsed_line = re.match(pattern, line)
    if parsed_line:
        return parsed_line.group(2)


def search_line(pattern, line):
    found = re.search(pattern, line)
    if found:
        return found.group(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("First argument should be path to library, second argument should be mode [composer, century, cminor]")

    path = sys.argv[1]

    try:
        if sys.argv[2] == "composer":
            counted_composers = count_composers()
            print_composers_counts(counted_composers)
        elif sys.argv[2] == "century":
            composation_centuries = count_comosation_centurie()
            print_centuries(composation_centuries)
        elif sys.argv[2] == "cminor":
            cminor_count = count_c_minor()
            print("%d compositions in c minor key" % cminor_count)
        else:
            print("Unknown mode, choose one from [composer, century, cminor]")
    except FileNotFoundError:
        print("Bad path to file")
