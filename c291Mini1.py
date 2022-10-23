"""
CMPUT 291, Fall 2022
Mini-Project 1
Jonathan Fjeld, Ying Wan, Crystal Zhang
"""

import sqlite3
import sys  # For taking command line argument
from getpass import getpass  # For making the password non-visible at the time of typing
import hashlib  # Used for hashing passwords to prevent SQL injection

def setup(dbName):
    # connects to an sql db, returns a cursor and conection variables
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    return conn, c

def getID():
    # Loops until user/artist enters a valid ID (under 4 characters)
    valid = False
    while not valid:
        id = input("Enter user/artist ID: ").lower()  # Lower for case insensitivity
        if len(id) <= 4 and len(id) > 0:
            valid = True
        else:
            print("Please enter a valid ID (between 1-4 characters)") # Loop again
    return id

def login(id, pwd, c, conn):
    isUser = False
    isArtist = False
    c.execute('SELECT * FROM users WHERE pwd = ?;', (pwd,))  # This format escapes special characters (prevents SQL injection)
    print(c.fetchall())
    return
    # if len(c.fetchall()) != 0:
    #     isUser = True
    # c.execute('SELECT * FROM artists WHERE aid = ?;', id,)
    # if len(c.fetchall()) != 0:
    #     isArtist = True
    # if isUser == False and isArtist == False:


if __name__ == "__main__":
    exit = False
    loggedIn = False
    conn, c = setup(sys.argv[1])
    while not exit:
        while not loggedIn:
            print("Welcome! Please login to continue.")
            id = getID()
            pwd = getpass("Enter password:")  # Non-visible password at the time of typing
            login(id, pwd, c, conn)

