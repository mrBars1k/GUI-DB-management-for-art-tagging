import psycopg2
from psycopg2 import sql
from token import *

adb = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
cur = adb.cursor()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## ## ТАБЛИЦА ТЕГОВ;
cur.execute("""CREATE TABLE IF NOT EXISTS main_tags (
    id bigserial PRIMARY KEY,
    ru varchar(150) NOT NULL UNIQUE,
    eng varchar(150) NOT NULL UNIQUE,
    alias1 varchar(150) UNIQUE,
    alias2 varchar(150) UNIQUE,
    alias3 varchar(150) UNIQUE,
    alias4 varchar(150) UNIQUE,
    type varchar(75) NOT NULL CHECK (type IN ('author', 'object', 'character', 'copyright', 'description', 'other', 'unknown')),
    date timestamp DEFAULT CURRENT_TIMESTAMP(1) NOT NULL
);""")
adb.commit()

## ## ТАБЛИЦА ИЗОБРАЖЕНИЙ АРТОВ;
cur.execute("""CREATE TABLE IF NOT EXISTS arts (
    id bigserial PRIMARY KEY,
    artist varchar(150) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    FOREIGN KEY (artist) REFERENCES main_tags (ru) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT unique_artist_url UNIQUE (artist, url)
);""")
adb.commit()

## ## ТАБЛИЦА СВЯЗИ АРТОВ И ТЕГОВ;
cur.execute("""CREATE TABLE IF NOT EXISTS tag_to_art (
    tag varchar,
    art integer,
    FOREIGN KEY (tag) REFERENCES main_tags (ru) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (art) REFERENCES arts (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT unique_tag_art_pair UNIQUE (tag, art)
);""")
adb.commit()

## ## ТАБЛИЦА ССЫЛОК НА АВТОРОВ (МОЖЕТ БЫТЬ НА ПРИМЕР ПРАВИЛЬНОГО ТЕГА);
cur.execute("""CREATE TABLE IF NOT EXISTS author_links (
    artist varchar(150),
    link text NOT NULL UNIQUE,
    type_source varchar(120) NOT NULL,
    FOREIGN KEY (artist) REFERENCES main_tags (ru) ON DELETE CASCADE ON UPDATE CASCADE
);""")
adb.commit()

## ## ТАБЛИЦА ОПИСАНИЯ ТЕГОВ;
cur.execute("""CREATE TABLE IF NOT EXISTS descriptions (
    id integer,
    text text NOT NULL UNIQUE,
    language varchar(20) NOT NULL CHECK (language IN ('RU', 'EN', 'UA')),
    FOREIGN KEY (id) REFERENCES main_tags (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT unique_id_language_pair UNIQUE (id, language)
);""")
adb.commit()

## ## ТАБЛИЦА СВЯЗИ РОДИТЕЛЬНЫХ ТЕГОВ;
cur.execute("""CREATE TABLE IF NOT EXISTS parents_children (
    mother integer,
    child integer,
    FOREIGN KEY (mother) REFERENCES main_tags (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (child) REFERENCES main_tags (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT unique_tag_relationship UNIQUE (mother, child)
);""")
adb.commit()

cur.close()
adb.close()