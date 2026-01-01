import sqlite3

connection = sqlite3.connect('database.db')
connection.row_factory = sqlite3.Row

data = connection.execute("SELECT * FROM characters").fetchall()
connection.close()

for d in data:
    print(d[0], d[1], d[2])
