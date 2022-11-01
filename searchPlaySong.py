def search(connection,cursor,id):
    keyword_list=input("Enter keyword: ").split(';')
    keywords=sorted(set(keyword_list))
    query=""
    for i in range(len(keywords)):
        keyword=keywords[i].lower()
        query+=f'''
            
            SELECT ID,title, duration, (LENGTH(title)-LENGTH(REPLACE(LOWER(title), '{keyword}', '')))/LENGTH('{keyword}') AS counter,type
        FROM (
            SELECT pl.pid AS 'ID',p.title,SUM(s.duration) AS 'duration','playlist' AS 'type'
            FROM plinclude pl
            INNER JOIN songs s 
            ON s.sid=pl.sid
            INNER JOIN playlists p 
            ON pl.pid=p.pid
            WHERE LOWER(p.title) LIKE '%{keyword}%'
            GROUP BY pl.pid

            UNION 

            SELECT s.sid AS 'ID' ,s.title,s.duration,'song' AS 'type' 
            FROM songs s 
            WHERE LOWER(s.title) LIKE '%{keyword}%'
        )
        '''
        if (i!=len(keywords)-1):
            query+="UNION"
    query_final="SELECT ROW_NUMBER() OVER(ORDER BY SUM(counter) DESC) AS order_no,ID,title,duration,type FROM("+query+") GROUP BY title"

    cursor.execute(query_final)
    name_list=[]
    for i in range(len(cursor.description)):
        desc = cursor.description[i]
        name_list.append(desc[0])
    rows=cursor.fetchall()
    
    get_five(name_list,rows,query_final,cursor,connection,id)


def get_five(name_list,rows,query,cursor,connection,id):
    print(name_list)
    page=1
    end=print_five(rows,page)
    ip=""
    page_flag=True # for page flipping
    while page_flag==True:
        ip=input("P/N/number: ")
        if ip=="N":
            if (end==len(rows)):
                print("this is the last page")
                pass
            else:
                page+=5
                end=print_five(rows,page)
        elif ip=="P":
            if (page==1):
                print("this is the first page")
                pass
            else:
                page=max(1,page-5)
                end=print_five(rows,page)
        elif ip.isdigit() and int(ip)>len(rows) or int(ip)<=0:
            print("those were none of the options")
        else:
            order=int(ip)
            page_flag=False
            
            if (rows[order-1][4]=="playlist"):
                query_final="SELECT ID,title,duration FROM (" + query + ") WHERE order_no=:ip"
                cursor.execute(query_final,{"ip":order})
                selected_p=cursor.fetchall()
                print(selected_p)
            elif (rows[order-1][4]=="song"):
                option_bool=True
                get_song_id="SELECT ID FROM (" + query + ") WHERE order_no=:ip"
                cursor.execute(get_song_id,{"ip":order})
                s=cursor.fetchall()
                song_id=s[0][0]
                
                while option_bool==True:
                    song_action=input("Would you like to (1) Listen, (2) See more Information, or (3) add it to a playlist? ")
                    if song_action=='1':
                        listen_song(song_id,cursor,connection,id)
                        option_bool==False
                    elif song_action=='2':
                        song_info(order,query,cursor,connection,song_id)
                        option_bool==False
                    elif song_action=='3':
                        addPlaylist(song_id,cursor,connection,id)
                        option_bool==False
                    else:
                        print("Those were none of the options")
            
                  

def print_five(rows,page):
    end=min(page+4,len(rows))
    for i in range(page-1,end):
        print(str(rows[i][0])+ ' | '+str(rows[i][1])+' | '+rows[i][2]+' | '+str(rows[i][3])+' | '+rows[i][4])
    return end

def listen_song(song_id,cursor,connection,uid):
    #Check if a session is started
    cursor.execute("SELECT * FROM sessions WHERE uid = ? AND `end` IS NULL;", (uid,))

    if len(cursor.fetchall()) != 0:  # A session is in progress
       
        # Check if user is already listening to the song
        cursor.execute("SELECT * FROM listen WHERE uid = ? AND sid=?;", (uid,song_id))
       
        if len(cursor.fetchall())!=0: #user listened to the song before
            #update count
            update_query='''UPDATE listen 
                            SET cnt=cnt+1 
                            WHERE uid=? AND sid=?'''
            cursor.execute(update_query,(uid,song_id))
            connection.commit()
        else: #first time listening to the song

            #get session number
            cursor.execute("SELECT sno FROM sessions WHERE uid=? AND `end` IS NULL", (uid,))
            sno_row=cursor.fetchall()
            sno=sno_row[0][0]

            #insert into listen
            cursor.execute("INSERT INTO listen VALUES(?,?,?,?)",(uid,sno,song_id,1.0))
            connection.commit()

    else: #A session is not in progress
        # Get new sno
        cursor.execute("SELECT MAX(sno) FROM sessions WHERE uid= ?",(uid,))
        sno_row=cursor.fetchall()
        sno=sno_row[0][0]+1

        #Start session
        cursor.execute("INSERT INTO sessions VALUES (?, ?, DATE('now'), NULL);", (uid, sno))
        connection.commit()
       

def song_info(order,query,cursor,connection,song_id):
    query_final="SELECT ID,title,duration FROM (" + query + ") WHERE order_no=:order"
    cursor.execute(query_final,{"order":order})

    basic_info=cursor.fetchall()

    info_string=str(basic_info[0][0])+ ' | '+str(basic_info[0][1])+' | '+ str(basic_info[0][2])+' | '
    artist_info_query='''SELECT name FROM artists a
                    INNER JOIN perform p
                    ON a.aid=p.aid 
                    INNER JOIN songs s
                    ON s.sid=p.sid 
                    WHERE s.sid=?'''
    cursor.execute(artist_info_query,(song_id,))
    artist_info=cursor.fetchall()

    for i in range(len(artist_info)):
        if i==len(artist_info)-1:
            info_string+=str(artist_info[i][0])+ ' | '
        else:
            info_string += str(artist_info[i][0]) + ', '

    playlist_info_query='''
                        SELECT p.title FROM playlists p 
                        INNER JOIN plinclude pl
                        ON pl.pid=p.pid 
                        INNER JOIN songs s 
                        ON s.sid=pl.sid 
                        WHERE s.sid=?'''
    cursor.execute(playlist_info_query,(song_id,))
    playlist_info=cursor.fetchall()

    for i in range(len(playlist_info)):
        if i==len(playlist_info)-1:
            info_string+=str(playlist_info[i][0])+ ' | '
        else:
            info_string += str(playlist_info[i][0]) + ', '
    print('SongID'+ ' | ' + 'Duration' + ' | ' + 'Title' + ' | ' + 'Artist(s)' + ' | ' + 'Playlists')
    print(info_string)
    

def addPlaylist(song_id,cursor,connection,uid):
    playlistName=input("Enter playlist name: ")
    # Check if playlist exists
    cursor.execute("SELECT * FROM playlists WHERE title =? AND uid=?",(playlistName,uid))
    
    if (len(cursor.fetchall())==0):
        #playlist does not exist
        cursor.execute("SELECT MAX(pid) FROM playlists")
        pid_row=cursor.fetchall()
        pid=pid_row[0][0]+1
        insert_p='''INSERT INTO playlists VALUES(?,?,?)'''
        cursor.execute(insert_p,(pid,playlistName,uid,))
        s_order=1
        connection.commit()
    else:
        #playlist exists
        cursor.execute("SELECT pid FROM playlists WHERE title =? AND uid=?",(playlistName,uid))
        pid_row=cursor.fetchall()
        pid=pid_row[0][0]
        cursor.execute("SELECT MAX(sorder) FROM plinclude WHERE pid=?",(pid,))
        s_order_row=cursor.fetchall()
        s_order=s_order_row[0][0]+1

    insertpl='''
        INSERT INTO plinclude VALUES (?, ?, ?)'''
    cursor.execute(insertpl,(pid,song_id,s_order,))
    connection.commit()
       
    
