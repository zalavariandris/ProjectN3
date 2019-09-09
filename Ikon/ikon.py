import scrape
if __name__ == "__main__":
    """
    Read data from files
    """
    filepaths = list(scrape.get_filepaths_on_disk("C:/Users/andris/IkOn/IkOn_HTML"))[:50]
    pages = list(scrape.read_files_from_disk(filepaths))
    data = scrape.parse_html_pages(pages)

    """
    Drop current database!
    """
    print("drop current db");
    import sqlite3
    from sqlite3 import Error
    try:
        connection = sqlite3.connect("../ikon.db")
    except Error as err:
        print(err)

    connection.execute("DROP TABLE IF EXISTS exhibitions");
    connection.execute("DROP TABLE IF EXISTS artists");
    connection.execute("DROP TABLE IF EXISTS galleries");
    connection.execute("DROP TABLE IF EXISTS artists_exhibitions")
    connection.execute("DROP TABLE IF EXISTS exhibitions_at_galleries")


    """
    Create database
    """ 
    print("Connect to database...")

    sql_create_exhibitions_table = """CREATE TABLE IF NOT EXISTS exhibitions (
        id integer PRIMARY KEY,
        title text NOT NULL,
        date text
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

    sql_create_exhibitions_at_galleries_table = """CREATE TABLE IF NOT EXISTS exhibitions_at_galleries(
        exhibition_id integer NOT NULL,
        gallery_id integer NOT NULL,
        FOREIGN KEY (exhibition_id) REFERENCES exhibitions (id), 
        FOREIGN KEY (gallery_id) REFERENCES galleries (id)
    );"""

    try:
        connection.cursor().execute(sql_create_exhibitions_table);
        connection.cursor().execute(sql_create_artists_table);
        connection.cursor().execute(sql_create_galleries_table);
        connection.cursor().execute(sql_create_artists_exhibition_table);
        connection.cursor().execute(sql_create_exhibitions_at_galleries_table);
    except Error as err:
        print(err)

    """
    fill tables with data
    """
    print("Filling tables with data...")
    sql_create_exhibition = '''
        INSERT INTO exhibitions(title, date)
        VALUES(?,?);'''

    sql_create_artist = '''
        INSERT INTO artists(name)
        VALUES(?);'''

    sql_create_artist_if_unique = '''
        INSERT INTO artists (name)                                                                                                                                                                          
        SELECT ?                                                                                                                                                                                     
        EXCEPT                                                                                                                                                                                              
        SELECT name FROM artists WHERE name LIKE ?; 
       '''

    sql_create_gallery = '''
        INSERT INTO galleries(name)
        VALUES(?);'''

    sql_create_gallery_if_unique = '''
        INSERT INTO galleries (name)                                                                                                                                                                          
        SELECT ?                                                                                                                                                                                     
        EXCEPT                                                                                                                                                                                              
        SELECT name FROM galleries WHERE name LIKE ?; 
       '''

    sql_link_artist_to_exhibition = '''
        INSERT INTO artists_exhibitions (artist_id, exhibition_id)
        VALUES(?,?);'''

    sql_link_gallery_to_exhibition = '''
        INSERT INTO exhibitions_at_galleries (gallery_id, exhibition_id)
        VALUES(?,?);'''

    cursor = connection.cursor()                      
    try:
        for i in range(len(data)):
            try:
                row = data[i]
                cursor.execute(sql_create_exhibition, (row['title'], row['date']))
                exhibition_id = cursor.lastrowid
                for artist_name in row['artists']:
                    # cursor.execute(sql_create_artist, (artist_name, ) ) # insert anyway
                    cursor.execute(sql_create_artist_if_unique, (artist_name, artist_name)) # insert only when its new
                    artist_id = cursor.lastrowid
                    cursor.execute(sql_link_artist_to_exhibition, (artist_id, exhibition_id) )
                gallery_name = row['gallery']
                cursor.execute(sql_create_gallery_if_unique, (gallery_name, gallery_name))
                gallery_id = cursor.lastrowid
                cursor.execute(sql_link_gallery_to_exhibition, (gallery_id, exhibition_id))
            except Error as e:
                print("ERROR:", e)
    except Error as err:
        print("ERROR: ", err)


    # TODO: DEBUG
    cursor = connection.cursor();
    cursor.execute("INSERT INTO artists(name) VALUES(?);", ("andris", ))
    print("andris_id:", cursor.lastrowid);
    connection.commit()

    """
    TEST DATABASE
    """
    exhibitions_count = connection.cursor().execute("""SELECT COUNT(*) FROM exhibitions;""").fetchone()[0]
    artists_count = connection.cursor().execute("""SELECT COUNT(*) FROM artists;""").fetchone()[0]
    galleries_count = connection.cursor().execute("""SELECT COUNT(*) FROM galleries;""").fetchone()[0]
    artists_exhibitions_count = connection.cursor().execute("""SELECT COUNT(*) FROM artists_exhibitions;""").fetchone()[0]
    exhibitions_at_galleries_count = connection.cursor().execute("""SELECT COUNT(*) FROM exhibitions_at_galleries;""").fetchone()[0]
    print("== Summary ==")
    print("exhibitions_ count:", exhibitions_count)
    print("artists count:", artists_count)
    print("galleries count:", galleries_count)
    print("artists_exhibition link count:", artists_exhibitions_count)
    print("exhibitions_at_galleries count", exhibitions_at_galleries_count)

    sql_select_duplicate_artists = """
        SELECT id, name,
           count(*) AS c
        FROM artists
        GROUP BY name
        HAVING c > 1
        ORDER BY c DESC
        """
    cursor.execute(sql_select_duplicate_artists);
    duplicated_artists = cursor.fetchall()
    assert len(duplicated_artists)==0, "Oh no! There are artists with the same name"

    """
    SELECT * FROM artists ORDER BY LOWER(name)
    SELECT id FROM artists WHERE name LIKE 'Tomay Katalin'; // is equal
    SELECT id, name FROM artists WHERE name LIKE 'Tomay Kat%'; / starts with
    """