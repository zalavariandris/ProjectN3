# -*- coding: utf-8 -*-
import pandas as pd

def get_filepaths_on_disk(dirpath):
    print("get files in folder...", dirpath)
    # get all htlm files
    import os
    for filename in os.listdir(dirpath):
        if filename.startswith("IkOn") and filename.endswith(".html"):
            filepath = os.path.join(dirpath, filename)
            yield filepath

def parse_page(page):
    def parse_date(elem):
        """
        parse ikon elements to TEXT as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS").
        """
        import datetime
        elem.select("div.year-month a")[0].text.split(" ")[0].replace(".", "")
        elem.select("div.day a")[0].text
        date_cell = elem.select("div.year-month a")[0].text
        year, month = [int(_) for _ in  date_cell.replace(".","").split()]
        day = int(elem.select("div.day a")[0].text)
        return datetime.date(year, month, day)

    def parse_title(elem):
        try:
            return elem.find("a", class_="title").text
        except Exception as err:
            raise Exception(err, elem)

    def parse_gallery(elem):
        return elem.find("a", class_="gallery").text

    def parse_artists(elem):
        return [_.text.rstrip(",") for _ in elem.find_all("a", class_="artists")]

    def parse_row(elem):
        return {
            "title": parse_title(elem),
            "gallery": parse_gallery(elem),
            "date": parse_date(elem),
            "artists": parse_artists(elem),
            "html": str(elem)
        }

    # Get rows with exhibitions
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page, features="lxml")
    elements = soup.select(".container .centercol .row")

    if elements[0].text.strip()=="Nincs találat!":
        """ No results! """
        return []

    """ Resukts found """
    # first element is 
    data = []
    for elem in elements[1::]:
        try:
            row = parse_row(elem)
            data.append(row)
        except Exception as err:
            raise err

    return data

def main():
    ## Collect data from html files
    data = [] 
    all_files = list(get_filepaths_on_disk("./tmp"))
    print("parsing {} html pages...".format(len(all_files)))
    for i, filepath in enumerate(all_files):
        print("parsing file...{}/{} {}".format(i, len(all_files), filepath))
        with open(filepath, encoding="utf-8") as html_file:
            page = html_file.read()
            page_data = parse_page(page)
            print("  found {} exhibitions".format(len(page_data)))
            data += page_data

    return data

if __name__=="__main__":
    data = main()
    for row in data:
        print(row)
    
    # ## Create dataframe
    # df = pd.DataFrame(data)
    # for i in range(len(df['artists'])):
    #     # clean artists array from falsy values
    #     df['artists'][i]= [a.strip() for a in df['artists'][i] if a.strip()]

    # ## Export to excel
    # df2 = df.copy()
    # # format artist list to string. Artists seperated with ';'
    # for i in range(len(df)):
    #     df2.loc[i,'artists'] = "; ".join( [a.strip() for a in df.loc[i, 'artists'] if a.strip()] )
    # df2.to_excel("ikon.xlsx")
    
    