-- A table that stores a person: could be either a composer or an editor.
create table person ( id integer primary key not null,
                      born integer,
                      died integer,
                      name varchar not null );

-- Stores info about a single score. Since some of the scores in the library
-- have multiple compositions in them, author data is stored in a separate
-- table (score_author). The relationship between authors and scores is M:N
-- since most composers have more than one composition to their name. Year in
-- this table refers to the field 'Composition Year' in the text file.
create table score ( id integer primary key not null,
                     name varchar,
                     genre varchar,
                     key varchar,
                     incipit varchar,
                     year integer );

-- Information about the voices in a particular score. Scores often contain
-- multiple voices, hence a separate table. The relationship is 1:N (each row
-- in the voice table belongs to exactly one score). The 'number' column
-- refers to the voice number, i.e. it's 1 for a line starting 'Voice 1:'.
create table voice ( id integer primary key not null,
                     number integer not null, -- which voice this is
                     score integer references score( id ) not null,
                     range varchar,
                     name varchar );

-- Multiple editions of a given score may exist, and any given edition could
-- have multiple editors. Like with score -- author relationship, this is M:N
-- and stored in an auxiliary table, edition_author.
create table edition ( id integer primary key not null,
                       score integer references score( id ) not null,
                       name varchar,
                       year integer );

-- Auxiliary table. See 'score'.
create table score_author( id integer primary key not null,
                           score integer references score( id ) not null,
                           composer integer references person( id ) not null );

-- Auxiliary table. See 'edition'.
create table edition_author( id integer primary key not null,
                             edition integer references edition( id ) not null,
                             editor integer references person( id ) not null );

-- Information about a printed score. This is always of a particular edition,
-- so we refer to that. The partiture column describes whether a partiture is
-- part of the print. In all the above tables, 'id' is an auto-generated
-- primary key. For print, however, this is the value of the 'Print Number'
-- field from the text file.
create table print ( id integer primary key not null,
                     partiture char(1) default 'N' not null, -- N = No, Y = Yes, P = Partial
                     edition integer references edition( id ) );

