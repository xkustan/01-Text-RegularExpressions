import re

class Person(object):
    def __init__(self, name, born, died, type):
        self.name = name
        self.born = born
        self.died = died
        self.type = type

    def __repr__(self):
        return "Name: {0}, Born: {1}, Died: {2}".format(self.name, self.born, self.died)


class Editor(Person):
    def __init__(self, name=None, born=None, died=None):
        Person.__init__(self, name, born, died, "editor")


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
        return "Name: {0}, Range: {1}".format(self.name, self.range)

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

    def __repr__(self):
        return "Name: {0}, Incipit: {1}, Key: {2}, Genre: {3}, Year: {4}, Voices: {5}, Authors: {6}".format(
            self.name, self.incipit, self.key, self.genre, self.year, self.voices, self.authors
        )

    def set_composers(self, text_value):
        for c in text_value.split(";"):
            composer = Composer()
            composer.create_from_text(c.strip())
            self.authors.append(composer)

    def set_name(self, text_value):
        self.name = text_value

    def set_genre(self, text_value):
        self.genre = text_value

    def set_key(self, text_value):
        self.key = text_value

    def set_year(self, text_value):
        try:
            if int(text_value) > 999 and int(text_value) < 10000:
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

    @staticmethod
    def _clean_composer(raw_name):
        only_name = raw_name.split("(")[0].strip()
        surname, *rest = only_name.split(" ")
        initials = ""
        for name in rest:
            if name.strip()[-1] == ".":
                initials += name
            else:
                initials += "{0}.".format(name[0])
        return "{0} {1}".format(surname, initials)


class Edition(object):
    def __init__(self, composition=None, authors=None, name=None):
        self.composition = composition or self._create_default_composition()
        self.authors = authors or []
        self.name = name

    def __repr__(self):
        return "Name: {0}, Authors: {1}, Composition: {2}".format(self.name, self.authors, self.composition)

    @staticmethod
    def _create_default_composition():
        return Composition()


class Print(object):
    def __init__(self, print_id, edition=None, partiture=None):
        self.print_id = print_id
        self.edition = edition or self._create_default_edition()
        self.partiture = partiture

    @staticmethod
    def _create_default_edition():
        return Edition()

    def format(self):
        print("""Print ID: {0}, Edition: {1}, Partiture: {2}""".format(
            self.print_id, self.edition, self.partiture)
        )

    def set_partiture_from_text(self, text_value):
        if text_value.strip() == "yes":
            self.partiture = True
        elif text_value.strip() == "no":
            self.partiture = False
        else:
            self.partiture = None
