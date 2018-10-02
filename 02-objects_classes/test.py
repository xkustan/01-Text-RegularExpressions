from scorelib import Print
import re
import sys


def parse_text(pattern, line):
    parsed_line = re.match(pattern, line)
    if parsed_line:
        parsed_text = parsed_line.group(2)
        parsed_text = parsed_text.strip() if parsed_text else None
        if parsed_text == "":
            return None
        return parsed_text


def parse_line(line):
    patterns = {
        "print": re.compile("(Print Number: )(.*)"),
        "composer": re.compile("(Composer: )(.*)"),
        "title": re.compile("(Title: )(.*)"),
        "genre": re.compile("(Genre: )(.*)"),
        "key": re.compile("(Key: )(.*)"),
        "composition_year": re.compile("(Composition Year: )(.*)"),
        "edition": re.compile("(Edition: )(.*)"),
        "editor": re.compile("(Editor: )(.*)"),
        "voice": re.compile("(Voice \d: )(.*)"),
        "partiture": re.compile("(Partiture: )(.*)"),
        "incipit": re.compile("(Incipit: )(.*)"),
    }

    if line == "\n":
        return {
            "type": "newline",
            "value": None,
        }

    for line_type, pattern in patterns.items():
        parsed_line = parse_text(pattern, line)
        if parsed_line:
            return {
                "type": line_type,
                "value": parsed_line,
            }


def load(file_path):
    prints = []

    with open(file_path, "r") as file:

        p = None

        for line in file:

            parsed = parse_line(line)

            if not parsed:
                continue

            parsed_type = parsed["type"]
            parsed_value = parsed["value"]

            if parsed_type == "print":
                p = Print(parsed_value)
                prints.append(p)

            if parsed_type == "composer":
                p.edition.composition.set_composers(parsed_value)

            if parsed_type == "title":
                p.edition.composition.set_name(parsed_value)

            if parsed_type == "genre":
                p.edition.composition.set_genre(parsed_value)

            if parsed_type == "key":
                p.edition.composition.set_key(parsed_value)

            if parsed_type == "composition_year":
                p.edition.composition.set_year(parsed_value)

            if parsed_type == "edition":
                p.edition.add_name(parsed_value)

            if parsed_type == "editor":
                p.edition.add_authors(parsed_value)

            if parsed_type == "voice":
                p.edition.composition.add_voice(parsed_value)

            if parsed_type == "partiture":
                p.set_partiture_from_text(parsed_value)

            if parsed_type == "incipit":
                p.edition.composition.set_incipit(parsed_value)

            # just to be sure
            if parsed_type == "newline":
                p = None

        file.close()

    return prints


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
