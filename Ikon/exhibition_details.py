"""read exhibition list"""
import pandas as pd
df = pd.read_excel("./data/exhibition_list_clean_v000.xlsx", index_col='id')


"""with each ikonid scrape ikon for exhibitions and save details html to disk"""
import mechanicalsoup
browser = mechanicalsoup.StatefulBrowser()
progress=0
for idx, row in df.iterrows():
    ikonid = row['ikonid']
    url = "https://ikon.hu/cal/{}".format(ikonid)
    browser.open(url)
    soup = browser.get_current_page()
    title = soup.find("title").text
    filepath = "./tmp/exhibition_details/exhibition{}.html".format(ikonid, title)
    print("{}/{} - {}".format(progress, len(df), filepath))
    with open(filepath, 'w', encoding='utf8') as html_file:
        html_file.write(str(soup))
    progress+=1