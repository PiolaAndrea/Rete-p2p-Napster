import socket
import os
import string
import random
import psycopg2
from datetime import datetime

class DB:
    def queryDb(query):
        try:
            connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="progettop2p")
            cursor = connection.cursor()
            for i in range(len(query)):
                cursor.execute(query[i])
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

class Metodi:
    def Login(pacchetto):
        ipP2P = pacchetto[4:19]
        ipP2P = ipP2P.replace("A", "")    #sostituisco 
        pP2P = pacchetto[19:24]
        length_of_string = 16
        SessionID = ''.join(random.SystemRandom().choice(string.digits) for _ in range(length_of_string))
        query = []
        query.append("INSERT INTO peer (ipp2p, pp2p, sessionid) VALUES('%s', '%s', '%s')" %(ipP2P, pP2P, SessionID))
        data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        query.append("INSERT INTO log (ipp2p, pp2p, sessionid, operazione, data) VALUES('%s', '%s', '%s', 'login', '%s')" %(ipP2P, pP2P, SessionID, data))
        if(DB.queryDb(query) != True):
            SessionID = '0000000000000000'
        return SessionID

    def Aggiunta(pacchetto):
        SessionID = pacchetto[4:20]
        print(SessionID)
        md5 = pacchetto[20:36]
        print(md5)
        filename = pacchetto[36:136].replace("Z", "")
        print(filename)
        return '005'




            

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 50000))
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
    elif richiesta == "ADDF":
        nCopie = Metodi.Aggiunta(pacchetto)
        risposta = 'AADD' + nCopie
