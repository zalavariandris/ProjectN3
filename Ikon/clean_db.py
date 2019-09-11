
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


# delete_rows_starts_with_non_letters()
# delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA()

@profile
def select_artists_with_exhibition_count():
    sql = '''
    SELECT
        a.name,
        COUNT(*)
    FROM
        artists_exhibitions ae
    INNER JOIN
        artists a ON a.id = ae.artist_id
    GROUP BY
        artist_id
    ORDER BY COUNT(*) DESC;
    '''

    result = connection.execute(sql).fetchall()
    print(len(result))
    for item in result:
        print(item)

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


    # list(filter(None, s.split("•")))

def find_variants():
    sql = '''
    SELECT name
    FROM artists;
    '''
    result = connection.execute(sql).fetchall()
    namevariants = dict()
    for item in result:
        ref_name = item[0]
        namevariants[ref_name] = []

    for ref_name, variants in namevariants.items():
        for n in namevariants.keys():
            if(ref_name !=n and ref_name in n):
                variants.append(n)

    cleaned_namevariants = []
    for ref_name, variants in namevariants.items():
        if len(variants) > 0:
            cleaned_namevariants.append(sorted(variants+[ref_name], key=len))

    print(len(cleaned_namevariants))
    for variants in cleaned_namevariants:
        print(len(variants),"\t", variants)

if __name__ == "__main__":
    # remove_parenthesis_from_names()
    # connection.commit()
    # delete_rows_starts_with_non_letters()
    # delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA()
    # connection.commit()





    """
    split_artist_lists
    """

    def select_artists_like(text):
        sql = '''
        SELECT id, name
        FROM artists
        WHERE name LIKE '{text}';
        '''.replace('{text}', text)

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

    def select_exhibitions_of_artist(artist):
        sql = '''
        SELECT e.id, e.title
        FROM artists_exhibitions ae
        INNER JOIN exhibitions e ON e.id = ae.exhibition_id
        WHERE ae.artist_id = {artist_id}
        '''.replace("{artist_id}", str(artist[0]))

        for exhibition in connection.execute(sql):
            yield exhibition


    delimiters = ["|","*","•"]
    for artist in select_artists_like("%{delimiter}%_{delimiter}%".replace("{delimiter}", delimiters[1])):
        print(artist[1])
        for exhibition in select_exhibitions_of_artist(artist):
            print(exhibition[1], exhibition[0])
        print()

