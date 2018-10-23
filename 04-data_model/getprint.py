import json
import sqlite3
import sys


GET_PRINT_COMPOSERS_SQL = """
SELECT person.name, person.born, person.died FROM print 
LEFT JOIN edition ON print.edition = edition.id
LEFT JOIN score ON edition.score = score.id
LEFT JOIN score_author ON score.id = score_author.score
LEFT JOIN person ON score_author.composer = person.id
WHERE print.id = ?;
"""


def db_connect(db):
    con = sqlite3.connect(db)
    return con


def get_print(db, print_id):
    con = db_connect(db)
    cur = con.cursor()
    cur.execute(GET_PRINT_COMPOSERS_SQL, (print_id,))
    composers_list = []
    for composer in cur.fetchall():
        composers_list.append({
            "name": composer[0],
            "born": composer[1],
            "died": composer[2]
        })

    json.dump(composers_list, sys.stdout, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("First argument should be print id!")

    db_path = "scorelib.dat"
    print_id = sys.argv[1]

    get_print(db_path, print_id)
