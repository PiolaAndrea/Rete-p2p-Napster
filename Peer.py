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
files = []

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
    ipIn = '126.152.135.123'#s.getsockname()[0]
    split = ipIn.split('.')
    ip = ""
    for i in range (len(split)):
        if len(split[i]) == 2:
            split[i] = '0' + split[i][0] + split[i][1]
        elif len(split[i]) == 1:
            split[i] = '00' + split[i][0]
        ip += split[i]+'.'
    return ip [0:15]


def openSocketConnection():      
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, int(porta)))
    return s

while True:
    selezione = Menu()

    if(selezione == '1'):
        if(sessionId == '0000000000000000'):
            s = openSocketConnection()    #apro connessione con la socket
            pacchetto = Metodi.Login(CalcolaIp())
            s.send(pacchetto.encode())
            risposta = s.recv(20).decode()[0:20]
            identificativo = risposta[0:4]
            sessionId = risposta[4:20]
            if(identificativo == 'ALGI'):  
                if(sessionId == '0000000000000000'):
                    print('Errore nel login si prega di riprovare')
                else:
                    print('Login effettuato con successo, il tuo SessionId è: ', sessionId)
            else: print("Errore di trasmissione con il server")
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
                risposta = s.recv(7).decode()[0:7]
                n_copie = risposta[4:7].replace("X", "")
                identificativo = risposta[0:4]
                if(identificativo == 'AADD'):
                    print('Il file %s ha %s copie' %(filename, n_copie))
                else: print("Errore di trasmissione con il server")
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
                risposta = s.recv(7).decode()[0:7]
                identificativo = risposta[0:4]
                n_copie = risposta[4:7].replace("X", "")
                if(identificativo == 'ADEL'):
                    print('Il file %s ha %s copie nel database' %(nome_File, n_copie))
                else: print("Errore di trasmissione con il server")
                s.close()        #chiudo connessione con la socket
            else:
                print('Non hai messo a disposizione nessun file denominato', nome_File)
        else:
            print("È necessario prima fare il login")


    elif(selezione == '4'):
        if(sessionId != '0000000000000000'):
            ricerca = input('Inserire il nome del file da ricercare: ')
            if ricerca != "" and len(ricerca) <= 20:    
                s = openSocketConnection()     #apro connessione con la socket
                pacchetto = Metodi.Ricerca(sessionId, ricerca)
                s.send(pacchetto.encode())
                risposte = []
                while True:
                    buffer = s.recv(162)
                    if not buffer: break 
                    else:
                        risposte.append(buffer.decode()) 
                s.close()        #chiudo connessione con la socket

                identificativo = buffer.decode()[0:4]
                if(identificativo == 'AFIN'):
                    if risposte[0][4:7] == "000":      #controllo campo idmd5
                        print("La ricerca non ha prodotto risultati")
                    else:
                        files = []
                        for i in range (len(risposte)):
                            files.append(L_File(risposte[i][7:39], risposte[i][39:139].replace("|", ""), risposte[i][142:157], risposte[i][157:162]))
                        print("La ricerca ha prodotto questi risultati:")
                        for i in range (len(files)):
                            print("Nome: %s || Md5: %s || ipP2P: %s || pP2P: %s" %(files[i].nome, files[i].md5, files[i].ipP2P, files[i].pP2P))
                else: print("Errore di trasmissione con il server")
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
            risposta = s.recv(7).decode()[0:7]
            identificativo = risposta[0:4]
            n_file = risposta[4:7].replace('X','')
            if(identificativo == 'ALGO'):
                print('Logout effettuato con successo, sono stati rimossi %s file' %(n_file))
            else: print("Errore di trasmissione con il server")
            s.close()
            exit(0)
        else:
            print("È necessario prima fare il login")
    
    else:
        print("Errore nell' inserimento dell' istruzione")
