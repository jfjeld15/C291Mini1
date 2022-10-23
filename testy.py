# This is me testing basic python concepts cuz im a dummy head (DELETE LATER!!)
import sqlite3

conn = sqlite3.connect('testdata.db')
c = conn.cursor()
c.execute('SELECT * FROM users WHERE uid = "ufo";')
rows = c.fetchall()
print(len(rows))
