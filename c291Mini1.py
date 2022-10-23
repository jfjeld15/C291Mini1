"""
CMPUT 291, Fall 2022
Mini-Project 1
Jonathan Fjeld, Ying Wan, Crystal Zhang
"""

import sqlite3
import sys  # For taking command line argument

def setupTables(dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    return conn, c

if __name__ == "__main__":
    dbName = sys.argv[1]
    conn, c = setupTables(dbName)
    c.execute("SELECT * FROM users;")
    rows = c.fetchall()
    print(rows)
