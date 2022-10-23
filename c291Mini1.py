"""
CMPUT 291, Fall 2022
Mini-Project 1
Jonathan Fjeld, Ying Wan, Crystal Zhang
"""

import sqlite3
import sys  # For taking command line argument
from getpass import getpass  # For making the password non-visible at the time of typing

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

def newUser(id, pwd, c, conn):
    name = input("New user detected! Please enter your name to create an account : ").lower
    c.execute("INSERT INTO users VALUES (?, ?, ?);", (id, name, pwd))
    conn.commit()


def login(id, pwd, c, conn):
    isUser = False
    isArtist = False
     # This format escapes special characters (prevents SQL injection):
    c.execute("SELECT * FROM users WHERE lower(uid) = ? AND pwd = ?;", (id, pwd,)) 
    if len(c.fetchall()) != 0:
        isUser = True
    c.execute("SELECT * FROM artists WHERE lower(aid) = ? AND pwd = ?;", (id, pwd,))
    if len(c.fetchall()) != 0:
        isArtist = True
    if isUser == False and isArtist == False:
        # User does not exist, create one!
        newUser(id, pwd, c, conn)


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

