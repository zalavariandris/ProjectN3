# -*- coding: utf-8 -*-
import mechanicalsoup
from datetime import date, timedelta

def request_ikon_archive(date_from, date_to):
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("https://ikon.hu/archiv/search")
    browser.select_form('form')
    browser["opening_tol_y"]= "{:04}".format(date_from.year)
    browser["opening_tol_m"]= "{:02}".format(date_from.month)
    browser["opening_tol_d"]= "{:02}".format(date_from.day)
    browser["opening_ig_y"]=  "{:04}".format(date_to.year)
    browser["opening_ig_m"]=  "{:02}".format(date_to.month)
    browser["opening_ig_d"]=  "{:02}".format(date_to.day)
    browser["sortOrder"]=     "opening"
    response = browser.submit_selected()
    return response.text
    
"""save page"""
def save_page(page, start_date, end_date, directory="./"):
    # save page to disk
    import os
    filename = "IkOn{:%Y.%m.%d.%a}-{:%Y.%m.%d.%a}.html".format(start_date, end_date)
    filepath = os.path.join(directory, filename) 
    filepath = os.path.normpath(filepath)  

    with open(filepath, 'w', encoding='utf8') as html_file:
        html_file.write(page)

if __name__ == "__main__":
    start_date = date(1999, 1, 4)
    start_date = date(2018, 3, 5)
    end_date = date(2020, 1, 1)
    while start_date <= end_date:
        print(start_date, "-", start_date+timedelta(days=7))
        page = request_ikon_archive(start_date, start_date+timedelta(days=6))
        save_page(page, start_date, start_date+timedelta(days=6), "./tmp")
        start_date += timedelta(days=7)
