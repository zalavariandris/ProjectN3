from utilities.profiler import profile
from CRUD import *
import re
def connectToDatabase(filepath):
    import sqlite3
    from sqlite3 import Error
    try:
        connection = sqlite3.connect(filepath)
    except Error as err:
        print(err)

    import re
    def regexp(y, x, search=re.search):
        return 1 if search(y, x) else 0

    connection.create_function('regexp', 2, regexp)

    return connection

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
def find_variants(connection):
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

@profile
def find_variants(connection, searchlimit=None):
    sql = '''
    SELECT id, name
    FROM artists
    ORDER BY name ASC;
    '''

    all_artists = connection.execute(sql).fetchall()[:searchlimit]
    variants = dict()

    for A in all_artists:
        for B in all_artists:
            if A[1] in B[1] and A[0]!=B[0] and B not in variants:
                if A not in variants:
                    variants[A] = []
                variants[A].append(B)

    return sorted( [[a] + b for a, b in variants.items()], key=lambda a : len(a[1]) )

def remove_frequent_indicatives(connection):
    """
    író
    előadása
    építész
    énekesnő
    esztéta
    képzőművész
    fotóművész
    szobrászművész
    művészettörténész
    kurátor
    társkurátor
    fotográfus
    festőművész
    DLA
    képzőművész / visual artist
    grafikusművész
    médiaművész
    építész
    iparművész
    fotóriporter
    filmkritikus
    műkritikus
    művészeti író    
    kritikus
    esztéta
    szerkesztője
    művészettörténész
    művészetkritikus
    esztéta
    egyetemi docens
    egyetemi adjunktus
    Mnkácsy-díjas festőművész
    Munkácsy-díjas
    zenész
    zeneszerző
    basszusklarinét
    filmkritikus
    filmtörténész
    filmesztéta
    irodalmár
    filozófus
    előadása
    médiakritikus
    esztéta  médiakritikus
    fotográfus
    egyetemi tanár
    """
    pass


filmrendező
rendező
kulturális antropológus
rende
főszerkesztő
 szerkesztőművészettörténész

def delete_suspicous(connection):
    # with two spaces "  "
    with a single dash: " - "
    " & "
    with lot of spaces "% % % %"
    with strange characters not latin
    sql = "DELETE FROM artists WHERE name NOT REGEXP '^[A-Ș]';"



if __name__ == "__main__":
    connection = connectToDatabase("../ikon.db")
    remove_parenthesis_from_names(connection)
    delete_rows_starts_with_non_letters(connection)
    split_artist_entries_with_multiple_artist_names(connection)
    delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA(connection)
    remove_frequent_indicatives(connection)
    connection.commit()

    # clean
    # művész, író, költő, képzőnűvész, művészeti író, ***díjas építést

    for variants in [v for v in find_variants(connection) if len(v[0][1].split(" "))>1]:
        for a in variants:
            print("-", a[1])
        print()
        # if len(variants[1].split(" "))==1:
        #     artist = list(select_artists_where_name_like(connection, variants[1]))[0]
        #     exhibition = list(select_exhibitions_where_artist_is(connection, artist))[0]
        #     print(variants[0], "    (  ",exhibition[1], " )")
        #     print(variants[1:])
        #     print()

    # for a in select_artists_where_name_like(connection, "%  %"):
    #     e = select_exhibitions_of_artist(connection, a)
    #     print(a[1], "      ", e[0][1])

    def delete_suspicous(connection):


