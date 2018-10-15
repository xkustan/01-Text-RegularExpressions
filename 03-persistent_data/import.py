import sqlite3
import sys
from sqlite3 import Error
import scorelib
import sql_queries


def init_database(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        # create empty database
        for sql in sql_queries.CREATE_EMPTY_DB:
            cur.execute(sql)
            conn.commit()
        # add constrains
        for sql in sql_queries.DEFINED_CONSTRAINTS:
            cur.execute(sql)
            conn.commit()
        print("Database created successfully!")
    except Error as e:
        print(e)
    finally:
        conn.close()


def db_connect(db):
    con = sqlite3.connect(db)
    return con


def test_selects(db):
    tables = ["person", "score", "score_author", "edition", "edition_author", "voice", "print"]
    con = db_connect(db)
    cur = con.cursor()
    for table in tables:
        cur.execute("SELECT * FROM {0};".format(table))
        result = cur.fetchall()
        print(table, len(result), result[:5])


def process_print(db_conn, p):
    # store authors (person)
    composers_ids = []
    for composer in p.edition.composition.authors:
        composer_id = composer.insert_or_update_to_db(db_conn)
        composers_ids.append(composer_id)

    editors_ids = []
    for editor in p.edition.authors:
        editor_id = editor.insert_or_update_to_db(db_conn)
        editors_ids.append(editor_id)

    # score + score_author + voice
    score_id = p.edition.composition.insert_to_db(db_conn, composers_ids)

    # edition + edition_author
    edition_id = p.edition.insert_to_db(db_conn, score_id, editors_ids)

    # print
    p.save_to_db(db_conn, edition_id)


def fill_database_with_data(db, data_path):
    prints = scorelib.load(data_path)
    db_conn = db_connect(db)
    for p in prints:
        process_print(db_conn, p)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("First argument should be path to library file and second name of database!")

    filename = sys.argv[1]
    db_path = sys.argv[2]

    init_database(db_path)
    fill_database_with_data(db_path, filename)
    # test_selects(db_path)
