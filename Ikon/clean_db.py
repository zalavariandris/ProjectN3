from utilities.profiler import profile
from CRUD import *
import re


@profile
def select_artists_with_exhibition_count(connection):
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

# ========================================================================
@profile
def delete_rows_starts_with_non_letters(connection):
    # Törölj mindent, ami nem betüvel kezdődik
    sql = "SELECT name FROM artists WHERE name NOT REGEXP '^[A-Ș]' ORDER BY name ASC;"
    result = connection.execute(sql).fetchall()
    print(len(result)) if result else None
    for item in result:
        print(item[0])

    sql = "DELETE FROM artists WHERE name NOT REGEXP '^[A-Ș]';"
    connection.execute(sql)

@profile
def delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA(connection):
    sql = "SELECT name FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera' ORDER BY name ASC;"
    result = connection.execute(sql).fetchall()
    print(len(result)) if result else None
    for item in result:
        print(item[0])

    sql = "DELETE FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera';"
    connection.execute(sql)

@profile
def remove_parenthesis_from_names(connection):
    sql = '''
    SELECT id, name
    FROM artists
    WHERE name LIKE '%(%)%'
    '''
    table = connection.execute(sql).fetchall()

    for row in table:
        artist_id = row[0]
        name = row[1]
        clean_name = re.sub(r" ?\([^)]+\)", "", name)
        print(name, " -> ", clean_name)
        update_artist_where_id_is(connection, artist_id, clean_name)

@profile
def split_artist_entries_with_multiple_artist_names(connection):
    """
    Barna Orsolya – Fodor Emese – Kristóf Gábor – Pálinkás Bence György
    Bondor Csilla Csurka Eszter Kucsora Márta Sipos Eszter Schmal Róza Verebics Ági Verebics Kati Földesi Barnabás Herman Levente Kondor Attila Kovács Lehel Lőrincz Tamás Péterfy Ábel Szotyory László
     Bernát András Bullás József Chilf Mária Csiszér Zsuzsa Fóris Katalin Gajzágó Donáta Horváth Lóczi Judit Káldi Kata Korodi Luca Kovács Lola Lengyel András Madácsy István Nagy Gábor György Nagy Zsófia Nemere Réka Ötvös Zoltán Soós Tamás Szabó Attila Szilágy
Bernát András Bullás József Chilf Mária Csiszér Zsuzsa Fóris Katalin Gajzágó Donáta Horváth Lóczi Judit Káldi Kata Korodi Luca Kovács Lola Lengyel András Madácsy István Nagy Gábor György Nagy Zsófia Nemere Réka Ötvös Zoltán Soós Tamás Szabó Attila Szilágy

    - Barna Orsolya – Gosztola Kitti – Pálinkás Bence György
    - Gosztola Kitti & Hegedűs Fanni & Pálinkás Bence
    - Gosztola Kitti & Pálinkás Bence & Hegedűs Fanni
    - Gosztola Kitti - Hegedűs Fanni - Pálinkás Bence György
    - Gosztola Kitti – Pálinkás Bence György
    - Gosztola Kitti–Pálinkás Bence György

    - Gosztola Kitti & Hegedűs Fanni & Pálinkás Bence
    - Gosztola Kitti & Pálinkás Bence & Hegedűs Fanni
    - Gosztola Kitti - Hegedűs Fanni - Pálinkás Bence György

    - Herendi Péter  ▪ Gábor Éva Mária

    - Hencze Tamás
    - Haraszty István  Hencze Tamás
    """
    def split_names(text, delimiter):
        return [_.strip() for _ in filter(None, text.split(delimiter))]

    def insert_artist_if_unique(name):
        row = connection.execute("SELECT id FROM artists WHERE name=?;", (name, )).fetchone()
        if row==None:
            cursor = connection.cursor()
            artist_id = insert_artist(connection, artist_name)

        else:
            artist_id = row[0]
        return artist_id, name

    for delimiter in ["|","*","•", " – "]:
        for artist_list_id, artist_list_text in select_artists_where_name_like(connection, "%{delimiter}%_{delimiter}%".replace("{delimiter}", delimiter)):
            # find exhibitions of the current text of artist names
            exhibitions = list(select_exhibitions_of_artist(connection, (artist_list_id, )))
            exhibition_ids = [_[0] for _ in exhibitions]
            
            # extact artist names from text
            artists_names = split_names(artist_list_text, delimiter) 

            # create artists from names extracted from text, if not exists
            for artist_name in artists_names:
                artist = insert_artist_if_unique(artist_name)

                # link exhibitions to artists
                for exhibition_id in exhibition_ids:
                    link_artist_to_exhibition(connection, artist, (exhibition_id, ))

            # clear artist lists from tables
            for exhibition_id in exhibition_ids:
                unlink_artist_from_exhibition(connection, (artist_list_id, ), (exhibition_id, ))
            delete_artist_where_id_is(connection, artist_list_id)

@profile
def find_variants(connection, searchlimit=None):
    sql = '''
    SELECT id, name
    FROM artists
    ORDER BY name ASC;
    '''
    all_artists = connection.execute(sql).fetchall()[:searchlimit]
    variants = dict()
    stack = set()
    for A in all_artists:
        for B in all_artists:
            if A[0]!=B[0] and A[1].lower() in B[1].lower():
                if B not in stack:
                    if A not in variants:
                        variants[A] = []
                        stack.add(A)
                    variants[A].append(B)
                    stack.add(B)


    return sorted( [[a] + b for a, b in variants.items()], key=lambda a : len(a[1]) )

def remove_frequent_indicatives(connection):

    indicatives = ["író",
    "előadása",
    "építész",
    "énekesnő",
    "esztéta",
    "képzőművész",
    "fotóművész",
    "szobrászművész",
    "művészettörténész",
    "kurátor",
    "társkurátor",
    "fotográfus",
    "festőművész",
    "DLA",
    "képzőművész / visual artist",
    "grafikusművész",
    "médiaművész",
    "iparművész",
    "fotóriporter",
    "filmkritikus",
    "műkritikus",
    "művészeti író    ",
    "kritikus",
    "szerkesztője",
    "művészetkritikus",
    "egyetemi docens",
    "egyetemi adjunktus",
    "egyetemi tanár",
    "Mnkácsy-díjas",
    "zenész",
    "zeneszerző",
    "basszusklarinét",
    "filmtörténész",
    "filmesztéta",
    "irodalmár",
    "filozófus",
    "médiakritikus",
    "riporter",
    "pszichológus",
    "költő",
    "témavezető"]

    sql = '''
    SELECT id, name FROM artists;
    '''
    for artist in connection.execute(sql).fetchall():
        for indicative in indicatives:
            if indicative in artist[1]:
                clean_name = artist[1].replace(indicative, "").strip()
                update_artist_where_id_is(connection, artist[0], clean_name)


# filmrendező
# rendező
# kulturális antropológus
# rende
# főszerkesztő
#  szerkesztőművészettörténész

def tag_suspicous(connection):
    # contains weird characters  
    sql = '''
    UPDATE artists
    SET suspicious="contains weird characters"
    WHERE name REGEXP '[:/*©"#♥]';
    '''
    sql = '''
    UPDATE artists
    SET suspicious="contains weird characters"
    WHERE name REGEXP '[^a-zA-ZőűŐŰĂčć\u00C0-\u00FF-. ]';
    '''
    connection.execute(sql)

    # with two spaces "  "
    sql = '''
    UPDATE artists
    SET suspicious="two spaces"
    WHERE name LIKE "%  %"
    '''
    # with lot of spaces
    sql = '''
    UPDATE artists
    SET suspicious="too many words"
    WHERE name LIKE "% % % %";
    '''
    connection.execute(sql)

    # one word only
    sql = '''
    UPDATE artists
    SET suspicious="single word only"
    WHERE name NOT LIKE "% %";
    '''
    connection.execute(sql)

    # contains numbers
    sql = '''
    UPDATE artists
    SET suspicious="contains numbers"
    WHERE name REGEXP '[0-9]';
    '''
    connection.execute(sql)

    # contains 'és'
    sql = '''
    UPDATE artists
    SET suspicious="contains 'és'"
    WHERE name LIKE '%és%';
    '''
    connection.execute(sql)

    # contains 'foglalkozás'
    sql = '''
    UPDATE artists
    SET suspicious="contains 'foglalkozás'"
    WHERE name LIKE '%foglalkozás%';
    '''
    connection.execute(sql)

    # contains 'kiállítás'
    sql = '''
    UPDATE artists
    SET suspicious="contains 'kiállítás'"
    WHERE name LIKE '%kiállítás%';
    '''
    connection.execute(sql)


    # contains 'Akadémia'
    sql = '''
    UPDATE artists
    SET suspicious="contains 'Akadémia'"
    WHERE name LIKE '%Akadémia%';
    '''
    connection.execute(sql)

        # contains 'Akadémia'
    sql = '''
    UPDATE artists
    SET suspicious="contains 'tagok'"
    WHERE name LIKE '%tagok%';
    '''
    connection.execute(sql)
    
    
def delete_suspicious(connection):
    sql = '''
    DELETE
    FROM artists
    WHERE suspicious NOT NULL;
    '''
    connection.execute(sql)

def convert_artists_to_title_case(connection):
    for artist in select_artists(connection):
        if artist[1] != artist[1].title():
            update_artist_where_id_is(connection, artist[0], artist[1].title())

if __name__ == "__main__":
    connection = connectToDatabase("../resources/ikon.db")
    remove_parenthesis_from_names(connection)
    delete_rows_starts_with_non_letters(connection)
    split_artist_entries_with_multiple_artist_names(connection)
    delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA(connection)
    remove_frequent_indicatives(connection)
    tag_suspicous(connection)
    delete_suspicious(connection)
    convert_artists_to_title_case(connection)
    connection.execute("DELETE FROM ARTISTS WHERE name LIKE 'és mások...';")
    connection.commit()

    # fin variants and merge them
    def merge_variants(connection, variants):
        sql = '''
        SELECT exhibition_id
        FROM artists_exhibitions
        WHERE artist_id IN ({});
        '''.format( ",".join(["?"]*len(variants) ) )

        exhibitions = connection.execute(sql, [a[0] for a in variants]).fetchall()
        artist_id = insert_artist(connection, variants[0][1])
        for exhibition in exhibitions:

            print("link artist to exhibition", artist_id,"->", exhibition)
            link_artist_to_exhibition(connection, (artist_id,), exhibition)

        for variant in variants:
            delete_artist_where_id_is(connection, variant[0])

    for variants in find_variants(connection):
        for a in variants:
            print("-", a[1])
        print()
        merge_variants(connection, variants)

    connection.commit()
        # if len(variants[1].split(" "))==1:
        #     artist = list(select_artists_where_name_like(connection, variants[1]))[0]
        #     exhibition = list(select_exhibitions_where_artist_is(connection, artist))[0]
        #     print(variants[0], "    (  ",exhibition[1], " )")
        #     print(variants[1:])
        #     print()




