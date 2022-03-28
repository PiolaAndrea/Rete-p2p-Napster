import socket
import os
import string
import random
import psycopg2


class Metodi:
    def Login(pacchetto):
        ipP2P = pacchetto[4:19]
        ipP2P = ipP2P.replace("A", "")    #sostituisco 
        pP2P = int(pacchetto[19:24])
        #query = ""
        #if(DB.queryDb(query)):
        length_of_string = 16
        SessionID = ''.join(random.SystemRandom().choice(string.digits) for _ in range(length_of_string))
        #else:
        #    SessionID = '0000000000000000'
        return SessionID

class DB:
    def queryDb(query):
        try:
            connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="")
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()     #conferma e salva modifiche sul db
            if connection:
                cursor.close()
                connection.close()
                return True
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            if connection:
                cursor.close()
                connection.close()
                return False
            

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 50002))
s.listen(10)

while True:
    conn, addr = s.accept()
    pacchetto = conn.recv(4096).decode()
    richiesta = pacchetto[0:4]
    print(pacchetto)
    print(richiesta)
    if richiesta == "LOGI":
        SessionID = Metodi.Login(pacchetto)
        risposta = 'ALGI' + SessionID
        conn.send(risposta.encode())


    conn.close()
