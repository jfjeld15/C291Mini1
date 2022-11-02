import searchPlaySong

def search(connection, cursor, uid):
    '''
    Searches through the database for songs and artist names that contain the inputted keywords.

    Parameters
    ----------
    connection: connection to the database
    cursor: connection beftween database and queries
    uid: id of user logged in
    '''
    keywords = input('Please input keywords to search by: ')
    if keywords.strip() == "":
        return
    else:
        keywords = keywords.split(";")

    # return name, nationality, and number of songs of artist
    query = '''SELECT DISTINCT out.name, out.nation, out.cnt_song AS 'number of songs'
            FROM (SELECT COUNT(*) AS cnt_keyword, params.name AS name, params.nation AS nation, params.cnt_song
                FROM ('''
    # for every keyword, get the name, nationality, and number of songs where the keyword is present
    # if a song's title or an artist's name has the keyword in it
    for word in keywords:
        query += f'''SELECT a.name AS name, a.nationality AS nation, count.s_num AS cnt_song 
                FROM artists a, songs s, perform p, (SELECT a.aid, COUNT(DISTINCT s.sid) AS s_num 
                    FROM artists a, songs s, perform p 
                    WHERE s.sid = p.sid 
                        AND p.aid = a.aid
                    GROUP BY a.aid) AS count
                 WHERE (a.name LIKE '%{word}%' OR s.title LIKE '%{word}%')
                     AND s.sid = p.sid 
                     AND p.aid = a.aid
                     AND count.aid = a.aid'''
        if word != keywords[-1]:
            query += '\nUNION ALL\n'
    # order by number of keyword occurences
    query += ''' ) AS params
            GROUP BY params.name) AS out
            ORDER BY out.cnt_keyword DESC  
            '''
    cursor.execute(query)
    name_list = cursor.description
    rows = cursor.fetchall()
    
    get_five(name_list, rows, cursor, connection, uid)


def get_five(name_list, rows, cursor, connection, uid):
    '''
    Keeps track of the pages and number of rows to display. Prints errors when attempting
    to view pages that are not within range.

    Parameters
    ----------
    name_list: column names of selected artist information
    rows: all the rows returning selected artist information
    cursor: connection beftween database and queries
    connection: connection to the database
    uid: id of user logged in
    '''
    # print the column names
    print('order no | ' + str(name_list[0][0]) + ' | ' + str(name_list[1][0]) + ' | ' + str(name_list[2][0]))
    page = 1  # row number to start print from (ie page=1 will print rows 1-5)
    end = print_five(rows, page)

    while True:
        ip = input("Type (P) for Previous Page, (N) for Next Page, (E) to exit, or the order no of the artist you wish to select: ").lower()
        if ip == "n":  # print next page by printing rows (page+5) to (page+10)
            if (end == len(rows)):
                print("this is the last page")
            else:
                page += 5
                end = print_five(rows, page)
        elif ip == "p":  # print previous page by printing rows (page-5) to page
            if (page == 1):
                print("this is the first page")
            else:
                page = max(1, page-5)
                end = print_five(rows,page)
        elif ip=="e": #Exit
            return
        elif (ip.isdigit() and (int(ip)>len(rows) or int(ip)<=0)) or (not ip.isdigit() and ip != "e"):
            print("those were none of the options")
        else:
            printSongInfo(cursor, connection, uid, ip, rows)  # see artist info
            break


def print_five(rows, page):
    '''
    Prints 5 rows of the table.

    Parameters
    ----------
    rows: all the rows in the table
    page: row number to start printing from

    Returns
    -------
    end: 
    '''
    end = min(page + 4, len(rows))  # check whether we'll hit the end of the table or the end of the page
    for i in range(page-1, end):
        print(str(i+1) + ' | '+ str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
    return end


def printSongInfo(cursor, connection, uid, ip, rows):
    '''
    Prints information about songs performed by the selected artist.

    Parameters
    ----------
    cursor: connection beftween database and queries
    connection: connection to the database
    uid: id of user logged in
    ip: row number of the selected artist
    rows: all the rows returning selected artist information
    '''
    # get the artist id of the selected artist from its row number
    ip = int(ip)
    get_aid = f"SELECT aid FROM artists WHERE name = '{rows[ip-1][0]}'"
    cursor.execute(get_aid)
    aid = cursor.fetchall()
    
    # get the song ids, titles, and durations of all songs by the selected artist
    query = f'''SELECT s.sid, s.title, s.duration 
            FROM songs s, perform p, artists a
            WHERE a.aid = '{aid[0][0]}'
                AND a.aid = p.aid
                AND p.sid = s.sid'''
    cursor.execute(query)
    rows = cursor.fetchall()

    # print the column names and rows for the artist's song information
    col_list = cursor.description
    print('order no | ' + str(col_list[0][0]) + ' | ' + str(col_list[1][0]) + ' | ' + str(col_list[2][0]))
    for i in range(len(rows)):
        print(str(i+1) + ' | ' + str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
    
    ip = input("Type (E) to exit or order no of the song you wish to select: ").lower()
    if (ip.isdigit() and (int(ip)>len(rows) or int(ip)<=0)) or (not ip.isdigit() and ip != "e"):
        #Error checking user input
        print("Those were none of the options, returning to user menu")
        return
    elif ip.isnumeric():
        ip = int(ip)
        # get the song id of the user selected song from the row/order number
        get_sid = f"SELECT sid FROM songs WHERE title = '{rows[ip-1][1]}'"
        cursor.execute(get_sid)
        sid = cursor.fetchall()

        songActions(sid[0][0], cursor, connection, uid)


def songActions(song_id, cursor, connection, uid):
    '''
    Takes in input for user song actions and executes actions.

    Parameters
    ----------
    song_id: id of song selected
    cursor: connection beftween database and queries
    connection: connection to the database
    uid: id of user logged in
    '''
    song_action = input("Would you like to (1) Listen, (2) See more Information, or (3) add it to a playlist? ")
    if song_action=='1':
        searchPlaySong.listen_song(song_id, cursor, connection, uid)
    elif song_action=='2':
        song_info(cursor, song_id)
    elif song_action=='3':
        addPlaylist(song_id, cursor, connection, uid)
    else:
        print("Those were none of the options")

def song_info(cursor, song_id):
    '''
    Displays information about the selected song.

    Parameters
    ----------
    cursor: connection beftween database and queries
    song_id: id of song selected
    '''
    # get sid, title, duration
    query = f"SELECT sid, title, duration FROM songs WHERE sid = {song_id}"
    cursor.execute(query)
    basic_info = cursor.fetchall()
    info_string = str(basic_info[0][0]) + ' | ' + str(basic_info[0][1]) + ' | ' + str(basic_info[0][2]) + ' | '

    # get artist name
    artist_info_query = f'''SELECT name FROM artists a
                        INNER JOIN perform p
                            ON a.aid = p.aid 
                        INNER JOIN songs s
                            ON s.sid = p.sid 
                        WHERE s.sid = {song_id}'''
    cursor.execute(artist_info_query)
    artist_info=cursor.fetchall()
    for i in range(len(artist_info)):
        if i == len(artist_info) - 1:
            info_string += str(artist_info[i][0])+ ' | '
        else:
            info_string += str(artist_info[i][0]) + ', '

    # get title of playlists
    playlist_info_query = f'''SELECT p.title FROM playlists p 
                        INNER JOIN plinclude pl
                            ON pl.pid = p.pid 
                        INNER JOIN songs s 
                            ON s.sid = pl.sid 
                        WHERE s.sid = {song_id}'''
    cursor.execute(playlist_info_query)
    playlist_info = cursor.fetchall()
    for i in range(len(playlist_info)):
        if i == len(playlist_info) - 1:
            info_string += str(playlist_info[i][0])+ ' | '
        else:
            info_string += str(playlist_info[i][0]) + ', '
    
    print('SongID'+ ' | ' + 'Duration' + ' | ' + 'Title' + ' | ' + 'Artist(s)' + ' | ' + 'Playlists')
    print(info_string)


def addPlaylist(song_id,cursor,connection,uid):
    '''
    Displays information about the selected song.

    Parameters
    ----------
    song_id: id of song selected
    cursor: connection beftween database and queries
    connection: connection to the database
    uid: id of the user logged in
    '''
    playlistName = input("Enter playlist name: ")
    # Check if playlist exists
    cursor.execute("SELECT * FROM playlists WHERE title = ? AND uid = ?", (playlistName, uid))
    
    # playlist does not exist, initialize new playlist
    if (len(cursor.fetchall()) == 0):
        cursor.execute("SELECT MAX(pid) FROM playlists")
        pid_row = cursor.fetchall()
        pid = pid_row[0][0] + 1
        insert_p = '''INSERT INTO playlists VALUES(?,?,?)'''
        cursor.execute(insert_p, (pid, playlistName, uid,))
        s_order = 1
        connection.commit()

    # playlist exists, get playlist id and order number to insert at
    else:
        cursor.execute("SELECT pid FROM playlists WHERE title = ? AND uid = ?", (playlistName, uid))
        pid_row = cursor.fetchall()
        pid = pid_row[0][0]
        cursor.execute("SELECT MAX(sorder) FROM plinclude WHERE pid = ?", (pid,))
        s_order_row = cursor.fetchall()
        s_order = s_order_row[0][0] + 1

    # insert song playlist
    insertpl = '''INSERT INTO plinclude VALUES (?, ?, ?)'''
    try:
        cursor.execute(insertpl,(pid,song_id,s_order,))
        print("Song inserted into playlist.")
    except:
        print("Song is already in playlist")
    connection.commit()
