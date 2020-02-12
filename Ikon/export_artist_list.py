from utilities.profiler import profile
import CRUD
import pandas as pd

KISVARSÓ
NAGY BOGLÁRKA
indicatives = [
    "kulturális antropológus",
    "történész",
    "antropológus",
    "tanszékvezető",
    "irodalomtörténész",
    "filmkritikus",
    "tárlatvezetés",
    "főiskolai docens",
    "újságíró",
    "akadémikus",
    "műkritikus",
    "etnográfus",
    "fotómuzeológus",
    "műfordító",
    "műgyűjtő",
    "szerkesztő",
    "szépségkutató",
    "művészeti író",
    "író",
    "előadása",
    "építész",
    "énekesnő",
    "esztéta",
    "képzőművészek",
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
    "művészeti író",
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
    "témavezető",
    "történész"]

if __name__ == "__main__":
    connection = CRUD.connectToDatabase("./data/ikon.db")
    sql = '''
    SELECT a.id, a.name, COUNT(ae.artist_id) as No_exhibitions
    FROM artists_exhibitions ae
    JOIN artists a ON a.id = ae.artist_id
    GROUP BY ae.artist_id
    ORDER BY No_exhibitions DESC;
    '''
    
    data = connection.execute(sql).fetchall()
    df = pd.DataFrame(data, columns=['id', 'name', 'no_exhibitions'])
    
        
    for idx, row in df.iterrows():
        print(idx, row['id'], row['name'])
        for indicative in indicatives:
            if indicative in row['name']:
                df.loc[idx, 'name'] = row['name'].replace(indicative, '').strip()
                df.loc[idx, 'indicative'] = indicative

    df.to_excel('./data/artist_list.xlsx')