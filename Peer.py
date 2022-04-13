import socket
import sys
import os
from random import *
from MetodiPeer import *
from Utility import *
# -*- coding: utf-8 -*- 

porta = sys.argv[2]
hostname = sys.argv[1]
path = sys.argv[4]
ipIn = sys.argv[3]
sessionId = '0000000000000000'
nomi_File = []
p = 0
for filename in os.listdir(path):
    nomi_File.append(filename)


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
                #print(lenBytes)
                i += 4096
                if(lenBytes <= 4096):
                    conn.send(risposta[i:i+lenBytes])
                    break
        conn.close()

s = openSocketConnection(hostname, porta)    #apro connessione con la socket
pacchetto = MetodiPeer.Login(CalcolaIp(ipIn))
p = pacchetto[19:24]
s.send(pacchetto.encode())
risposta = s.recv(4096).decode()
sessionId = risposta[4:20]
s.close()        #chiudo connessione con la socket
if(risposta[0:4] == "ALGI"):
    if(sessionId == '0000000000000000'):
        print('Errore nel login il programma si chiuderà')
        exit(0)
    else:
        print('Login effettuato con successo, il tuo SessionId è: ', sessionId)
        pid = os.fork()
        if pid == 0:
            FiglioUpload(p)
else:
    print("Ops! Qualcosa è andato storto!") 
    exit(1)   

while True:
    selezione = Menu()

    if(selezione == '1'):
        if(sessionId != '0000000000000000'): 
            nomi_File = []      
            for filename in os.listdir(path):
                nomi_File.append(filename)
                s = openSocketConnection(hostname, porta)     #apro connessione con la socket
                pacchetto = MetodiPeer.Aggiungi(sessionId, filename, path)
                s.send(pacchetto.encode())
                risposta = s.recv(4096).decode()
                n_copie = int(risposta[4:7])
                if(risposta[0:4] == "AADD"):
                    print('Il file %s ha %s copie' %(filename, str(n_copie)))
                else:
                    print("Ops! Qualcosa è andato storto!")   
            s.close()        #chiudo connessione con la socket
        else:
            print("È necessario prima fare il login")

     
    elif(selezione == '2'):
        if(sessionId != '0000000000000000'):   
            nome_File = input('Inserire il nome del file da eliminare: ')    
            if (nome_File in nomi_File):                #CONTROLLARE FILE NON PRESENTI NELLA PROPRIA CARTELLA
                s = openSocketConnection(hostname, porta)     #apro connessione con la socket
                pacchetto = MetodiPeer.Rimuovi(sessionId, nome_File, path)
                s.send(pacchetto.encode())
                risposta = s.recv(4096).decode()
                s.close()        #chiudo connessione con la socket
                n_copie = int(risposta[4:7])
                if(risposta[0:4] == "ADEL"):
                    print('Il file %s ha %s copie nel database' %(nome_File, str(n_copie)))
                else:
                    print("Ops! Qualcosa è andato storto!")

            else:
                print('Non hai messo a disposizione nessun file denominato', nome_File)
        else:
            print("È necessario prima fare il login")


    elif(selezione == '3'):
        if(sessionId != '0000000000000000'):
            files = []
            ricerca = input('Inserire il nome del file da ricercare: ')
            if ricerca != "" and len(ricerca) <= 20:    
                s = openSocketConnection(hostname, porta)     #apro connessione con la socket
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
                if risposta[0:4] == "AFIN":
                    if risposta[4:7] == "000":      #controllo campo idmd5
                        print("La ricerca non ha prodotto risultati")
                    else:
                        files = ScomponiRicerca(risposta)
                    for file in files:
                        print("Nome: %s || Md5: %s || ipP2P: %s || pP2P: %s" %(file.nome, file.md5, file.ipP2P, file.pP2P))
                else:
                    print("Ops! Qualcosa è andato storto!")
            else:
                print("Hai inserito una stringa vuota o troppo lunga")
        else:
            print("È necessario prima fare il login")


    elif(selezione == '4'):  
        if(sessionId != '0000000000000000'):
            md5 = input("Inserire l'Md5 del file da scaricare: ")
            ip = input("Inserire l'indirizzo ip del peer da cui scaricare il file: ")
            port = input("Inserire porta del peer da cui scaricare il file: ")
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                so.connect((ip, int(port)))
                pacchetto = MetodiPeer.Download(md5)
                so.send(pacchetto.encode())
                risposta = bytes(0)
                while True:
                    buffer = so.recv(4096)
                    #print(len(buffer))
                    if not buffer: break 
                    else:
                        risposta += buffer
                        #print(len(risposta))
                if risposta[0:4].decode() == "ARET":
                    while True:
                        filename = input("Come vuoi salvare il file [nome].[estensione]: ")
                        exist = os.path.isfile('%s/%s' %(path,filename))     #inserire path generico
                        if exist:
                            print("Sembra che ci sia già un file con lo stesso nome")
                        else:
                            ScomponiDownload(risposta, filename, path)
                            print("Il file è stato scaricato e salvato correttamente")
                            s = openSocketConnection(hostname, porta)   #collegamento directory
                            ip = CalcolaIp(ip)
                            pacchetto = "RREG" + sessionId + md5 + ip + port          #ip deve essere 15 byte
                            s.send(pacchetto.encode())
                            risposta = s.recv(4096).decode()
                            n_fileScaricati = int(risposta[4:7])
                            if(risposta[0:4] == "ARRE"):
                                print("Questo file è già stato scaricato %s volte" %(str(n_fileScaricati)))
                            else:
                                print("Ops! Qualcosa è andato storto!")
                            s.close()
                            break
                else:
                    print("Ops! Qualcosa è andato storto!")
                so.close()
            except:
                print("Errore nell'inserimento di IP o PORTA")
        else:
            print("È necessario prima fare il login")

    elif(selezione == '5'):
        if(sessionId != '0000000000000000'):
            s = openSocketConnection(hostname, porta) 
            pacchetto = MetodiPeer.Logout(sessionId)
            s.send(pacchetto.encode())
            risposta = s.recv(4096).decode()
            n_file = int(risposta[4:7])
            s.close()
            if risposta[0:4] == "ALGO":
                print('Logout effettuato con successo, sono stati rimossi %s file' %(str(n_file)))
                exit(0)
            else:
                print("Ops! Qualcosa è andato storto!")
        else:
            print("È necessario prima fare il login")
    
    else:
        print("Errore nell' inserimento dell' istruzione")
