import socket
import os
import string
import random
import psycopg2
from datetime import datetime



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
        query.append("INSERT INTO log (ipp2p, operazione, data) VALUES('%s', 'login', '%s')" %(ipP2P, data))
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
            query = "INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'aggiunta', '%s')" %(SessionID, data)
            DB.queryDb(query)
            query = "UPDATE file set filename = '%s' where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND md5 = '%s'" %(filename, SessionID, md5)
            if(DB.queryDb(query) == 0):    #se non esiste gia' un file con lo stesso identificativo md5 aggiunto da quel peer
                query = "INSERT INTO file (filename, md5, ipp2p, nDownload) VALUES('%s', '%s', (Select ipp2p from peer where sessionid = '%s'), 0)" %(filename, md5, SessionID)
                if(DB.queryDb(query) == 1):    #se è stato inserito correttamente il file nel db
                    query = "Select * from file where md5 = '%s'" %(md5)
                    nCopie = str(DB.queryDb(query))    #ritorno numero copie con lo stesso identificativo md5
                    while(len(nCopie) < 3):
                        nCopie = "0" + nCopie
                    risposta = "AADD" + nCopie
                    return risposta
                else:
                    return 'ERRO'
            else:
                query = "Select * from file where md5 = '%s'" %(md5)
                nCopie = str(DB.queryDb(query))    #ritorno numero copie con lo stesso identificativo md5
                while(len(nCopie) < 3):
                    nCopie = "0" + nCopie
                risposta = "AADD" + nCopie
                return risposta
        else:
            return 'ERRO'

    def Ricerca(pacchetto):
        SessionID = pacchetto[4:20]
        ricerca = pacchetto[20:40].replace("|", "")
        risposta = ""
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = "INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'ricerca', '%s')" %(SessionID, data)
            DB.queryDb(query)
            listFile = []
            query = "Select DISTINCT (md5, filename) from file where filename LIKE '%" + ricerca + "%'"
            listResult = DB.queryRicerca(query)
            for file in listResult:
                #print(file)
                result = file.split(",")
                listFile.append(result[0])
                listFile.append(result[1])
            idmd5 = len(listResult)
            if len(str(idmd5)) == 2:
                risposta = "AFIN0" + str(idmd5)
            elif len(str(idmd5)) == 1:
                risposta = "AFIN00" + str(idmd5)
            i = 0
            #print(len(listFile))
            while i < len(listFile):
                md5 = listFile[i]
                #print(md5)
                filename = listFile[i+1]
                #print(filename)
                query = "Select * from file where md5 = '%s' AND filename = '%s'" %(md5, filename)
                nCopie = DB.queryDb(query)
                nCopie = str(nCopie)
                while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                    nCopie = "0" + nCopie
                nome = filename
                while(len(nome) < 100):         #riempio gli eventuali bytes mancanti
                    nome = "|" + nome
                risposta += md5 + nome + nCopie
                query = "Select file.ipP2P, peer.pP2P from file, peer where peer.ipp2p = file.ipp2p AND file.md5 = '%s' AND file.filename = '%s'"%(md5, filename)
                #print(query)
                risultati = DB.queryRicerca(query)
                for row in risultati:
                    #print(row)
                    risultato = row.split(",")
                    ipP2P = risultato[0]
                    pP2P = risultato[1]
                    risposta += ipP2P+pP2P
                i = i+2
            return risposta
        return "ERRO"


    def Rimozione(pacchetto):
        SessionID = pacchetto[4:20]
        md5 = pacchetto[20:52]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = []
            query.append("INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'rimozione', '%s')" %(SessionID, data))
            query.append("Delete from file where md5 = '%s' AND ipp2p = (Select ipp2p from peer where sessionid = '%s')"%(md5, SessionID))
            for i in range(len(query)):     #eseguo query in successione
                DB.queryDb(query[i])
            query = "Select * from file where md5 = '%s'"%(md5)
            nCopie = str(DB.queryDb(query))      #ritorno numero copie con stesso identificativo md5
            while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                nCopie = "0" + nCopie
            risposta = 'ADEL' + nCopie
            return risposta
        return 'ERRO'
            
    def Download(pacchetto):
        SessionID = pacchetto[4:20]
        md5 = pacchetto[20:52]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = []
            query.append("INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'download', '%s')" %(SessionID, data))
            query.append("Update file set nDownload = nDownload + 1 where md5 = '%s' AND ipp2p = (Select ipp2p from peer where sessionid = '%s')"%(md5, SessionID))
            for i in range(len(query)):     #eseguo query in successione
                DB.queryDb(query[i])
            query = ("Select nDownload from file where md5 = '%s' AND ipp2p = (Select ipp2p from peer where sessionid = '%s')"%(md5, SessionID))
            nDownload = str(DB.queryRicerca(query))
            risposta = "ARRE" + nDownload
        return 'ERRO'

    def Logout(pacchetto):
        SessionID = pacchetto[4:20]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            query = "Delete from file where ipp2p = (Select ipp2p from peer where sessionid = '%s')" %(SessionID)
            nFileEliminati = str(DB.queryDb(query))     #ritorno numero file Eliminati
            #query = "Delete from peer where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND pp2p = (Select pp2p from peer where sessionid = '%s')" %(SessionID, SessionID)
            query = []
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query.append("INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'logout', '%s')" %(SessionID, data))
            query.append("Delete from peer where ipp2p = (Select ipp2p from peer where sessionid = '%s') AND pp2p = (Select pp2p from peer where sessionid = '%s')" %(SessionID, SessionID))
            for i in range(len(query)):    #eseguo query in successione
                DB.queryDb(query[i])
            while(len(nFileEliminati) < 3):     #riempio gli eventuali bytes mancanti
                nFileEliminati = "0" + nFileEliminati
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
            risposta = Metodi.Aggiunta(pacchetto)
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

        elif richiesta == "RREG":
            risposta = Metodi.Download(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "LOGO":
            risposta = Metodi.Logout(pacchetto)
            print(risposta)
            conn.send(risposta.encode())
        conn.close()
