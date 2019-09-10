if __name__ == "__main__":
    """
    CONNECT to db
    """
    print("Connect to database...")
    
    import sqlite3
    from sqlite3 import Error
    try:
        connection = sqlite3.connect("../ikon.db")
    except Error as err:
        print(err)
    """
    TEST DATABASE
    """
    exhibitions_count = connection.cursor().execute("""SELECT COUNT(*) FROM exhibitions;""").fetchone()[0]
    artists_count = connection.cursor().execute("""SELECT COUNT(*) FROM artists;""").fetchone()[0]
    galleries_count = connection.cursor().execute("""SELECT COUNT(*) FROM galleries;""").fetchone()[0]
    artists_exhibitions_count = connection.cursor().execute("""SELECT COUNT(*) FROM artists_exhibitions;""").fetchone()[0]
    print("== Summary ==")
    print("exhibitions_ count:", exhibitions_count)
    print("artists count:", artists_count)
    print("galleries count:", galleries_count)
    print("artists_exhibition link count:", artists_exhibitions_count)

    """
    Reconstruct exhibtions from database
    """
    sql_select_artists_of_exhibtion='''
    SELECT ae.artist_id FROM artists_exhibitions ae INNER JOIN exhibitions e ON e.id == ae.exhibition_id WHERE e.id=?;
    '''

    exhibitions = connection.execute("SELECT id, title, gallery_id, date FROM exhibitions").fetchall()
    for exhibition in exhibitions:
        exhibition_id, title, gallery_id, exhibition_date = exhibition
        gallery_name = connection.execute("SELECT id, name FROM galleries WHERE id=?", (gallery_id, ) ).fetchone()

        artists_id = [row[0] for row in connection.execute(sql_select_artists_of_exhibtion, (exhibition_id, )).fetchall()]
        sql_select_artists_with_ids  ="SELECT id, name FROM artists WHERE id IN ("+",".join(["?"]*len(artists_id))+");"
        artist_names =[row[1] for row in connection.execute(sql_select_artists_with_ids, artists_id).fetchall()]

        exhibition = {
            'id': exhibition_id,
            'title': title,
            'gallery': gallery_name,
            'artists': artist_names,
            'date': exhibition_date
        }
        print(exhibition)


    """
    SELECT * FROM artists ORDER BY LOWER(name)
    SELECT id FROM artists WHERE name LIKE 'Tomay Katalin'; // is equal
    SELECT id, name FROM artists WHERE name LIKE 'Tomay Kat%'; / starts with

    SELECT e.id, e.title, e.date, g.name FROM galleries g INNER JOIN exhibitions e ON g.id == e.gallery_id;
    SELECT g.id FROM galleries g INNER JOIN exhibitions e ON g.id == e.gallery_id WHERE e.id=2;
    """

    sql_select_entities_with_filter = '''
    SELECT a.id, a.name, e.id, e.title, e.date, g.id, g.name
    FROM artists_exhibitions ae
    INNER JOIN galleries g ON g.id = e.gallery_id
    INNER JOIN exhibitions e ON e.id = ae.exhibition_id
    INNER JOIN artists a ON a.id = ae.artist_id
    WHERE a.name LIKE 'and%' AND e.title LIKE 'Think%';
    '''



