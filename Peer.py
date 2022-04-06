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

def Menu():
    print('Menù di scelta:')
    print('1) Login')
    print('2) Aggiunta')
    print('3) Rimozione')
    print('4) Ricerca')
    print('5) Download')
    print('6) Logout')
    return input('Cosa si desidera fare? ')

class Metodi:
    def Login(ip):
            p = randint(50001,52000)
            pacchetto = 'LOGI'+ip+ str(p) 
            return pacchetto

    def Aggiungi(sessionId, filename, path):   
            file = open('%s/%s' %(path,filename), 'rb')
            contenuto = file.read()
            md5 = str(hashlib.md5(contenuto).hexdigest())
            lunghezza = len(filename)
            for i in range (100-lunghezza):
                filename = '|' + filename
            return ('ADDF'+sessionId+md5+filename)

    def Rimuovi(sessionId, nomeFile):
            file = open('%s/%s' %(path,nomeFile), 'rb')
            contenuto = file.read()
            md5 = str(hashlib.md5(contenuto).hexdigest())
            pacchetto = 'DELF' + sessionId + md5
            return pacchetto

    def Ricerca(sessionId, ricerca):
            lunghezza = len(ricerca)
            for i in range (20-lunghezza):
                ricerca = '|' + ricerca
            pacchetto = 'FIND' + sessionId + ricerca
            return pacchetto

    def Download():
            pacchetto = 1

    def Upload(md5):
            pacchetto = 1

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
    ipIn = '104.152.104.112'#s.getsockname()[0]
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
                    print(risposta)
                    k = 7
                    for i in range(int(risposta[4:7])):
                        file = L_File("","","","")
                        file.md5 = risposta[k:k+32]
                        file.nome = risposta[k+32:k+132].replace("|", "")
                        y = 142
                        for j in range(int(risposta[k+132:k+135])):
                            file.ipP2P = risposta[y:y+15]
                            file.pP2P = risposta[y+15:y+20]
                            y += 20
                            files.append(file)
                        k+=y
                for file in files:
                    print("Nome: %s || Md5: %s || ipP2P: %s || pP2P: %s" %(file.nome, file.md5, file.ipP2P, file.pP2P))
            else:
                print("Hai inserito una stringa vuota o troppo lunga")
        else:
            print("È necessario prima fare il login")


    elif(selezione == '5'):
        a=0

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
