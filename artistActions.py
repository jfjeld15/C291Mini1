def addSong(cursor, aid, conn):
    '''
    Adds a song by title and duration. Also allows for artist to input other artists (if 
    the inputted artist is not in the artists table, the program will ignore it).

    Parameters
    ----------
    cursor: connection beftween database and queries
    aid: id of artist logged on
    connection: connection to the database
    '''
    title = input("Input song title: ")
    while True:
        # Loops until the user inputs a positive integer duration
        try:
            dur = int(input("Input song duration: "))
        except ValueError:
            print("Please input a positive integer.")
            continue
        if dur <= 0:
            print("Please input a positive integer.")
            continue
        break
    artists = input("Input id of additional artists (leave blank if none): ").split(";")
    # adds logged in artist if not already in list
    if aid not in artists:
        artists.append(aid)

    # counts the number of songs that have the same name and duration by the artist
    query = f'''SELECT COUNT(*) 
            FROM songs s, perform p, artists a
            WHERE LOWER(title) = '{title.lower()}'
                AND duration = '{dur}'
                AND s.sid = p.sid
                AND p.aid = a.aid
                AND a.aid = '{aid}';
            '''
    cursor.execute(query)
    exists = cursor.fetchall()[0][0]
    # number of identical songs is greater than or equal to 1, warn artist
    if exists >= 1:
        ip = int(input('Song already exists! Enter (1) to cancel or (2) to add it as a new song: '))
        if ip == 1:
            print("cancelled")
            return
        elif ip != 2:
            print("Those were none of the options")
            return

    # get a unique sid
    cursor.execute('SELECT MAX(s.sid) FROM songs s;')
    sid = cursor.fetchall()[0][0] + 1

    # add song to songs
    cursor.execute('INSERT INTO songs VALUES(?, ?, ?)', (sid, title, dur))
    conn.commit()

    # gets a list of all artist aids
    all_aid = []
    cursor.execute('SELECT aid FROM artists')
    all_artists = cursor.fetchall()
    for i in range(len(all_artists)):
        all_aid.append(all_artists[i][0])

    # for all artists who performed the song, check if they are in the artists table
    # If yes, add to performs, else ignore and move to next artist in list
    for artist in artists:
        if artist.lower() in all_aid:
            cursor.execute('INSERT INTO perform VALUES(?, ?)', (artist, sid))
            conn.commit()
        else:
            print(artist + ' is not an artist, did not add to performers')
    return


def findTop(cursor, aid):
    '''
    Prints the top 3 users based on total duration spent listening to the artists songs and the
    top 3 playlists based on the number of songs included by the artist.

    Parameters
    ----------
    cursor: connection beftween database and queries
    aid: id of artist logged on
    '''
    # get the uid and total durations of every user who listens to the artists and sort in 
    # descending order by total duration
    user_query = f'''SELECT l.uid, SUM(l.cnt*s.duration)
                FROM listen l, songs s, perform p, artists a
                WHERE l.sid = s.sid 
                    AND s.sid = p.sid
                    AND p.aid = a.aid
                    AND a.aid = '{aid}'
                GROUP BY l.uid, p.aid, s.sid
                ORDER BY SUM(l.cnt*s.duration) DESC'''
    cursor.execute(user_query)
    rows = cursor.fetchall()

    print("top users:")
    print('uid | duration listened')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]))
        except:  # if rows has less than 3 rows, the try will be unable to index and will throw an error
            break

    # get the pid, playlist title, and the number of songs included that were performed by the artist 
    # and sorts in descending order by number of the sartist's included songs
    play_query = f'''SELECT DISTINCT pl.pid, playlists.title, COUNT(*) AS num_songs_by_artist
                FROM songs s, perform p, plinclude pl, playlists
                WHERE playlists.pid = pl.pid
                    AND pl.sid = s.sid
                    AND s.sid = p.sid
                    AND p.aid = '{aid}'
                GROUP BY pl.pid
                ORDER BY COUNT(*) DESC'''
    cursor.execute(play_query)
    rows = cursor.fetchall()

    print("\ntop playlists:")
    print('pid | title | number of songs included by artist')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
        except:
            break

