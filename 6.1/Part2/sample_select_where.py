import sqlite3

connection = sqlite3.connect('database.db')

cur = connection.cursor()

data = cur.execute("SELECT c_name FROM characters WHERE c_attack > 2").fetchall()
print(data)

connection.close()
