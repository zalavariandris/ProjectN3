I. scrape_ikon.py
II. parse_ikon.py
III. build_sql.py
IV. clean_sql.py
 na ezen még lehetne javítani.
 - a find_variants, lényegében egy inclusive filter.
 azaz a kissebb megvan  nagyobban, akor azt egynek tekinti.
 Szabó Eszter és Szabó Eszter Ágnes egybeolvad.
 - hiányzik az elírésok felkutatása, azaz fuzzy matching.
   - A Fehér Vera != A. Fehrér Verával.
   - Beke László != Beke Laszó-val.

CRUD.py
Create Read Update SQL table helper functions