#Print,Edition,Composition,Voice,Person
path = "scorelib.txt"


class Person:
    def __init__(self, name, born, died):
        self.name =  name
        self.born = born
        self.died =  died


class Voice:
    def __init__(self, name, range):
        self.name =  name
        self. range =  range


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors



class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name


class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture



def load(filename):
    pass