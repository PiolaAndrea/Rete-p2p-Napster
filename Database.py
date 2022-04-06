import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="progettop2p")
    cursor = connection.cursor()

    query = "CREATE TABLE peer(ipP2P varchar(15), pP2P int, SessionID varchar(16), PRIMARY KEY (ipP2P))"
    cursor.execute(query)
    query = "CREATE TABLE file(filename varchar(100), md5 varchar(32), ipP2P varchar(15), nDownload int, PRIMARY KEY (md5, ipP2P), FOREIGN KEY(ipP2P) references peer(ipP2P))"    
    cursor.execute(query)
    query = "CREATE TABLE log(idLOG SERIAL, ipP2P varchar(15), operazione varchar(20), data varchar(30), PRIMARY KEY (idLOG), FOREIGN KEY(ipP2P) references peer(ipP2P))"
    cursor.execute(query)

    connection.commit()     #conferma e salva modifiche sul db
    
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
