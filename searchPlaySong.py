def search(connection,cursor,id):
    #get input
    keyword_list=input("Enter keyword(s): ").split(';')
   

    #make sure there aren't any duplicates
    keyword_sorted=sorted(set(keyword_list))

    #Create a copy 
    keywords=sorted(set(keyword_list))

    #Delete blank entries
    for w in range(len(keyword_sorted)):
        test_word=keyword_sorted[w]
        if len(test_word.strip())==0:
            keywords.remove(keyword_sorted[w])

    query=""

    if keywords:
        #For every word in the list, count the number of occurences in the song and playlist titles
        for i in range(len(keywords)):
            #For key insensitivity
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
    
        # Sum the occurrences together and return an ordered list of songs and playlists 
        query_final="SELECT ROW_NUMBER() OVER(ORDER BY SUM(counter) DESC) AS order_no,ID,title,duration,type FROM("+query+") GROUP BY title"
        cursor.execute(query_final)
        rows=cursor.fetchall()

        if len(rows) == 0:
            print("No matching titles with those keywords")
        else:
            #Get the column names
            name_list=[]
            for i in range(len(cursor.description)):
                desc = cursor.description[i]
                name_list.append(desc[0])
            
            
            #Proceed to print the query to terminal
            get_five(name_list,rows,query_final,cursor,connection,id)
    else:
        print("No keywords were given")


def get_five(name_list,rows,query,cursor,connection,id):
    #Print column names
    col_str=""
    for col in range(len(name_list)):
        col_str+=str(name_list[col]) + ' | '
    print(col_str)
    
    #Initialize necessary variables
    page=1
    end=print_five(rows,page)
    ip=""
    page_flag=True # for page flipping

    #These options will keep appearing unless the songs option is chosen
    while page_flag==True:
        ip=input("Type (P) for Previous Page, (N) for Next Page, (E) to exit, or the order number of the song/playlist you wish to select: ")
       
        #make sure it's case insensitive
        ip=ip.lower()

        #based on user input, perform different actions
        if ip=="n": #Next page

            #Make sure that indices don't go out of bounds
            if (end==len(rows)):
                print("this is the last page")
                pass
            else:
                #Get the next five songs/playlists
                page+=5
                end=print_five(rows,page)
        elif ip=="p": #Previous page
            #Make sure that indices don't go out of bounds
            if (page==1):
                print("this is the first page")
                pass
            else:
                #Define 1 as the minimum page number user can access
                page=max(1,page-5)
                end=print_five(rows,page)
        elif ip=="e": #Exit
            return
        elif (ip.isdigit() and (int(ip)>len(rows) or int(ip)<=0)) or (not ip.isdigit() and ip != "e"):
            #Error checking user input
            print("Those were none of the options")
        else:
            order=int(ip)
            page_flag=False
            #Determine action depending on whether user chose a playlist or a song
            if (rows[order-1][4]=="playlist"):
                #Get the necessary columns
                query_final="SELECT ID,title,duration FROM (" + query + ") WHERE order_no=:ip"
                cursor.execute(query_final,{"ip":order})
                selected_p=cursor.fetchall()

                print(selected_p)
            elif (rows[order-1][4]=="song"):
                #Get the songID
                get_song_id="SELECT ID FROM (" + query + ") WHERE order_no=:ip"
                cursor.execute(get_song_id,{"ip":order})
                s=cursor.fetchall()
                song_id=s[0][0]

                #Proceed to different songOptions
                songOptions(song_id,cursor,connection,id,order,query)

            
def songOptions(song_id,cursor,connection,uid,order,query):
    #Set flag so that songOptions would stop looping after user chooses an action
    option_bool=True
    while option_bool==True:
                song_action=input("Would you like to (1) Listen, (2) See more Information, (3) add it to a playlist or (4) Exit? ")
                
                #Direct user to next options
                if song_action=='1':
                    listen_song(song_id,cursor,connection,uid)
                    option_bool=False
                elif song_action=='2':
                    song_info(order,query,cursor,connection,song_id)
                    option_bool=False
                elif song_action=='3':
                    addPlaylist(song_id,cursor,connection,uid)
                    option_bool=False
                elif song_action=='4':
                    return
                else:
                    print("Those were none of the options")


def print_five(rows,page):
    #Makes sure that indices stay in bounds 
    end=min(page+4,len(rows))

    #Prints a maximum of 5 rows
    for i in range(page-1,end):
        print(str(rows[i][0])+ ' | '+str(rows[i][1])+' | '+rows[i][2]+' | '+str(rows[i][3])+' | '+rows[i][4])
    return end

def listen_song(song_id,cursor,connection,uid):
    #Check if a session is started
    cursor.execute("SELECT * FROM sessions WHERE uid = ? AND `end` IS NULL;", (uid,))

    if len(cursor.fetchall()) == 0:  # A session is not in progress, start one
        # Get new sno
        cursor.execute("SELECT MAX(sno) FROM sessions WHERE uid = ?;", (uid,))
        try:
            sno = cursor.fetchone()[0] + 1  # This will be the session number if a new session is started (Will always be unique)
        except TypeError:
            # a TypeError occurs when fetchone() returns (None,), which is not subscriptable
            sno = 1  # The user has not had any sessions yet
        #Start session
        cursor.execute("INSERT INTO sessions VALUES (?, ?, DATE('now'), NULL);", (uid, sno))
        connection.commit()
        print("Session started.")
    else:
        #get session number (a session is already in progress)
        cursor.execute("SELECT sno FROM sessions WHERE uid=? AND `end` IS NULL", (uid,))
        sno_row=cursor.fetchall()
        sno=sno_row[0][0]

    # Check if user is already listening to the song in this session
    cursor.execute("SELECT * FROM listen WHERE uid = ? AND sid=? AND sno=?;", (uid,song_id,sno))
    
    if len(cursor.fetchall())!=0: #user listened to the song before in this session
        #update count
        update_query='''UPDATE listen 
                        SET cnt=cnt+1 
                        WHERE uid=? AND sid=? AND sno=?'''
        cursor.execute(update_query,(uid,song_id,sno))
        connection.commit()
    else: #first time listening to the song
        #insert into listen
        cursor.execute("INSERT INTO listen VALUES(?,?,?,?)",(uid,sno,song_id,1.0))
        connection.commit()
    print("Listened to song.")
       

def song_info(order,query,cursor,connection,song_id):
    #Get basic info by reusing previous query
    query_final="SELECT ID,title,duration FROM (" + query + ") WHERE order_no=:order"
    cursor.execute(query_final,{"order":order})
    basic_info=cursor.fetchall()
    info_string=str(basic_info[0][0])+ ' | '+str(basic_info[0][1])+' | '+ str(basic_info[0][2])+' | '
    
    #Get the artist(s) that perform the song
    artist_info_query='''SELECT name FROM artists a
                    INNER JOIN perform p
                    ON a.aid=p.aid 
                    INNER JOIN songs s
                    ON s.sid=p.sid 
                    WHERE s.sid=?'''
    cursor.execute(artist_info_query,(song_id,))
    artist_info=cursor.fetchall()

    #Add on to the info_string, code can adjust to more than one artist
    for i in range(len(artist_info)):
        if i==len(artist_info)-1:
            info_string+=str(artist_info[i][0])+ ' | '
        else:
            info_string += str(artist_info[i][0]) + ', '

    #Get which playlists song is in 
    playlist_info_query='''
                        SELECT p.title FROM playlists p 
                        INNER JOIN plinclude pl
                        ON pl.pid=p.pid 
                        INNER JOIN songs s 
                        ON s.sid=pl.sid 
                        WHERE s.sid=?'''
    cursor.execute(playlist_info_query,(song_id,))
    playlist_info=cursor.fetchall()

    #adds on to info_string 
    for i in range(len(playlist_info)):
        if i==len(playlist_info)-1:
            info_string+=str(playlist_info[i][0])+ ' | '
        else:
            info_string += str(playlist_info[i][0]) + ', '
    
    #Output results
    print('SongID'+ ' | ' + 'Duration' + ' | ' + 'Title' + ' | ' + 'Artist(s)' + ' | ' + 'Playlists')
    print(info_string)
    

def addPlaylist(song_id,cursor,connection,uid):
    
    playlistName=input("Enter playlist name: ")
    # Check if playlist exists
    cursor.execute("SELECT * FROM playlists WHERE LOWER(title) =? AND uid=?",(playlistName.lower(),uid))
    
    if (len(cursor.fetchall())==0):
        #playlist does not exist
        #Get the largest pid and add 1 to ensure that it's unique
        cursor.execute("SELECT MAX(pid) FROM playlists")
        pid_row=cursor.fetchall()
        pid=pid_row[0][0]+1

        #Insert new playlist
        insert_p='''INSERT INTO playlists VALUES(?,?,?)'''
        cursor.execute(insert_p,(pid,playlistName,uid,))
        s_order=1
        connection.commit()
    else:
        #playlist exists
        #Get existing pid to update data
        cursor.execute("SELECT pid FROM playlists WHERE LOWER(title) =? AND uid=?",(playlistName.lower(),uid))
        pid_row=cursor.fetchall()
        pid=pid_row[0][0]

        #Get the largest sorder and add 1 to ensure uniqueness
        cursor.execute("SELECT MAX(sorder) FROM plinclude WHERE pid=?",(pid,))
        s_order_row=cursor.fetchall()
        s_order=s_order_row[0][0]+1

    insertpl='''
        INSERT INTO plinclude VALUES (?, ?, ?)'''
    try:
        cursor.execute(insertpl,(pid,song_id,s_order,))
        print("Song inserted into playlist.")
    except:
        print("Song is already in playlist")
    connection.commit()
       
    
