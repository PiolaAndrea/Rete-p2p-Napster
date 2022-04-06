from fileinput import filename
import socket
import os
import string
import random
from unittest import result
import psycopg2
from datetime import datetime


class L_File:
    def __init__(self, md5, nome, ipP2P, pP2P):
        self.md5 = md5
        self.nome = nome
        self.ipP2P = ipP2P
        self.pP2P = pP2P
    


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
        

class Metodi:

    def Login(pacchetto):
        ipP2P = pacchetto[4:19]
        pP2P = pacchetto[19:24]
        length_of_string = 16
        while True:
            SessionID = ''.join(random.SystemRandom().choice(string.digits) for _ in range(length_of_string))     #genero casualmente
            query = "Select * from peer where sessionid = '%s'"%(SessionID)
            if(DB.queryDb(query) == 0):      #se non è già stato generato quel SessionID
                break
        query = []
        query.append("INSERT INTO peer (ipp2p, pp2p, sessionid) VALUES('%s', '%s', '%s')" %(ipP2P, pP2P, SessionID))
        data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        query.append("INSERT INTO log (ipp2p, pp2p, sessionid, operazione, data) VALUES('%s', '%s', '%s', 'login', '%s')" %(ipP2P, pP2P, SessionID, data))
        for i in range(len(query)):
            if(DB.queryDb(query[i]) != 1):       #se le query danno errori
                SessionID = '0000000000000000'
        risposta = 'ALGI'+SessionID
        return risposta

    def Aggiunta(pacchetto):
        SessionID = pacchetto[4:20]
        #SessionID = '6338084801094733'
        md5 = pacchetto[20:52]
        filename = pacchetto[52:152].replace("|", "")
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = "INSERT INTO log (ipp2p, pp2p, sessionid, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), (Select pp2p from peer where sessionid = '%s'), '%s', 'aggiunta', '%s')" %(SessionID, SessionID, SessionID, data)
            DB.queryDb(query)
            query = "UPDATE file set nome = '%s' where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND md5 = '%s'" %(filename, SessionID, md5)
            if(DB.queryDb(query) == 0):    #se non esiste gia' un file con lo stesso identificativo md5 aggiunto da quel peer
                query = "INSERT INTO file (nome, md5, ipp2p, pp2p) VALUES('%s', '%s', (Select ipp2p from peer where sessionid = '%s'), (Select pp2p from peer where sessionid = '%s'))" %(filename, md5, SessionID, SessionID)
                if(DB.queryDb(query) == 1):    #se è stato inserito correttamente il file nel db
                    query = "Select * from file where md5 = '%s'" %(md5)
                    return str(DB.queryDb(query))    #ritorno numero copie con lo stesso identificativo md5
                else:
                    return 'ERRO'
            else:
                query = "Select * from file where md5 = '%s'" %(md5)
                return str(DB.queryDb(query))         #ritorno numero copie con lo stesso identificativo md5
        else:
            return 'ERRO'

    def Ricerca(pacchetto):
        SessionID = pacchetto[4:20]
        ricerca = pacchetto[20:40].replace("|", "")
        risposta = ""
        #aggiungere controlli sessionID e log
        listFile = []
        query = "Select DISTINCT (md5, nome) from file where nome LIKE '%" + ricerca + "%'"
        listResult = DB.queryRicerca(query)
        for file in listResult:
            print(file)
            result = file.split(",")
            listFile.append(result[0])
            listFile.append(result[1])
        idmd5 = len(listResult)
        if len(str(idmd5)) == 2:
            risposta = "AFIN0" + str(idmd5)
        elif len(str(idmd5)) == 1:
            risposta = "AFIN00" + str(idmd5)
        i = 0
        for stringa in listFile:
            print(stringa)
        """
        while i < (len(listFile)*2):
            md5 = listFile[i]
            print(md5)
            filename = listFile[i+1]
            print(filename)
            query = "Select * from file where md5 = '%s' AND nome = '%s'" %(md5, filename)
            nCopie = DB.queryDb(query)
            nCopie = str(nCopie)
            while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                nCopie = "0" + nCopie
            nome = filename
            while(len(nome) < 100):         #riempio gli eventuali bytes mancanti
                nome = "|" + nome
            risposta += md5 + filename + nCopie
            for j in range(int(nCopie)):
                query = "Select ipP2P, pP2P from file where md5 = '%s' AND nome = '%s'"%(md5, filename)
                risultati = DB.queryRicerca(query)
                for row in risultati:
                    risultato = row.split(",")
                    ipP2P = risultato[0]
                    pP2P = risultato[1]
                risposta += ipP2P+pP2P
            i = i + 2
            """
        return risposta




        """
        pacchetti = []
        if idmd5 > 0:
            idmd5 = str(idmd5)
            while(len(idmd5) < 3):         #riempio gli eventuali bytes mancanti
                idmd5 = "0" + idmd5
            for file in files:
                filename = file.nome
                while(len(filename) < 100):         #riempio gli eventuali bytes mancanti
                    filename = "|" + filename
                query = "Select * from file where md5 = '%s'" %(file.md5)
                nCopie = str(DB.queryDb(query))
                while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                    nCopie = "X" + nCopie
                pacchetti.append('AFIN'+idmd5+file.md5+filename+nCopie+file.ipP2P+file.pP2P)
            return pacchetti
        elif idmd5 == 0:
            idmd5 = "000"
            pacchetti.append('AFIN'+idmd5)
            return pacchetti
        """


    def Rimozione(pacchetto):
        SessionID = pacchetto[4:20]
        md5 = pacchetto[20:52]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = []
            query.append("INSERT INTO log (ipp2p, pp2p, sessionid, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), (Select pp2p from peer where sessionid = '%s'), '%s', 'rimozione', '%s')" %(SessionID, SessionID, SessionID, data))
            query.append("Delete from file where md5 = '%s' AND ipp2p = (Select ipp2p from peer where sessionid = '%s')"%(md5, SessionID))
            for i in range(len(query)):     #eseguo query in successione
                DB.queryDb(query[i])
            query = "Select * from file where md5 = '%s'"%(md5)
            nCopie = str(DB.queryDb(query))      #ritorno numero copie con stesso identificativo md5
            while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                nCopie = "X" + nCopie
            risposta = 'ADEL' + nCopie
            return risposta
        return 'ERRO'
            

    
    def Logout(pacchetto):
        SessionID = pacchetto[4:20]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            query = "Delete from file where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND pp2p = (Select pp2p from peer where sessionid = '%s')" %(SessionID, SessionID)
            nFileEliminati = str(DB.queryDb(query))     #ritorno numero file Eliminati
            query = "Delete from peer where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND pp2p = (Select pp2p from peer where sessionid = '%s')" %(SessionID, SessionID)
            query = []
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query.append("INSERT INTO log (ipp2p, pp2p, sessionid, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), (Select pp2p from peer where sessionid = '%s'), '%s', 'logout', '%s')" %(SessionID, SessionID, SessionID, data))
            query.append("Delete from peer where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND pp2p = (Select pp2p from peer where sessionid = '%s')" %(SessionID, SessionID))
            for i in range(len(query)):    #eseguo query in successione
                DB.queryDb(query[i])
            while(len(nFileEliminati) < 3):     #riempio gli eventuali bytes mancanti
                nFileEliminati = "X" + nFileEliminati
            risposta = 'ALGO' + nFileEliminati
            return risposta
        return 'ERRO'

            
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 80))
    s.listen(10)

    while True:
        conn, addr = s.accept()
        pacchetto = conn.recv(4096).decode()        
        richiesta = pacchetto[0:4]
        print(pacchetto)
        print(richiesta)
        if richiesta == "LOGI":
            risposta = Metodi.Login(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "ADDF":
            nCopie = Metodi.Aggiunta(pacchetto)
            while(len(nCopie) < 3):
                nCopie = "X" + nCopie
            risposta = 'AADD' + nCopie
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "FIND":
            risposta = Metodi.Ricerca(pacchetto)
            print(risposta)
            conn.send(risposta.encode())
            

        elif richiesta == "DELF":
            risposta = Metodi.Rimozione(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "LOGO":
            risposta = Metodi.Logout(pacchetto)
            print(risposta)
            conn.send(risposta.encode())
        conn.close()
