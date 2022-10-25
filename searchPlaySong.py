def search(connection,cursor):
    keywords=input("Enter keyword: ").split(';')
    query=""
    for i in range(len(keywords)):
        keyword=keywords[i]
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

    #print(query_final)
    cursor.execute(query_final)
    name_list=[]
    for i in range(len(cursor.description)):
        desc = cursor.description[i]
        name_list.append(desc[0])
    rows=cursor.fetchall()
    
    get_five(name_list,rows,query_final,cursor,connection)


def get_five(name_list,rows,query,cursor,connection):
    print(name_list)
    page=1
    end=print_five(rows,page)
    ip="Y"
    flag=True
    while flag==True:
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
        else:
            flag==False
            ip=int(ip)
            if (rows[ip-1][4]=="playlist"):
                query_final="SELECT ID,title,duration FROM (" + query + ") WHERE order_no=:ip"
                
                cursor.execute(query_final,{"ip":ip})
                rows=cursor.fetchall()
                print(rows)

def print_five(rows,page):
    end=min(page+4,len(rows))
    for i in range(page-1,end):
        print(str(rows[i][0])+ ' | '+str(rows[i][1])+' | '+rows[i][2]+' | '+str(rows[i][3])+' | '+rows[i][4])
    return end