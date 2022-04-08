import socket
import sys
import os
from random import *
import hashlib
from metodiPeer import *
# -*- coding: utf-8 -*- 


porta = sys.argv[2]
hostname = sys.argv[1]
path = sys.argv[3]
sessionId = '0000000000000000'
nomi_File = []
p = 0
for filename in os.listdir(path):
    nomi_File.append(filename)

def Menu():
    print('Menù di scelta:')
    print('1) Login')
    print('2) Aggiunta')
    print('3) Rimozione')
    print('4) Ricerca')
    print('5) Download')
    print('6) Logout')
    return input('Cosa si desidera fare? ')




class L_File:
    def __init__(self, md5, nome, ipP2P, pP2P):
        self.md5 = md5
        self.nome = nome
        self.ipP2P = ipP2P
        self.pP2P = pP2P

def CalcolaIp():
    ipIn = '222.222.222.387'#s.getsockname()[0]
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


def ScomponiDownload(pacchetto):
    #print(len(pacchetto))
    fd = os.open("fittizio.jpg", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o777)
    nChunk = int(pacchetto[4:10].decode())
    #print(nChunk)
    i = 10
    for chunk in range(nChunk):
        lenchunk = pacchetto[i:i+5].decode()
        lenchunk = int(lenchunk)
        #print(lenchunk)
        i+=5          #sposto puntatore dopo la lenchunk
        buffer = pacchetto[i:i+lenchunk]
        os.write(fd, buffer)
        i += lenchunk     #sposto il puntaotre dopo i byte di quel chunk
    os.close(fd)


def FiglioUpload(p):
    sFiglio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sFiglio.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sFiglio.bind(("", int(p)))
    sFiglio.listen(10)
    while True:
        conn, addr = sFiglio.accept()
        pacchetto = conn.recv(36).decode()
        #print(pacchetto)
        if pacchetto[0:4] == "RETR":
            fileMd5 = pacchetto[4:36]
            risposta = MetodiPeer.Upload(fileMd5, path, nomi_File)
            #risposta = risposta.encode()
            #print(sys.getsizeof(risposta))
            #conn.sendall(risposta)
            
            i = 0
            lenBytes = len(risposta)
            while True:
                conn.send(risposta[i:i+4096])
                lenBytes -= 4096
                print(lenBytes)
                i += 4096
                if(lenBytes <= 4096):
                    conn.send(risposta[i:i+lenBytes])
                    break
            
        conn.close()
        

while True:
    selezione = Menu()

    if(selezione == '1'):
        if(sessionId == '0000000000000000'):
            s = openSocketConnection()    #apro connessione con la socket
            pacchetto = MetodiPeer.Login(CalcolaIp())
            p = pacchetto[19:24]
            s.send(pacchetto.encode())
            sessionId = s.recv(4096).decode()[4:20]
            s.close()        #chiudo connessione con la socket
            if(sessionId == '0000000000000000'):
                print('Errore nel login si prega di riprovare')
            else:
                print('Login effettuato con successo, il tuo SessionId è: ', sessionId)
                pid = os.fork()
                
                if pid == 0:
                    FiglioUpload(p)
                #t = Thread(target= FiglioUpload, args=(p,))
                #t.start()
            #s.close()        #chiudo connessione con la socket
        else:
            print('Login già effettuato')

    elif(selezione == '2'):
        if(sessionId != '0000000000000000'): 
            nomi_File = []      
            for filename in os.listdir(path):
                nomi_File.append(filename)
                s = openSocketConnection()     #apro connessione con la socket
                pacchetto = MetodiPeer.Aggiungi(sessionId, filename, path)
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
                pacchetto = MetodiPeer.Rimuovi(sessionId, nome_File, path)
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
                pacchetto = MetodiPeer.Ricerca(sessionId, ricerca)
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
            md5 = input("Inserire l'Md5 del file da scaricare: ")
            ip = input("Inserire l'indirizzo ip del peer da cui scaricare il file: ")
            port = input("Inserire porta del peer da cui scaricare il file: ")
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print(ip)
            #print(port)
            so.connect((ip, int(port)))
            pacchetto = "RETR" + md5
            so.send(pacchetto.encode())
            risposta = bytes(0)
            while True:
                buffer = so.recv(4096)
                print(len(buffer))
                if not buffer: break 
                else:
                    risposta += buffer
                    #print(len(risposta))
            ScomponiDownload(risposta)
            #print(risposta)
            so.close()
        else:
            print("È necessario prima fare il login")

    elif(selezione == '6'):
        if(sessionId != '0000000000000000'):
            s = openSocketConnection() 
            pacchetto = MetodiPeer.Logout(sessionId)
            s.send(pacchetto.encode())
            n_file = s.recv(4096).decode()[4:7].replace('X','')
            print('Logout effettuato con successo, sono stati rimossi %s file' %(n_file))
            s.close()
            exit(0)
        else:
            print("È necessario prima fare il login")
    
    else:
        print("Errore nell' inserimento dell' istruzione")
