def request_ikon_archive(date_from, date_to):
    import requests
    formdata = {
        "authenticityToken":"08bcd4db7f3ea318e51a0133d2aa9a16afe408c5", 
        "opening_tol_y"    : "{}".format(date_from.year),
        "opening_tol_m"    : "{}".format(date_from.month),
        "opening_tol_d"    : "{}".format(date_from.day),
        "opening_ig_y"     : "{}".format(date_to.year),
        "opening_ig_m"     : "{}".format(date_to.month),
        "opening_ig_d"     : "{}".format(date_to.day),
        "open_until_tol_y" : "1999",
        "open_until_tol_m" : "01",
        "open_until_tol_d" : "01",
        "open_until_ig_y"  : "2022",
        "open_until_ig_m"  : "12",
        "open_until_ig_d"  : "31",
        "sortOrder"        : "opening",
        "search"           : "Keresés"
    }
    print(formdata)
    result = requests.post("http://ikon.hu/archiv/search", data=formdata)
    return result.text

def get_pages_from_http(dirpath):
    """
    Query all weeks and save html to Disk
    """
    import os
    import datetime
    DATE_FROM = datetime.date(2014,1,1)+datetime.timedelta(days=7)
    DATE_TO =   datetime.date(2018, 11, 16)
    current_date = DATE_FROM
    while(current_date<DATE_TO):
        page = request_ikon_archive(current_date, current_date+datetime.timedelta(days=6))
        current_date+=datetime.timedelta(days=7)

        # save page to disk
        filename = "IkOn{0:%Y%m%d}-{1:%Y%m%d}.html".format(current_date, current_date+datetime.timedelta(days=6))
        filepath = os.path.join(dirpath, filename) 
        filepath = os.path.normpath(filepath)  

        with open(filepath, 'w', encoding='utf8') as html_file:
            html_file.write(page)
        
def get_filepaths_on_disk(dirpath):
    print("get files in folder...", dirpath)
    # get all htlm files
    import os
    for filename in os.listdir(dirpath):
        if filename.startswith("IkOn") and filename.endswith(".html"):
            filepath = os.path.join(dirpath, filename)
            yield filepath

def read_files_from_disk(filepaths):
    print("reading {} files from disk...".format(len(filepaths)))
    for filepath in filepaths:
        with open(filepath, encoding="utf-8") as html_file:
            page = html_file.read()
            yield page

def parse_html_pages(pages):
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
            raise Exception("Error occured while parsing title of element", elem)

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

    def parse_page(page):
        # Get rows with exhibitions
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page, features="lxml")
        elements = soup.select(".container .centercol .row")[1::]
        data = []
        for elem in elements:
            try:
                row = parse_row(elem)
                data.append(row)
            except Exception as err:
                print(err)

        return data

    print("parsing {} html pages...".format(len(pages)))
    data = [] 
    for page in pages:
        data += parse_page(page) 

    return data;

if __name__=="__main__":
    import datetime
    # page = request_ikon_archive(datetime.date(2018,1,1), datetime.date(2018,2,1))
    # parse_html_pages([page])

    # get_pages_from_http("./tmp")

    # filepaths = list(get_filepaths_on_disk("./tmp"))[:1]
    # pages = list(read_files_from_disk(filepaths))
    # data = parse_html_pages(pages)

    # for row in data:
    #     print("- {}, {}, {}".format(row['title'], row['date'], row['gallery']))
