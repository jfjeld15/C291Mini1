def addSong(cursor, aid, conn):
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
        break
    artists = input("Input additional artists (leave blank if none): ").split(";")
    artists.append(aid)

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
    if exists >= 1:
        ip = int(input('Song already exists! Enter (1) to cancel or (2) to add it as a new song: '))
        if ip == 1:
            print("cancelled")
            return
        elif ip != 2:
            print("Those were none of the options")
            return

    cursor.execute('SELECT MAX(s.sid) FROM songs s;')
    sid = cursor.fetchall()[0][0] + 1

    cursor.execute('INSERT INTO songs VALUES(?, ?, ?)', (sid, title, dur))
    conn.commit()

    all_aid = []
    cursor.execute('SELECT aid FROM artists')
    all_artists = cursor.fetchall()
    for i in range(len(all_artists)):
        all_aid.append(all_artists[i][0])

    for artist in artists:
        if artist in all_aid:
            cursor.execute('INSERT INTO perform VALUES(?, ?)', (artist, sid))
            print('yes')
            conn.commit()
    return

def findTop(cursor, aid):
    user_query = f'''select l.uid, sum(l.cnt*s.duration)
                from listen l, songs s, perform p, artists a
                where l.sid=s.sid and s.sid=p.sid and p.aid = a.aid and a.aid = '{aid}'
                group by l.uid, p.aid, s.sid
                ORDER BY SUM(l.cnt*s.duration) DESC'''
    cursor.execute(user_query)
    rows = cursor.fetchall()

    print('uid | duration listened')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]))
        except:
            break

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

    print('pid | title | number of songs included by artist')
    for i in range(3):
        try:
            print(str(rows[i][0]) + ' | ' + str(rows[i][1]) + ' | ' + str(rows[i][2]))
        except:
            break
