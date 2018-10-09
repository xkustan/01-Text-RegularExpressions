import re


class Person(object):
    def __init__(self, name, born, died, type):
        self.name = name
        self.born = born
        self.died = died
        self.type = type

    def __repr__(self):
        return "{0} ({1}--{2})".format(self.name, self.born, self.died)


class Editor(Person):
    def __init__(self, name=None, born=None, died=None):
        Person.__init__(self, name, born, died, "editor")

    def create_from_text(self, text_editor):
        tmp_name, *rest = text_editor.split("(")
        self.name = tmp_name.strip().strip("[").strip("]")
        if self.name.strip() == "":
            self.name = None


class Composer(Person):
    def __init__(self, name=None, born=None, died=None):
        Person.__init__(self, name, born, died, "composer")

    def create_from_text(self, text_composer):
        text_composer = text_composer.strip()
        tmp_name, *rest = text_composer.split("(")
        self.name = tmp_name.strip()
        if self.name.strip() == "":
            self.name = None

        # normal range
        parsed = re.search("(\d\d\d\d--\d\d\d\d)", text_composer)
        if parsed:
            b, d = parsed.group().split("--")
            self.born, self.died = int(b), int(d)
            return

        # born start with *
        parsed = re.search("\*\d\d\d\d", text_composer)
        if parsed:
            self.born = int(parsed.group()[1:6])
            return

        # died start with +
        parsed = re.search("\+\d\d\d\d", text_composer)
        if parsed:
            self.died = int(parsed.group()[1:6])
            return

        parsed = re.search("(None--\d\d\d\d)", text_composer)
        if parsed:
            b, d = parsed.group().split("--")
            self.born, self.died = None, int(d)
            return

        parsed = re.search("(\d\d\d\d--None)", text_composer)
        if parsed:
            b, d = parsed.group().split("--")
            self.born, self.died = int(b), None
            return


class Voice(object):
    def __init__(self, name=None, range=None):
        self.name = name
        self.range = range

    def __repr__(self):
        return "{0}, {1}".format(self.range, self.name)

    def create_from_text(self, text_voice):
        if "--" in text_voice:
            temp_range, *temp_name = text_voice.split(",")
            self.name = "".join(temp_name).strip()
            self.range = temp_range.strip()
        else:
            text_voice = text_voice.strip()
            if text_voice.startswith("None, "):
                self.range = None
                self.name = text_voice.lstrip("None,").strip()
            else:
                self.name = text_voice


class Composition(object):
    def __init__(self, name=None, incipit=None, key=None, genre=None, year=None, voices=None, authors=None):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices or []
        self.authors = authors or []

    def set_composers(self, text_value):
        if ";" in text_value:
            composers = [c.strip() for c in text_value.split(";")]
        elif "r/F" in text_value:
            composers = [c.strip() for c in text_value.split("/")]
        elif "&" in text_value:
            composers = [c.strip() for c in text_value.split("&")]
        elif text_value.strip()[0] == "[":
            composers = [c.strip() for c in text_value.strip()[1:-1].split("),")]
        else:
            composers = [text_value.strip()]

        for comp in composers:
            composer = Composer()
            composer.create_from_text(comp)
            if composer.name:
                self.authors.append(composer)

    def set_name(self, text_value):
        self.name = text_value

    def set_genre(self, text_value):
        self.genre = text_value

    def set_key(self, text_value):
        self.key = text_value

    def set_year(self, text_value):
        try:
            if int(text_value) in range(999, 10000):
                self.year = text_value
            else:
                raise ValueError
        except ValueError:
            self.year = None

    def set_incipit(self, text_value):
        self.incipit = text_value

    def add_voice(self, text_value):
        voice = Voice()
        voice.create_from_text(text_value)
        self.voices.append(voice)


class Edition(object):
    def __init__(self, composition=None, authors=None, name=None):
        self.composition = composition or self._create_default_composition()
        self.authors = authors or []
        self.name = name

    @staticmethod
    def _create_default_composition():
        return Composition()

    def add_name(self, text_value):
        self.name = text_value.strip()

    def add_authors(self, text_value):
        text_value = text_value.strip()
        if "continuo by" in text_value:
            editors = [e.strip() for e in text_value.split(", continuo by")]
        elif "continuo" in text_value:
            editors = [e.strip() for e in text_value.split(", continuo")]
        elif "," in text_value:
            editors = []
            edis = [e.strip() for e in text_value.split(",")]
            if " " in edis[0]:
                editors.extend(edis)
            else:
                for i in range(0, len(edis), 2):
                    editors.append(edis[i] + " " + edis[i + 1])
        else:
            editors = [text_value]

        for edo in editors:
            editor = Editor()
            editor.create_from_text(edo)
            if editor.name:
                self.authors.append(editor)


class Print(object):
    def __init__(self, print_id, edition=None, partiture=None):
        self.print_id = print_id
        self.edition = edition or self._create_default_edition()
        self.partiture = partiture

    @staticmethod
    def _create_default_edition():
        return Edition()

    def composition(self):
        return self.edition.composition

    def format(self):
        voice_prints = []
        for i, voice in enumerate(self.edition.composition.voices):
            voice_prints.append(VOICE_TEMPLATE.format(i + 1, voice))

        if voice_prints:
            printed_voice = "\n" + "\n".join(voice_prints)
        else:
            printed_voice = ""

        to_print = PRINT_TEMPLATE.format(
            self.print_id,
            self.edition.composition.authors,
            self.edition.composition.name,
            self.edition.composition.genre,
            self.edition.composition.key,
            self.edition.composition.year,
            self.edition.name,
            self.edition.authors,
            printed_voice,
            self.partiture,
            self.edition.composition.incipit,
        )

        print(to_print)

    def set_partiture_from_text(self, text_value):
        if text_value.strip() in ("yes", "True"):
            self.partiture = True
        elif text_value.strip() in ("no", "False"):
            self.partiture = False
        else:
            self.partiture = None


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


PRINT_TEMPLATE = """Print Number: {0}
Composer: {1}
Title: {2}
Genre: {3}
Key: {4}
Composition Year: {5} 
Edition: {6}
Editor: {7}{8}
Partiture: {9}
Incipit: {10}
"""

VOICE_TEMPLATE = """Voice {0}: {1}"""
