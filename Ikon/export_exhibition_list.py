from utilities.profiler import profile
import CRUD
import pandas as pd

if __name__ == "__main__":
    connection = CRUD.connectToDatabase("./data/ikon2.db")
    sql = '''
    SELECT e.id, e.ikonid, e.title, e.date, g.name
    FROM exhibitions e
    JOIN galleries g ON g.id = e.gallery_id
    ORDER BY date DESC, title ASC;
    '''
    
    data = connection.execute(sql).fetchall()
    df = pd.DataFrame(data, columns=['id', 'ikonid', 'title', 'date', 'gallery'])

    # Create events column
    events = [
        "vezetés",
        "tárlatvezetés",
        "finisszázs",
        "finissage",
        "előadás",
        "beszélgetés",
        "interjú",
        "könyvbemutató",
        "workshop",
        "bemutató",
        "pályázat",
        "felhívás",
        "Reading Club"
    ]
    
    for idx, row in df.iterrows():
        print(idx, row['id'], row['title'])
        for event in events:
            if event in row['title'].lower():
                df.loc[idx, 'event'] = event

    # Create artists column
    progress = 0
    progress_max = len(df)
    for idx, row in df.iterrows():
        progress+=1
        print("{}/{}".format(progress, progress_max), row['title'])
        artists = CRUD.select_artists_of_exhibition(connection, (row['id'], ) )
        names = "; ".join([a[1] for a in artists])
        df.loc[idx, 'artists'] = names

    df = df.set_index('id')
    df.to_excel('./data/exhibition_list_clean_v000.xlsx')
