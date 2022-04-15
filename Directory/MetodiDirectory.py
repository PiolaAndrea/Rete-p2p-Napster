from datetime import datetime
import random
import string
from ClassDB import *

class MetodiDirectory:

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
        md5 = pacchetto[20:52]
        filename = pacchetto[52:152].strip()
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
        ricerca = pacchetto[20:40].strip()
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
                result = file.split(",")
                listFile.append(result[0])
                listFile.append(result[1])
            idmd5 = len(listResult)
            if len(str(idmd5)) == 2:
                risposta = "AFIN0" + str(idmd5)
            elif len(str(idmd5)) == 1:
                risposta = "AFIN00" + str(idmd5)
            i = 0
            while i < len(listFile):
                md5 = listFile[i]
                filename = listFile[i+1]
                query = "Select * from file where md5 = '%s' AND filename = '%s'" %(md5, filename)
                nCopie = DB.queryDb(query)
                nCopie = str(nCopie)
                while(len(nCopie) < 3):         #riempio gli eventuali bytes mancanti
                    nCopie = "0" + nCopie
                nome = filename
                nome = nome.ljust(100)
                risposta += md5 + nome + nCopie
                query = "Select file.ipP2P, peer.pP2P from file, peer where peer.ipp2p = file.ipp2p AND file.md5 = '%s' AND file.filename = '%s'"%(md5, filename)
                risultati = DB.queryRicerca(query)
                for row in risultati:
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
        ipP2P = pacchetto[52:67]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
            query = []
            query.append("INSERT INTO log (ipp2p, operazione, data) VALUES((Select ipp2p from peer where sessionid = '%s'), 'download', '%s')" %(SessionID, data))
            query.append("Update file set nDownload = nDownload + 1 where md5 = '%s' AND ipp2p = '%s'"%(md5, ipP2P))
            for i in range(len(query)):     #eseguo query in successione
                DB.queryDb(query[i])
            query = ("Select nDownload from file where md5 = '%s' AND ipp2p = '%s'"%(md5, ipP2P))
            nDownload = str(DB.queryRicerca(query))
            caratteriDaSostituire = "[]', "
            for carattere in caratteriDaSostituire:
                nDownload = nDownload.replace(carattere, "")
            while(len(nDownload) < 5):     #riempio gli eventuali bytes mancanti
                nDownload = "0" + nDownload
            risposta = "ARRE" + nDownload
            return risposta
        return 'ERRO'

    def Logout(pacchetto):
        SessionID = pacchetto[4:20]
        query = "select * from peer where sessionid = '%s'" %(SessionID)
        if(DB.queryDb(query) == 1):     #se il sessionid è presente
            query = "Delete from file where ipp2p = (Select ipp2p from peer where sessionid = '%s')" %(SessionID)
            nFileEliminati = str(DB.queryDb(query))     #ritorno numero file Eliminati
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
