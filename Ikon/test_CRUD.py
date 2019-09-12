import unittest
import sqlite3
from CRUD import *


def initDatabase():
    from sqlite3 import Error
    try:
        connection = sqlite3.connect("test.db")
    except Error as err:
        print(err)

    """
    Drop database
    """
    connection.execute("DROP TABLE IF EXISTS exhibitions");
    connection.execute("DROP TABLE IF EXISTS artists");
    connection.execute("DROP TABLE IF EXISTS galleries");
    connection.execute("DROP TABLE IF EXISTS artists_exhibitions")

    """
    Create tables
    """
    sql_create_exhibitions_table = """CREATE TABLE IF NOT EXISTS exhibitions (
        id integer PRIMARY KEY,
        title text NOT NULL,
        gallery_id integer,
        date text,
        html text
    );"""

    sql_create_artists_table = """CREATE TABLE IF NOT EXISTS artists (
        id integer PRIMARY KEY,
        name text NOT NULL
    );"""

    sql_create_galleries_table = """CREATE TABLE IF NOT EXISTS galleries (
        id integer PRIMARY KEY,
        name text NOT NULL
    );"""

    sql_create_artists_exhibition_table = """CREATE TABLE IF NOT EXISTS artists_exhibitions(
        artist_id integer NOT NULL,
        exhibition_id integer NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES artists (id), 
        FOREIGN KEY (exhibition_id) REFERENCES exhibitions(id)
    );"""

    connection.execute(sql_create_exhibitions_table);
    connection.execute(sql_create_artists_table);
    connection.execute(sql_create_galleries_table);
    connection.execute(sql_create_artists_exhibition_table);

    return connection


class TestCRUD(unittest.TestCase):
    def test_select_artist(self):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO artists (name) VALUES (?);", ("andris", ))
        andris_id = cursor.lastrowid

        artist = select_artist_where_id_is(connection, andris_id)
        self.assertEqual(artist, (andris_id, "andris"))

    def test_insert_artist(self):
        cursor = connection.cursor()
        ID = insert_artist(connection, "Judit")

        self.assertIsInstance(ID, int)
        self.assertEqual(select_artist_where_id_is(connection, ID)[1], "Judit")

    def test_delete_artist(self):
        connection.execute("INSERT INTO artists (name) VALUES (?);", ("peti", ))
        row = connection.execute("SELECT id, name FROM artists WHERE name = 'peti';").fetchone()

        delete_artist_where_id_is(connection, row[0])
        row = connection.execute("SELECT name FROM artists WHERE name = 'peti';").fetchone()
        self.assertEqual(row, None)


    def test_select_gallery(self):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO galleries (name) VALUES (?);", ("FKSE", ))
        ID = cursor.lastrowid

        artist = select_gallery_where_id_is(connection, ID)
        self.assertEqual(artist, (ID, "FKSE"))

    def test_insert_gallery(self):
        cursor = connection.cursor()
        ID = insert_gallery(connection, "FKSE")

        self.assertIsInstance(ID, int)
        self.assertEqual(select_gallery_where_id_is(connection, ID)[1], "FKSE")

    def test_delete_gallery(self):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO galleries (name) VALUES (?);", ("Liget", ))
        ID = cursor.lastrowid

        delete_gallery_where_id_is(connection, ID)
        row = connection.execute("SELECT name FROM galleries WHERE name = 'Liget';").fetchone()
        self.assertEqual(row, None)

if __name__ == '__main__':
    connection = initDatabase()
    unittest.main()