from CRUD import *

def init_database(filename="./data/ikon.db"):
    """
    Drop current database!
    """
    print("Initalize Database...")
    
    print("connect...")
    import sqlite3
    from sqlite3 import Error
    try:
        connection = sqlite3.connect(filename)
    except Error as err:
        print(err)

    print("drop tables...");
    connection.execute("DROP TABLE IF EXISTS exhibitions");
    connection.execute("DROP TABLE IF EXISTS artists");
    connection.execute("DROP TABLE IF EXISTS galleries");
    connection.execute("DROP TABLE IF EXISTS artists_exhibitions")

    """
    Create tables
    """
    print("create tables...");
    sql_create_exhibitions_table = """CREATE TABLE IF NOT EXISTS exhibitions (
        id integer PRIMARY KEY,
        title text NOT NULL,
        gallery_id integer,
        date text,
        html text
    );"""

    sql_create_artists_table = """CREATE TABLE IF NOT EXISTS artists (
        id integer PRIMARY KEY,
        name text NOT NULL,
        suspicious text
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

def fill_database(connection, data):
    # fill table from data
    print("Filling tables with data...")
    for i in range(len(data)):
        row = data[i]
        # insert gallery
        gallery_name = row['gallery']
        
        gallery = select_gallery_where_name_is(connection, gallery_name)
        if gallery == None:
            gallery_id = insert_gallery(connection, gallery_name)
        else:
            gallery_id = gallery[0]

        # insert exhibition
        exhibition_id = insert_exhibition(connection, row['title'], row['date'], gallery_id, row['html'])

        # insert artists
        for artist_name in row['artists']:
            artist = select_artist_where_name_is(connection, artist_name)
            if artist==None:
                artist_id = insert_artist(connection, artist_name)
            else:
                artist_id = artist[0]
            link_artist_to_exhibition(connection, (artist_id, ), (exhibition_id, ) )

    connection.commit()

if __name__ == "__main__":    
    """
    parse html files
    """
    import parse_ikon
    data = parse_ikon.main()


    """
    Fill tables with data
    """
    connection = init_database(filename="./data/ikon.db")
    fill_database(connection, data)
