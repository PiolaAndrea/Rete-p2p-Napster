import psycopg2

class DB:
    def queryDb(query):
        try:
            rowaffected = -1
            connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="progettop2p")
            cursor = connection.cursor()
            cursor.execute(query)
            rowaffected = cursor.rowcount
            #print(str(rowaffected))
            connection.commit()     #conferma e salva modifiche sul db
            if connection:
                cursor.close()
                connection.close()
                return rowaffected    #ritorno numero righe coinvolte
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            if connection:
                cursor.close()
                connection.close()
                return rowaffected
    
    def queryRicerca(query):
        try:
            dbRow = []
            connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="progettop2p")
            cursor = connection.cursor()
            cursor.execute(query)
            caratteriDaSostituire = "()' "
            for row in cursor.fetchall():
                for carattere in caratteriDaSostituire:
                    row = str(row).replace(carattere, "")
                dbRow.append(row)
            connection.commit()     #conferma e salva modifiche sul db
            if connection:
                cursor.close()
                connection.close()
                return dbRow    #ritorno elenco risultati
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            if connection:
                cursor.close()
                connection.close()
                return dbRow
