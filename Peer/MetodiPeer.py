import hashlib
from random import *
from Utility import *


class MetodiPeer:
    def Login(ip):
        p = randint(50001,52000)
        pacchetto = 'LOGI'+ip+ str(p) 
        return pacchetto

    def Aggiungi(sessionId, filename, path):   
        md5 = FindMd5(path,filename)
        filename.ljust(100)
        return ('ADDF'+sessionId+md5+filename)

    def Rimuovi(sessionId, nomeFile, path):
        file = open('%s/%s' %(path,nomeFile), 'rb')
        contenuto = file.read()
        file.close()
        md5 = str(hashlib.md5(contenuto).hexdigest())
        pacchetto = 'DELF' + sessionId + md5
        return pacchetto

    def Ricerca(sessionId, ricerca):
        ricerca.ljust(20)
        pacchetto = 'FIND' + sessionId + ricerca
        return pacchetto

    def Download(md5):
        pacchetto = "RETR" + md5
        return pacchetto

    def Upload(md5, path):
        listMd5 = []
        nomi_File = []
        pacchetto = ("ARET").encode()
        try:
            for filename in os.listdir(path):
                nomi_File.append(filename)
            for filename in nomi_File:
                listMd5.append(FindMd5(path, filename))   
            indice = listMd5.index(md5)   #cerco indice nella lista
            file = open('%s/%s' %(path,nomi_File[indice]), 'rb')
            contenuto = file.read()
            file.close()
            modulo = len(contenuto) % 4096   #per capire numero di chunk
            if modulo > 0:
                nChunk = int((len(contenuto)/4096)) + 1
            else:
                nChunk = int(len(contenuto)/4096)
            while (len(str(nChunk))) < 6:
                nChunk = "0" + str(nChunk)
            pacchetto += nChunk.encode()
            lenChunk = []
            chunk = []
            lunghezzaContenuto = len(contenuto)
            nChunk = int(nChunk)
            if(nChunk == 1):
                while(len(str(lunghezzaContenuto)) < 5):     #riempio gli eventuali bytes mancanti
                    lunghezzaContenuto = "0" + str(lunghezzaContenuto)
                lenChunk.append(lunghezzaContenuto)
                chunk.append(contenuto)
            else: 
                ultimoChunk = lunghezzaContenuto % 4096    #calcolo lunghezza ultimo chunk
                while(len(str(ultimoChunk)) < 5):     #riempio gli eventuali bytes mancanti
                    ultimoChunk = "0" + str(ultimoChunk)
                i = 0
                for c in range(nChunk-1):
                    lenChunk.append("04096")
                    chunk.append(contenuto[i:i+4096])
                    i += 4096
                lenChunk.append(ultimoChunk)
                chunk.append(contenuto[i:i+int(ultimoChunk)])
            for j in range(len(chunk)):
                pacchetto += lenChunk[j].encode() + chunk[j]
            return pacchetto
        except:
            return 'ERRO'
        
    def Logout(sessionId):
            pacchetto = 'LOGO' + sessionId
            return pacchetto
