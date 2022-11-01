import searchPlaySong 

def search(connection, cursor, uid):
    keywords = input('Please input keywords to search by: ').split(';')

    query = '''SELECT DISTINCT 
                out.name, out.nation, out.cnt_song AS 'number of songs'
            FROM (SELECT COUNT(*) AS cnt_keyword, params.name AS name, params.nation AS nation, params.cnt_song
                FROM ('''
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
    query += ''' ) AS params
            GROUP BY params.name
            ) AS out
            ORDER BY out.cnt_keyword DESC
            '''

    cursor.execute(query)
    name_list = cursor.description
    rows = cursor.fetchall()
    
    get_five(name_list, rows, cursor, connection, uid)


def get_five(name_list, rows, cursor, connection, uid):
    print('order no | ' + str(name_list[0][0]) + ' | ' + str(name_list[1][0]) + ' | ' + str(name_list[2][0]))
    page = 1
    end = print_five(rows, page)
    flag = True
    while flag == True:
        ip = input("P/N/number: ").lower()
        if ip == "n":
            if (end == len(rows)):
                print("this is the last page")
                pass
            else:
                page += 5
                end = print_five(rows,page)
        elif ip == "p":
            if (page == 1):
                print("this is the first page")
                pass
            else:
                page = max(1, page-5)
                end = print_five(rows,page)
        elif ip.isdigit() and int(ip)>len(rows) or int(ip)<=0:
            print("those were none of the options")
        else:
            flag = False
            printArtistInfo(cursor, connection, uid, ip, rows)

def print_five(rows, page):
    end = min(page + 4, len(rows))
    for i in range(page-1, end):
        print(str(i+1) + ' | '+ str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
    return end

def printArtistInfo(cursor, connection, uid, ip, rows):
    ip = int(ip)
    get_aid = f"SELECT aid FROM artists WHERE name = '{rows[ip-1][0]}'"
    cursor.execute(get_aid)
    aid = cursor.fetchall()
    
    query = f'''SELECT s.sid, s.title, s.duration 
            FROM songs s, perform p, artists a
            WHERE a.aid = '{aid[0][0]}'
                AND a.aid = p.aid
                AND p.sid = s.sid'''
    cursor.execute(query)
    rows = cursor.fetchall()

    col_list = cursor.description
    print('order no | ' + str(col_list[0][0]) + ' | ' + str(col_list[1][0]) + ' | ' + str(col_list[2][0]))
    for i in range(len(rows)):
        print(str(i+1) + ' | ' + str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
    
    ip = input("E/number: ").lower()
    if ip != 'e':
        ip = int(ip)
        get_sid = f"SELECT sid FROM songs WHERE title = '{rows[ip-1][1]}'"
        cursor.execute(get_sid)
        sid = cursor.fetchall()

        songActions(sid[0][0], cursor, connection, uid)

def songActions(song_id, cursor, connection, uid):
    song_action = input("Would you like to (1) Listen, (2) See more Information, or (3) add it to a playlist? ")
    if song_action=='1':
        searchPlaySong.listen_song(song_id, cursor, connection, uid)
    elif song_action=='2':
        song_info(cursor, connection, song_id)
    elif song_action=='3':
        addPlaylist(song_id, cursor, connection, uid)
    else:
        print("Those were none of the options")

def song_info(cursor, connection, song_id):
    query_final = f"SELECT sid, title, duration FROM songs WHERE sid = {song_id}"
    cursor.execute(query_final)

    basic_info = cursor.fetchall()

    info_string = str(basic_info[0][0]) + ' | ' + str(basic_info[0][1]) + ' | ' + str(basic_info[0][2]) + ' | '
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
    playlistName = input("Enter playlist name: ")
    # Check if playlist exists
    cursor.execute("SELECT * FROM playlists WHERE title = ? AND uid = ?", (playlistName, uid))
    
    if (len(cursor.fetchall()) == 0):
        #playlist does not exist
        cursor.execute("SELECT MAX(pid) FROM playlists")
        pid_row = cursor.fetchall()
        pid = pid_row[0][0] + 1
        insert_p = '''INSERT INTO playlists VALUES(?,?,?)'''
        cursor.execute(insert_p, (pid, playlistName, uid,))
        s_order = 1
        connection.commit()
    else:
        #playlist exists
        cursor.execute("SELECT pid FROM playlists WHERE title = ? AND uid = ?", (playlistName, uid))
        pid_row = cursor.fetchall()
        pid = pid_row[0][0]
        cursor.execute("SELECT MAX(sorder) FROM plinclude WHERE pid = ?", (pid,))
        s_order_row = cursor.fetchall()
        s_order = s_order_row[0][0] + 1

    insertpl = '''INSERT INTO plinclude VALUES (?, ?, ?)'''
    cursor.execute(insertpl, (pid, song_id, s_order,))
    connection.commit()