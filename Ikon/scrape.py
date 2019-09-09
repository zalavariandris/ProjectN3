def get_filepaths_on_disk(dirpath):
    print("get files in folder...", dirpath)
    # get all htlm files
    import os
    for filename in os.listdir(dirpath):
        if filename.startswith("IkOn") and filename.endswith(".html"):
            filepath = os.path.join(dirpath, filename)
            yield filepath

def read_files_from_disk(filepaths):
    print("reading files from disk...")
    for filepath in filepaths:
        with open(filepath, encoding="utf-8") as html_file:
            page = html_file.read()
            yield page

def parse_html_pages(pages):
    def parse_date(elem):
        import datetime
        elem.select("div.year-month a")[0].text.split(" ")[0].replace(".", "")
        elem.select("div.day a")[0].text
        date_cell = elem.select("div.year-month a")[0].text
        year, month = [int(_) for _ in  date_cell.replace(".","").split()]
        day = int(elem.select("div.day a")[0].text)
        return datetime.date(year, month, day)

    def parse_title(elem):
        return elem.find("a", class_="title").text

    def parse_gallery(elem):
        return elem.find("a", class_="gallery").text

    def parse_artists(elem):
        return [_.text.rstrip(",") for _ in elem.find_all("a", class_="artists")]

    def parse_row(elem):
        return {
            "title": parse_title(elem),
            "gallery": parse_gallery(elem),
            "date": parse_date(elem),
            "artists": parse_artists(elem)
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
            except AttributeError as err:
                print(err)
                
        return data

    print("parsing {} html pages...".format(len(pages)))
    data = [] 
    for page in pages:
        data += parse_page(page) 

    return data;