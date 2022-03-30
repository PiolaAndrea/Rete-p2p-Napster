import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="progettop2p")
    cursor = connection.cursor()

    query = "CREATE TABLE FILE(nome varchar(100), md5 varchar(32), ipP2P varchar(15), pP2P int, nCopie int, PRIMARY KEY (md5, ipP2P))"    #immettere query qui
    cursor.execute(query)
    query = "CREATE TABLE PEER(ipP2P varchar(15), pP2P int, SessionID varchar(16), PRIMARY KEY (ipP2P))"
    cursor.execute(query)
    query = "CREATE TABLE LOG(idLOG SERIAL, ipP2P varchar(15), pP2P int, SessionID varchar(16), operazione varchar(20), data varchar(30), PRIMARY KEY (idLOG))"
    cursor.execute(query)

    connection.commit()     #conferma e salva modifiche sul db
    
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)
finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
