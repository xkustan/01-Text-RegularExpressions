"""SQL queries."""

CREATE_EMPTY_DB = [
    """create table person ( id integer primary key not null,
                      born integer,
                      died integer,
                      name varchar not null);""",
    """create table score ( id integer primary key not null,
                     name varchar,
                     genre varchar,
                     key varchar,
                     incipit varchar,
                     year integer);""",
    """create table voice ( id integer primary key not null,
                     number integer not null,
                     score integer references score( id ) not null,
                     range varchar,
                     name varchar );""",
    """create table edition ( id integer primary key not null,
                       score integer references score( id ) not null,
                       name varchar,
                       year integer );""",
    """create table score_author( id integer primary key not null,
                           score integer references score( id ) not null,
                           composer integer references person( id ) not null );""",
    """create table edition_author( id integer primary key not null,
                             edition integer references edition( id ) not null,
                             editor integer references person( id ) not null );""",
    """create table print ( id integer primary key not null,
                     partiture char(1) default 'N' not null,
                     edition integer references edition( id ) );"""
]


DEFINED_CONSTRAINTS = [
    """CREATE UNIQUE INDEX person_name_unique_index ON person(name);""",
    """CREATE UNIQUE INDEX score_author_unique_index ON score_author(score, composer);""",
    """CREATE UNIQUE INDEX voice_unique_index ON voice(number, score, ifnull(range, ''), ifnull(name, ''));""",
    """CREATE UNIQUE INDEX print_unique_index ON print(id);""",
]
