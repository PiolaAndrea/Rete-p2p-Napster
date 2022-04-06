import socket
import sys
import os
from random import *
import hashlib
# -*- coding: utf-8 -*- 

porta = sys.argv[2]
hostname = sys.argv[1]
path = sys.argv[3]
sessionId = '0000000000000000'
nomi_File = []
p = 0
grandChunk = []

def Menu():
    print('Menù di scelta:')
    print('1) Login')
    print('2) Aggiunta')
    print('3) Rimozione')
    print('4) Ricerca')
    print('5) Download')
    print('6) Logout')
    return input('Cosa si desidera fare? ')

def FindMd5(filename):
    file = open('%s/%s' %(path,filename), 'rb')
    contenuto = file.read()
    file.close()
    return str(hashlib.md5(contenuto).hexdigest())

class Metodi:
    def Login(ip):
        p = randint(50001,52000)
        pacchetto = 'LOGI'+ip+ str(p) 
        return pacchetto

    def Aggiungi(sessionId, filename, path):   
        md5 = FindMd5(filename)
        lunghezza = len(filename)
        for i in range (100-lunghezza):
            filename = '|' + filename
        return ('ADDF'+sessionId+md5+filename)

    def Rimuovi(sessionId, nomeFile):
        file = open('%s/%s' %(path,nomeFile), 'rb')
        contenuto = file.read()
        file.close()
        md5 = str(hashlib.md5(contenuto).hexdigest())
        pacchetto = 'DELF' + sessionId + md5
        return pacchetto

    def Ricerca(sessionId, ricerca):
        lunghezza = len(ricerca)
        for i in range (20-lunghezza):
            ricerca = '|' + ricerca
        pacchetto = 'FIND' + sessionId + ricerca
        return pacchetto

    def Download(md5):
        pacchetto = "RETR" + md5
        return pacchetto

    def Upload(md5):
        listMd5 = []
        pacchetto = "ARET"
        for file in nomi_File:
            listMd5.append(FindMd5(file))
        indice = listMd5.index(md5)
        file = open('%s/%s' %(path,nomi_File[indice]), 'rb')
        contenuto = file.read()
        file.close()
        modulo = len(contenuto) % 4096
        if modulo > 0:
            nChunk = int((len(contenuto)/4096)) + 1
        else:
            nChunk = int(len(contenuto)/4096)
        pacchetto += str(nChunk)
        chunk = []
        i = 0
        lunghezzaContenuto = len(contenuto)
        while lunghezzaContenuto-4096 > 0:
            chunk.append(contenuto[i:i+4096])
            i += 4096
            lunghezzaContenuto -= 4096
            grandChunk.append("04096")
        chunk.append(contenuto)
        grandChunk.append(str(lunghezzaContenuto))
        for j in range(len(chunk)):
            pacchetto += grandChunk[j] + str(chunk[j]) 
        return pacchetto

    def Logout(sessionId):
            pacchetto = 'LOGO' + sessionId
            return pacchetto

class L_File:
    def __init__(self, md5, nome, ipP2P, pP2P):
        self.md5 = md5
        self.nome = nome
        self.ipP2P = ipP2P
        self.pP2P = pP2P

def CalcolaIp():
    ipIn = '025.040.036.128'#s.getsockname()[0]
    split = ipIn.split('.')
    ip = ""
    for i in range (len(split)):
        if len(split[i]) == 2:
            split[i] = 'A' + split[i][0] + split[i][1]
        elif len(split[i]) == 1:
            split[i] = 'AA' + split[i][0]
        ip += split[i]+'.'
    return ip [0:15]


def openSocketConnection():      
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, int(porta)))
    return s

def FiglioUpload():
    sFiglio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sFiglio.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sFiglio.bind(("", p))
    sFiglio.listen(10)
    while True:
        conn = sFiglio.accept()
        pacchetto = conn.recv(36).decode()
        if pacchetto[0:4] == "RETR":
            fileMd5 = pacchetto[4:36]
            Metodi.Upload(fileMd5)
            sFiglio.close()
        
def ScomponiRicerca(files,risposta):
    k = 7
    for i in range(int(risposta[4:7])):
        md5 = risposta[k:k+32]
        nome = risposta[k+32:k+132].replace("|", "")
        y = k + 132
        z = y + 3
        for j in range(int(risposta[y:y+3])):    #mantengo y separata dalle altre variabili per non cambiare l'intestazione in fase di iterazione
            ipP2P = risposta[z:z+15]
            pP2P = risposta[z+15:z+20]
            z += 20
            file = L_File(md5, nome, ipP2P, pP2P)
            files.append(file)
        y = z      #sposto puntatore su ultimo carattere considerato
        k = y

while True:
    selezione = Menu()

    if(selezione == '1'):
        if(sessionId == '0000000000000000'):
            s = openSocketConnection()    #apro connessione con la socket
            pacchetto = Metodi.Login(CalcolaIp())
            s.send(pacchetto.encode())
            sessionId = s.recv(4096).decode()[4:20]
            if(sessionId == '0000000000000000'):
                print('Errore nel login si prega di riprovare')
            else:
                print('Login effettuato con successo, il tuo SessionId è: ', sessionId)
                pid = os.fork()
                if pid == 0:
                    FiglioUpload()
            s.close()        #chiudo connessione con la socket
        else:
            print('Login già effettuato')

    elif(selezione == '2'):
        if(sessionId != '0000000000000000'):       
            for filename in os.listdir(path):
                nomi_File.append(filename)
                s = openSocketConnection()     #apro connessione con la socket
                pacchetto = Metodi.Aggiungi(sessionId, filename, path)
                s.send(pacchetto.encode())
                n_copie = s.recv(4096).decode()[4:7].replace("X", "")
                print('Il file %s ha %s copie' %(filename, n_copie))
            s.close()        #chiudo connessione con la socket
        else:
            print("È necessario prima fare il login")

     
    elif(selezione == '3'):
        if(sessionId != '0000000000000000'):   
            nome_File = input('Inserire il nome del file da eliminare: ')    
            if (nome_File in nomi_File):                #CONTROLLARE FILE NON PRESENTI NELLA PROPRIA CARTELLA
                s = openSocketConnection()     #apro connessione con la socket
                pacchetto = Metodi.Rimuovi(sessionId, nome_File)
                s.send(pacchetto.encode())
                n_copie = s.recv(4096).decode()[4:7].replace("X", "")
                print('Il file %s ha %s copie nel database' %(nome_File, n_copie))
                s.close()        #chiudo connessione con la socket
            else:
                print('Non hai messo a disposizione nessun file denominato', nome_File)
        else:
            print("È necessario prima fare il login")


    elif(selezione == '4'):
        if(sessionId != '0000000000000000'):
            files = []
            ricerca = input('Inserire il nome del file da ricercare: ')
            if ricerca != "" and len(ricerca) <= 20:    
                s = openSocketConnection()     #apro connessione con la socket
                pacchetto = Metodi.Ricerca(sessionId, ricerca)
                s.send(pacchetto.encode())
                risposta = bytes(0)
                while True:
                    buffer = s.recv(4096)
                    if not buffer: break 
                    else:
                        risposta += buffer
                risposta = risposta.decode()
                s.close()        #chiudo connessione con la socket
                if risposta[4:7] == "000":      #controllo campo idmd5
                    print("La ricerca non ha prodotto risultati")
                else:
                    #print(risposta)
                    ScomponiRicerca(files, risposta)
                for file in files:
                    print("Nome: %s || Md5: %s || ipP2P: %s || pP2P: %s" %(file.nome, file.md5, file.ipP2P, file.pP2P))
            else:
                print("Hai inserito una stringa vuota o troppo lunga")
        else:
            print("È necessario prima fare il login")


    elif(selezione == '5'):  
        if(sessionId != '0000000000000000'):
            md5 = input("Inserire l'Md5 del file da scaricare")
            ip = input("Inserire l'indirizzo ip del peer da cui scaricare il file")
            port = input("Inserire porta del peer da cui scaricare il file")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            pacchetto = "RETR" + md5
            s.send(pacchetto.encode())
            risposta = bytes(0)
            while True:
                buffer = s.recv(4096)
                if not buffer: break 
                else:
                    risposta += buffer
            risposta = risposta.decode()
            print(risposta)
        else:
            print("È necessario prima fare il login")

    elif(selezione == '6'):
        if(sessionId != '0000000000000000'):
            s = openSocketConnection() 
            pacchetto = Metodi.Logout(sessionId)
            s.send(pacchetto.encode())
            n_file = s.recv(4096).decode()[4:7].replace('X','')
            print('Logout effettuato con successo, sono stati rimossi %s file' %(n_file))
            s.close()
            exit(0)
        else:
            print("È necessario prima fare il login")
    
    else:
        print("Errore nell' inserimento dell' istruzione")
