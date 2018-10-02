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
        self.name = tmp_name.strip()


class Composer(Person):
    def __init__(self, name=None, born=None, died=None):
        Person.__init__(self, name, born, died, "composer")

    def create_from_text(self, text_composer):
        tmp_name, *rest = text_composer.split("(")
        self.name = tmp_name.strip()

        # normal range
        parsed = re.search("(\d\d\d\d--\d\d\d\d)", text_composer)
        if parsed:
            b, d = parsed.group().split("--")
            self.born, self.died = int(b), int(d)

        # born start with *
        parsed = re.search("\*\d\d\d\d", text_composer)
        if parsed:
            self.born = int(parsed.group()[1:6])

        # died start with +
        parsed = re.search("\+\d\d\d\d", text_composer)
        if parsed:
            self.died = int(parsed.group()[1:6])


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
            self.name = text_voice.strip()


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
        else:
            composers = [text_value.strip()]

        for comp in composers:
            composer = Composer()
            composer.create_from_text(comp)
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
            editors = [e.strip() for e in text_value.split("continuo by")]
        elif "continuo" in text_value:
            editors = [e.strip() for e in text_value.split("continuo")]
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

        to_print = PRINT_TEMPLATE.format(
            self.print_id,
            self.edition.composition.authors,
            self.edition.composition.name,
            self.edition.composition.genre,
            self.edition.composition.key,
            self.edition.composition.year,
            self.edition.name,
            self.edition.authors,
            "\n".join(voice_prints),
            self.partiture,
            self.edition.composition.incipit,
        )

        print(to_print)

    def set_partiture_from_text(self, text_value):
        if text_value.strip() == "yes":
            self.partiture = True
        elif text_value.strip() == "no":
            self.partiture = False
        else:
            self.partiture = None


PRINT_TEMPLATE = """
Print Number: {0}
Composer: {1}
Title: {2}
Genre: {3}
Key: {4}
Composition Year: {5} 
Edition: {6}
Editor: {7}
{8}
Partiture: {9}
Incipit: {10}"""

VOICE_TEMPLATE = "Voice {0}: {1}"
