import scrape
if __name__ == "__main__":
    """
    Drop current database!
    """
    print("Connect to database...")
    
    import sqlite3
    from sqlite3 import Error
    try:
        connection = sqlite3.connect("../ikon.db")
    except Error as err:
        print(err)

    print("drop current db");
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


    try:
        connection.cursor().execute(sql_create_exhibitions_table);
        connection.cursor().execute(sql_create_artists_table);
        connection.cursor().execute(sql_create_galleries_table);
        connection.cursor().execute(sql_create_artists_exhibition_table);
    except Error as err:
        print(err)

    """
    Fill tables with data
    """
    # read data from htlm files
    # filepaths = list(scrape.get_filepaths_on_disk("C:/Users/andris/IkOn/IkOn_HTML"))[:50]
    # pages = list(scrape.read_files_from_disk(filepaths))
    # data = scrape.parse_html_pages(pages)

    data = [
        {'title': "Thinking some more...",  'gallery': "Obudai Tarsaskor Galeria",  'artists': ["andris", "judit", "masa"],  'date': "2018"},
        {'title': "FKSE szalon",            'gallery': "MKE",                       'artists': ["andris", "masa"],            'date': "2019"}
    ]
    
    # fill table from data
    print("Filling tables with data...")
    sql_create_exhibition = '''
        INSERT INTO exhibitions(title, date, gallery_id)
        VALUES(?,?,?);'''

    sql_create_artist = '''
        INSERT INTO artists (name)
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

    sql_link_artist_to_exhibition = '''
        INSERT INTO artists_exhibitions (artist_id, exhibition_id)
        VALUES(?,?);'''

    sql_set_gallery_for_exhibiton = '''
        UPDATE exhibitions
        SET gallery_id = ?
        WHERE exhibition_id = ?;
        '''

    cursor = connection.cursor()                      
    try:
        for i in range(len(data)):
            try:
                row = data[i]
                # insert gallery
                gallery_name = row['gallery']
                gallery_id = artist_id = connection.execute("SELECT id FROM galleries WHERE name=?;", (gallery_name, )).fetchone()
                if gallery_id == None:
                    cursor.execute(sql_create_gallery, (gallery_name,))
                    gallery_id = cursor.lastrowid
                else:
                    gallery_id = gallery_id[0]

                # insert exhibition
                cursor.execute(sql_create_exhibition, (row['title'], row['date'], gallery_id))
                exhibition_id = cursor.lastrowid

                # insert artists
                for artist_name in row['artists']:
                    artist_id = connection.execute("SELECT id FROM artists WHERE name=?;", (artist_name, )).fetchone()
                    if artist_id==None:
                        cursor.execute(sql_create_artist, (artist_name, ) ) # insert anyway
                        artist_id = cursor.lastrowid
                    else:
                        artist_id = artist_id[0]
                    cursor.execute(sql_link_artist_to_exhibition, (artist_id, exhibition_id) )

            except Error as e:
                print("ERROR:", e)
    except Error as err:
        print("ERROR: ", err)

    connection.commit()

    for row in data:
        print(row)
