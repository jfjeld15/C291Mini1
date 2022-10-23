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
    # Creates a new user if the input uid does not have an account associated with it
    name = input("New user detected! Please enter your name to create an account: ").lower()
    c.execute("INSERT INTO users VALUES (?, ?, ?);", (id, name, pwd))
    conn.commit()


def login(id, pwd, c, conn):
    # Logs in as user or artist. Creates new user if user does not exist. Returns string representing if a user or an artist logged in
    isUser = False
    isArtist = False
     # This format escapes special characters (prevents SQL injection):
    c.execute("SELECT * FROM users WHERE lower(uid) = ?;", (id,)) 
    if len(c.fetchall()) != 0:
        isUser = True
    c.execute("SELECT * FROM artists WHERE lower(aid) = ?;", (id,))
    if len(c.fetchall()) != 0:
        isArtist = True

    if isUser == False and isArtist == False:
        # User does not exist, create one!
        newUser(id, pwd, c, conn)
        print("Login successful.")
        return "user", True

    if isUser == True and isArtist == False:
        c.execute("SELECT * FROM users WHERE lower(uid) = ? AND pwd = ?;", (id, pwd,))
        if len(c.fetchall()) != 0:
            print("Login successful.")
            return "user", True
        else:
            # The uid exists, but password is incorrect
            print("Login unsuccessful: Invalid password.")
            return "none", False

    if isUser == False and isArtist == True:
        c.execute("SELECT * FROM artists WHERE lower(aid) = ? AND pwd = ?;", (id, pwd,))
        if len(c.fetchall()) != 0:
            print("Login successful.")
            return "artist", True
        else:
            # The uid exists, but password is incorrect
            print("Login unsuccessful: Invalid password.")
            return "none", False
    
    if isUser == True and isArtist == True:
        # The id exists in both users AND artists
        result = input("ID found for both users and artists, login as user or artist (type 'user' or 'artist')? ").lower()
        if result == "user":
            c.execute("SELECT * FROM users WHERE lower(uid) = ? AND pwd = ?;", (id, pwd,))
            if len(c.fetchall()) != 0:
                print("Login successful.")
                return "user", True
            else:
                # The uid exists, but password is incorrect
                print("Login unsuccessful: Invalid password.")
                return "none", False
        elif result == "artist":
            c.execute("SELECT * FROM artists WHERE lower(aid) = ? AND pwd = ?;", (id, pwd,))
            if len(c.fetchall()) != 0:
                print("Login successful.")
                return "artist", True
            else:
                # The uid exists, but password is incorrect
                print("Login unsuccessful: Invalid password.")
                return "none", False
        else:
            print("Invalid response.")
            return "none", False


def userMenu():
    # User commands will be implemented here
    return

def artistMenu():
    # Artist commands will be implemented here
    return

if __name__ == "__main__":
    exit = False
    loggedIn = False
    conn, c = setup(sys.argv[1])
    while not exit:
        # Infinite loop until the user inputs "exit"
        while not loggedIn:
            print("Welcome! Please login to continue.")
            id = getID()
            pwd = getpass("Enter password:")  # Non-visible password at the time of typing
            who, loggedIn = login(id, pwd, c, conn)
        # Go to one of two different menus based on who is logged in:
        if who == "user":
            exit, loggedIn = userMenu()
        elif who == "artist":
            exit, loggedIn = artistMenu()
        else:
            print("How did you get here?")
            exit = True

