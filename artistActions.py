def addSong(cursor, aid):
    title = input("Input song title: ").lower()
    dur = input("Input song duration: ")

    query = f'''SELECT COUNT(*) 
            FROM songs s, perform p, artists a
            WHERE LOWER(title) = '{title}'
                AND duration = '{dur}'
                AND s.sid = p.sid
                AND p.aid = a.aid
                AND a.aid = '{aid}'
            '''
    cursor.execute(query)
    exists = cursor.fetchall()[0][0]

    if exists >= 1:
        ip = int(input('Song already exists! Enter (1) to cancel or (2) to add it as a new song: '))
        if ip == 1:
            print("cancelled")
        elif ip == 2:
            cursor.execute('INSERT INTO songs VALUES(?, ?, ?)', (aid, title, dur))
        else:
            print("Those were none of the options")
    else:
        cursor.execute('INSERT INTO songs VALUES(?, ?, ?)', (aid, title, dur))

def findTop(cursor, aid):
    user_query = f'''SELECT DISTINCT l.uid, SUM(l.cnt*s.duration) AS total_duration
                FROM songs s, listen l, perform p, artists a
                WHERE l.sid == s.sid
                    AND s.sid = p.sid
                    AND p.aid = '{aid}'
                GROUP BY l.uid
                ORDER BY SUM(l.cnt*s.duration) DESC'''
    cursor.execute(user_query)
    rows = cursor.fetchall()

    print('uid | duration listened')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]))
        except:
            break

    play_query = f'''SELECT DISTINCT pl.pid, playlists.title, SUM(pl.sid) AS num_songs_by_artist
                FROM songs s, perform p, artists a, plinclude pl, playlists
                WHERE playlists.pid = pl.pid
                    AND pl.sid == s.sid
                    AND s.sid = p.sid
                    AND p.aid = '{aid}'
                GROUP BY pl.pid
                ORDER BY SUM(pl.sid) DESC'''
    cursor.execute(play_query)
    rows = cursor.fetchall()

    print('pid | title | number of songs included by artist')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
        except:
            break