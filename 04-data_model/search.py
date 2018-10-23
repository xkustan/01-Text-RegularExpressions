from collections import defaultdict
import json
import sqlite3
import sys


GET_PRINT_ID_BY_COMPOSER_SQL = """
SELECT print.id FROM person 
INNER JOIN score_author ON person.id = score_author.composer
LEFT JOIN score ON score_author.score = score.id
LEFT JOIN edition ON score.id = edition.score
LEFT JOIN print ON edition.id = print.edition
WHERE INSTR(lower(person.name), lower(?)) > 0;
"""

GET_FULL_PRINT = """
SELECT
print.id as print_id,
composer.name as composer_name,
composer.born as composer_born,
composer.died as composer_died,
score.name as composition_name,
score.genre as composition_genre, -- 5
score.year as composition_year,
edition.name as edition_name,
edition.year as publication_year,
editor.name as editor_name,
editor.born as editor_born,  -- 10
editor.died as editor_died,
voice.number as voice_number,
voice.name as voice_name,
voice.range as voice_range,
score.key as composition_key,  --15
score.incipit as composition_incipit,
print.partiture as print_partiture
FROM print 
LEFT JOIN edition ON print.edition = edition.id
LEFT JOIN score ON edition.score = score.id
LEFT JOIN score_author ON score.id = score_author.score
LEFT JOIN person as composer ON score_author.composer = composer.id
LEFT JOIN edition_author ON edition.id = edition_author.edition
LEFT JOIN person as editor ON edition_author.editor = editor.id
LEFT JOIN voice ON score.id = voice.score
WHERE print.id = ?;
"""


def db_connect(db):
    con = sqlite3.connect(db)
    return con


def process_print(cur, print_id):
    cur.execute(GET_FULL_PRINT, (print_id,))
    p = None

    for row in cur.fetchall():
        if not p:
            p = {
                "Print Number": row[0],
                "Composer": set(),
                "Title": row[4],
                "Genre": row[5],
                "Composition Year": row[6],
                "Publication Year": row[8],
                "Edition": row[7],
                "Editor": set(),
                "Voices": {},
                "Partiture": row[17],
                "Key": row[15],
                "Incipit": row[16],
            }

        if row[1]:
            p["Composer"].add(frozenset({
                "name": row[1],
                "born": row[2],
                "died": row[3]
            }.items()))

        if row[9]:
            p["Editor"].add(frozenset({
                "name": row[9],
                "born": row[10],
                "died": row[11]
            }.items()))

        if row[12]:
            p["Voices"][row[12]] = {
                "name": row[13],
                "range": row[14]
            }

    p["Composer"] = [dict(x) for x in p["Composer"]]
    p["Editor"] = [dict(x) for x in p["Editor"]]

    return p


def search_composer(db, composer_substring):
    con = db_connect(db)
    cur = con.cursor()
    cur.execute(GET_PRINT_ID_BY_COMPOSER_SQL, (composer_substring,))
    all_print_ids = sorted([x[0] for x in cur.fetchall()])
    all_prints = defaultdict(list)

    for print_id in all_print_ids:
        full_print = process_print(cur, print_id)
        for comp in full_print["Composer"]:
            all_prints[comp["name"]].append(full_print)

    json.dump(all_prints, sys.stdout, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("First argument should be composer name/substring")

    db_path = "scorelib.dat"
    composer = sys.argv[1]

    try:
        search_composer(db_path, composer)
    except:
        sys.exit("Make sure you have valid sqlite database in this directory named scorelib.dat")
