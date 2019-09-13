import scrape
from build_db import *
from CRUD import *
if __name__ == "__main__":
    connection = init_database()

    """
    Fill tables with data
    """
    # read data from htlm files
    filepaths = list(scrape.get_filepaths_on_disk("./tmp"))
    pages = list(scrape.read_files_from_disk(filepaths))
    data = scrape.parse_html_pages(pages)
    
    fill_database(connection, data)
    