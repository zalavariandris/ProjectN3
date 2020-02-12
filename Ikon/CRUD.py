"""
CONNECT
"""
def connectToDatabase(filepath)->'sqlite3.Connection':
    import sqlite3
    from sqlite3 import Error

    connection = sqlite3.connect(filepath)


    import re
    def regexp(y, x, search=re.search):
        return 1 if search(y, x) else 0

    connection.create_function('regexp', 2, regexp)

    return connection

"""
INSERT SELECT UPDATE DELETE
"""
# INSERT
def insert_exhibition(connection, title, _date, gallery_id, html):
    sql = '''
    INSERT INTO exhibitions(title, date, gallery_id, html)
    VALUES (?,?,?,?);'''

    cursor = connection.cursor()
    cursor.execute(sql, (title, _date, gallery_id, html))
    return cursor.lastrowid

def insert_gallery(connection, name):
    sql = '''
    INSERT INTO galleries(name)
    VALUES (?);
    '''
    cursor = connection.cursor()
    cursor.execute(sql, (name,))
    return cursor.lastrowid

def insert_artist(connection, name):
    sql = '''
    INSERT INTO artists (name)
    VALUES (?);
    '''

    cursor = connection.cursor()
    cursor.execute(sql, (name,))
    return cursor.lastrowid

# SELECT
def select_exhibitions(connection):
    sql = '''
    SELECT id, title, date, html
    FROM exhibitions
    ORDER BY title ASC;
    '''

    return connection.execute(sql).fetchall()

def select_exhibition_where_id_is(connection, ID):
    sql = '''
    SELECT id, title, date, gallery_id, html
    FROM exhibitions
    WHERE id = ?;
    '''

    return connection.execute(sql, (ID, )).fetchone()

def select_exhibitions_where_title_like(connection, text):
    sql = '''
    SELECT id, title
    FROM exhibitions
    WHERE title LIKE '{text}';
    '''.replace('{text}', text)

    table = connection.execute(sql);
    for row in table:
        yield row

def select_gallery_of_exhibition(connection, exhibition):
    sql = '''
    SELECT g.id, g.name
    FROM exhibitions e
    JOIN galleries g ON g.id = e.gallery_id
    WHERE e.id = ?;
    '''

    return connection.execute(sql, (exhibition[0], )).fetchone()

def select_exhibitions_at_gallery(connection, gallery):
    sql = '''
    SELECT g.id, g.name
    FROM exhibitions e
    JOIN galleries g ON g.id = e.gallery_id
    WHERE e.gallery_id IS ?;
    '''
    return connection.execute(sql, (gallery[0], )).fetchall()

def select_artists(connection):
    sql = '''
    SELECT id, name
    FROM artists
    ORDER BY name ASC
    '''

    return connection.execute(sql).fetchall()

def select_artists_with_exhibitions_count(connection, count):
    sql = '''
    SELECT a.id, a.name, COUNT(ae.artist_id) as No_exhibitions
    FROM artists_exhibitions ae
    JOIN artists a ON a.id = ae.artist_id
    GROUP BY ae.artist_id
    HAVING No_exhibitions >= ?
    ORDER BY No_exhibitions DESC;
    '''

    return connection.execute(sql, (count, ) ).fetchall()

def select_exhibitions_where_artist_is(connection, artist):
    sql = '''
    SELECT e.id, e.title
    FROM artists_exhibitions ae
    INNER JOIN exhibitions e ON e.id = ae.exhibition_id
    WHERE ae.artist_id = {artist_id}
    '''.replace("{artist_id}", str(artist[0]))

    return connection.execute(sql).fetchall()

def select_artist_where_id_is(connection, ID):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE id = ?;
    '''

    return connection.execute(sql, (ID, )).fetchone();

def select_artist_where_name_is(connection, name):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name = ?;
    '''

    return connection.execute(sql, (name,)).fetchone();

def select_artists_where_name_like(connection, text):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name LIKE '{text}';
    '''.replace('{text}', text)

    for a in connection.execute(sql):
        yield a

def select_artists_where_name_in(connection, names):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name IN ({});
    '''

    placeholders = ",".join(["?"]*len(names))
    sql = sql.replace("{}", placeholders)

    return connection.execute(sql, names).fetchall()

def select_galleries(connection):
    sql = '''
    SELECT id, name
    FROM galleries
    ORDER BY name ASC
    '''

    return connection.execute(sql).fetchall()

def select_gallery_where_id_is(connection, ID):
    sql = '''
    SELECT id, name
    FROM galleries
    WHERE id = ?;
    '''

    return connection.execute(sql, (ID, )).fetchone();

def select_gallery_where_name_is(connection, name):
    sql = '''
    SELECT id, name
    FROM galleries
    WHERE name = ?;
    '''

    return connection.execute(sql, (name,)).fetchone();

def select_gallery_where_name_like(connection, text):
    sql = '''
    SELECT id, name
    FROM galleries
    WHERE name LIKE '{text}';
    '''.replace('{text}', text)

    return connection.execute(sql).fetchall();


# UPDATE 

def update_artist_where_id_is(connection, ID, name):
    sql =  '''
    UPDATE artists
    SET name = '{val}'
    WHERE id={ID};
    '''
    sql = sql.replace('{val}', name).replace("{ID}", str(ID))
    connection.execute(sql)


# DELETE

def delete_exhibition_where_id_is(connection, ID):
    sql = '''
    DELETE FROM exhibitions
    WHERE id = ?;
    '''
    connection.execute(sql, (ID,))

def delete_gallery_where_id_is(connection, ID):
    sql = '''
    DELETE FROM galleries
    WHERE id = ?;
    '''
    connection.execute(sql, (ID,))

def delete_artist_where_id_is(connection, ID):
    sql = '''
    DELETE FROM artists
    WHERE id = ?;
    '''
    connection.execute(sql, (ID,))

def delete_artists_where_id_in(connection, ids):
    sql = '''
    DELETE FROM artists
    WHERE id IN ({});
    '''.format( ",".join(["?"]*len(ids) ) )

    exhibitions = connection.execute(sql, ids)
   

"""
Relationships
"""
def link_artist_to_exhibition(connection, artist, exhibition):
    sql = '''
    INSERT INTO artists_exhibitions (artist_id, exhibition_id)
    VALUES(?,?);'''
    connection.execute(sql, (artist[0], exhibition[0]) )

def unlink_artist_from_exhibition(connection, artist, exhibition):
    sql = '''
    DELETE FROM artists_exhibitions
    WHERE artist_id = ? AND exhibition_id = ?;'''
    connection.execute(sql, (artist[0], exhibition[0]) )

def select_exhibitions_of_artist(connection, artist):
    sql='''
    SELECT e.id, e.title, e.date
    FROM artists_exhibitions ae 
    INNER JOIN exhibitions e ON e.id == ae.exhibition_id 
    WHERE ae.artist_id=?;
    '''
    return connection.execute(sql, (artist[0], )).fetchall()

def select_artists_of_exhibition(connection, exhibition):
    sql='''
    SELECT a.id,a.name
    FROM artists_exhibitions ae 
    INNER JOIN exhibitions e ON e.id == ae.exhibition_id 
    INNER JOIN artists a ON a.id == ae.artist_id
    WHERE e.id=?;
    '''

    return connection.execute(sql, (exhibition[0],)).fetchall()

# Complex modifications
def merge_artists(connection, artists):
    return artist

