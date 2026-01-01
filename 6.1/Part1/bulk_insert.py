import sqlite3

connection = sqlite3.connect('database.db')

with open('bulk_insert.sql') as f:
    connection.executescript(f.read())
