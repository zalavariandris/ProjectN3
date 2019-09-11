
import sqlite3
from sqlite3 import Error
try:
    connection = sqlite3.connect("../ikon.db")
except Error as err:
    print(err)

import re
def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0

connection.create_function('regexp', 2, regexp)

from utilities.profiler import profile

sql_select_exhibitions ='''
    SELECT id, title
    FROM exhibitions
    WHERE id = {ID};
    '''

def select_artists_like(text):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name LIKE '{text}';
    '''.replace('{text}', text)

    result = connection.execute(sql);
    for artist in result:
        yield artist

def select_artists_with_name(name):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name = '{name}';
    '''.replace('{name}', name)

    result = connection.execute(sql);
    for artist in result:
        yield artist
        
def select_exhibition_with_id(ID):
    sql = '''
    SELECT id, title
    FROM exhibitions
    WHERE id = {ID};
    '''.replace("{ID}", str(ID))

    result = connection.execute(sql)
    return result.fetchone()

def select_exhibitions_of_artist(artist_id):
    sql = '''
    SELECT e.id, e.title
    FROM artists_exhibitions ae
    INNER JOIN exhibitions e ON e.id = ae.exhibition_id
    WHERE ae.artist_id = {artist_id}
    '''.replace("{artist_id}", str(artist_id))

    for exhibition in connection.execute(sql):
        yield exhibition

sql_link_artist_to_exhibition = '''
INSERT INTO artists_exhibitions (artist_id, exhibition_id)
VALUES(?,?);'''

sql_unlink_artist_to_exhibition = '''
DELETE FROM artists_exhibitions
WHERE artist_id = ? AND exhibition_id = ?;'''

sql_create_artist = '''
INSERT INTO artists (name)
VALUES(?);'''

sql_delete_artist = '''
DELETE FROM artists
WHERE id = ?
'''

@profile
def select_artists_with_exhibition_count():
    sql = '''
    SELECT a.name, COUNT(*)
    FROM artists_exhibitions ae
    INNER JOIN artists a ON a.id = ae.artist_id
    GROUP BY artist_id
    ORDER BY COUNT(*) DESC;
    '''

    result = connection.execute(sql).fetchall()
    print(len(result))
    for item in result:
        print(item)

@profile
def delete_rows_starts_with_non_letters():
    # Törölj mindent, ami nem betüvel kezdődik
    sql = "SELECT name FROM artists WHERE name NOT REGEXP '^[A-Ș]' ORDER BY name ASC;"
    result = connection.execute(sql).fetchall()
    print(len(result))
    for item in result:
        print(item[0])

    sql = "DELETE FROM artists WHERE name NOT REGEXP '^[A-Ș]';"
    connection.execute(sql)

@profile
def delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA():
    print("delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA")
    sql = "SELECT name FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera' ORDER BY name ASC;"
    result = connection.execute(sql).fetchall()
    print(len(result))
    for item in result:
        print(item[0])

    sql = "DELETE FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera';"
    connection.execute(sql)

@profile
def remove_parenthesis_from_names():
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name LIKE '%(%)%'
    '''
    result = connection.execute(sql).fetchall()
    
    sql_update_artist_name =  '''
    UPDATE artists
    SET name = '{val}'
    WHERE id={ID};
    '''

    for row in result:
        ID = row[0]
        name = row[1]
        clean_name = re.sub(r" ?\([^)]+\)", "", name)
        print(name, " -> ", clean_name)
        connection.execute(sql_update_artist_name.replace('{val}', clean_name).replace("{ID}", str(ID)))

@profile
def split_artist_entries_with_multiple_artist_names():
    def split_names(text, delimiter):
        return [_.strip() for _ in filter(None, text.split(delimiter))]

    def insert_artist_if_unique(name):
        row = connection.execute("SELECT id FROM artists WHERE name=?;", (name, )).fetchone()
        if row==None:
            cursor = connection.cursor()
            cursor.execute(sql_create_artist, (artist_name, ) )
            artist_id = cursor.lastrowid
        else:
            artist_id = row[0]
        return artist_id, name

    for delimiter in ["|","*","•"]:
        for artist_list_id, artist_list_text in select_artists_like("%{delimiter}%_{delimiter}%".replace("{delimiter}", delimiter)):
            # find exhibitions of the current text of artist names
            exhibitions = list(select_exhibitions_of_artist(artist_list_id))
            exhibition_ids = [_[0] for _ in exhibitions]
            
            # extact artist names from text
            artists_names = split_names(artist_list_text, delimiter) 

            # create artists from names extracted from text, if not exists
            for artist_name in artists_names:
                artist = insert_artist_if_unique(artist_name)

                # link exhibitions to artists
                for exhibition_id in exhibition_ids:
                    connection.execute(sql_link_artist_to_exhibition, (artist[0], exhibition_id) )

            # clear artist lists from tables
            for exhibition_id in exhibition_ids:
                connection.execute(sql_unlink_artist_to_exhibition, (artist_list_id, exhibition_id) )
            connection.execute(sql_delete_artist, (artist_list_id,))

def find_variants():
    sql = '''
    SELECT name
    FROM artists;
    '''
    all_names = connection.execute(sql).fetchall()
    namevariants = dict()
    for row in all_names:
        ref_name = row[0]
        namevariants[ref_name] = []

    for ref_name, variants in namevariants.items():
        for n in namevariants.keys():
            if(ref_name in n and ref_name !=n):
                variants.append(n)

    cleaned_namevariants = []
    for ref_name, variants in namevariants.items():
        if len(variants) > 0:
            cleaned_namevariants.append(sorted(variants+[ref_name], key=len))

    for variants in cleaned_namevariants:
        yield variants

if __name__ == "__main__":
    remove_parenthesis_from_names()
    delete_rows_starts_with_non_letters()
    split_artist_entries_with_multiple_artist_names()
    delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA()
    connection.commit()

    # clean
    művész, író, költő, képzőnűvész, művészeti író, ***díjas építést

    for variants in find_variants():
        if len(variants[0].split(" "))==1:
            artist = list(select_artists_with_name(variants[0]))[0]
            exhibition = list(select_exhibitions_of_artist(artist[0]))[0]
            print(variants[0], "    (  ",exhibition[1], " )")
            print(variants[1:])
            print()

