import sqlite3
from sqlite3 import Error
try:
    connection = sqlite3.connect("../ikon.db")
except Error as err:
    print(err)

import re
def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0

connection.create_function('regexp', 2, regexp)

import inspect
def delete_rows_starts_with_non_letters():
	# Törölj mindent, ami nem betüvel kezdődik
	sql = "SELECT name FROM artists WHERE name NOT REGEXP '^[A-Ș]' ORDER BY name ASC;"
	result = connection.execute(sql).fetchall()
	print(len(result))
	for item in result:
		print(item[0])


	sql = "DELETE FROM artists WHERE name NOT REGEXP '^[A-Ș]';"
	connection.execute(sql)
	connection.commit()

def delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA():
	sql = "SELECT name FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera' ORDER BY name ASC;"
	result = connection.execute(sql).fetchall()
	print(len(result))
	for item in result:
		print(item[0])

	sql = "DELETE FROM artists WHERE name LIKE 'Az %' OR name LIKE 'A %' AND name NOT LIKE 'A Fehér Vera';"
	connection.execute(sql)
	connection.commit()


# delete_rows_starts_with_non_letters()
# delete_rows_starts_with_A_or_AZ_but_A_FEHER_VERA()

def select_artists_with_exhibition_count():
	sql = '''
	SELECT
		a.name,
	    COUNT(*)
	FROM
	    artists_exhibitions ae
	INNER JOIN
		artists a ON a.id = ae.artist_id
	GROUP BY
	    artist_id
	ORDER BY COUNT(*) DESC;
	'''

	result = connection.execute(sql).fetchall()
	print(len(result))
	for item in result:
		print(item)

sql = '''
SELECT name
FROM artists;
'''
result = connection.execute(sql).fetchall()
namevariants = dict()
for item in result:
	ref_name = item[0]
	namevariants[ref_name] = []

for ref_name, variants in namevariants.items():
	for n in namevariants.keys():
		if(ref_name !=n and ref_name in n):
			variants.append(n)

cleaned_namevariants = []
for ref_name, variants in namevariants.items():
	if len(variants) > 0:
		cleaned_namevariants.append(sorted(variants+[ref_name], key=len))

print(len(cleaned_namevariants))
for variants in cleaned_namevariants:
	print(len(variants),"\t", variants)



