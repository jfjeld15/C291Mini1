"""
CMPUT 291, Fall 2022
Mini-Project 1
Jonathan Fjeld, Ying Wan, Crystal Zhang
"""

import sqlite3
import sys  # For taking command line argument
import searchPlaySong
import searchArtist
import artistActions
from getpass import getpass  # For making the password non-visible at the time of typing


def setup(dbName):
    # connects to an sql db, returns a cursor and conection variables
    # conn = sqlite3.connect('./testdata.db')
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
        result = input("ID found for both users and artists, login as user or artist? (type 'user' or 'artist'): ").lower()
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


def startSession(c, conn, id, snoNext):
    # Create a session with a unique session number for the current logged in user id.
    # a user should only have ONE session at a time! (This should be checked first)
    c.execute("SELECT * FROM sessions WHERE uid = ? AND end IS NULL;", (id,))
    if len(c.fetchall()) != 0:
        # A session is already in progress!
        print("ERROR: There is already a session in progress. Please end the current session before starting a new one.")
    else:
        c.execute("INSERT INTO sessions VALUES (?, ?, DATE('now'), NULL);", (id, snoNext))
        conn.commit()
        snoNext += 1  # For creating the next session in the future
        print("Session started.")
    return snoNext

def endSession(c, conn, id):
    # The user wants to end the current session. A session can only be ended if there is currently a session in progress.
        c.execute("SELECT * FROM sessions WHERE uid = ? AND end IS NULL;", (id,))
        if len(c.fetchall()) != 0:
            # A session is in progress, we can end it.
            c.execute("UPDATE sessions SET end = DATE('now') WHERE end IS NULL;")
            conn.commit()
            print("Session ended.")
        else:
            print("ERROR: No session in progress. Please start a session before trying to end it.")

    
def userMenu(id, c, conn):
    # User commands will be implemented here
    # First, get the current highest sno from sessions (so we do not accidentally create a duplicate session)
    c.execute("SELECT MAX(sno) FROM sessions WHERE uid = ?;", (id,))
    try:
        snoNext = c.fetchone()[0] + 1  # This will be the session number if a new session is started (Will always be unique)
    except TypeError:
        # a TypeError occurs when fetchone() returns (None,), which is not subscriptable
        snoNext = 1  # The user has not had any sessions yet
        
    print("Please select a command (enter a value between 1 and 6): ")
    print("1. Start a session \n2. Search for songs and playlists \n3. Search for artists \n4. End the current session \n5. Log out \n6. Quit the program")
    try:
        command = int(input())
    except ValueError:
        # The user inputted a non-numeric value. Treat this as an incorrect option
        command = 0

    if command == 1:
        # The user wants to start a session with a unique sno (snoNext), starting at today's date and the end date is null
        snoNext = startSession(c, conn, id, snoNext)
        return False, True
        
    elif command == 2:
        # The user wants to search for songs and playlists. After they have selected songs, they may perform SONG ACTIONS as specified on the eClass spec
        searchPlaySong.search(conn, c, id)
        return False, True

    elif command == 3:
        # The user wants to search for artists.
        searchArtist.search(conn, c, id)
        return False, True

    elif command == 4:
        # The user wants to end the current session.
        endSession(c, conn, id)
        return False, True

    elif command == 5:
        # The user wants to log out, but not quit the program
        print("Logout Successful")
        return False, False

    elif command == 6:
        # The user wants to quit the program
        return True, True
        
    else:
        print("Invalid option selected (enter a value between 1 and 6)")
        return False, True

def artistMenu(id, c, conn):
    # Artist commands will be implemented here.
    print("Please select a command (enter a value between 1 and 4): ")
    print("1. Add a song \n2. Find top fans and playlists \n3. Log out \n4. Quit the program")
    try:
        command = int(input())
    except ValueError:
        # The artist inputted a non-numeric value. Treat this as an incorrect option
        command = 0
    
    if command == 1:
        # The artist wants to add a song.
        artistActions.addSong(c, id, conn)
        return False, True
        
    elif command == 2:
        # The artist wants to find their top fans and playlists
        artistActions.findTop(c, id)
        return False, True
    
    elif command == 3:
        # The artist wants to log out, but not quit the program
        print("Logout Successful")
        return False, False

    elif command == 4:
        # The artist wants to quit the program
        return True, True

    else:
        print("Invalid option selected (enter a value between 1 and 4)")
        return False, True


if __name__ == "__main__":
    exit = False
    loggedIn = False
    conn, c = setup(sys.argv[1])
    # conn,c=setup('placeholder')
    while not exit:
        # Infinite loop until the user inputs "exit"
        while not loggedIn:
            print("Welcome! Please login to continue.")
            print("NEW USERS: Enter an unused ID and password to register.")
            id = getID()
            pwd = getpass("Enter password:")  # Non-visible password at the time of typing
            who, loggedIn = login(id, pwd, c, conn)
        # Go to one of two different menus based on who is logged in:
        if who == "user":
            exit, loggedIn = userMenu(id, c, conn)
        elif who == "artist":
            exit, loggedIn = artistMenu(id, c, conn)
        else:
            print("How did you get here?")
            exit = True
    print("Goodbye!")

