    import os
import socket
from random import *
import hashlib

class L_File:
    def __init__(self, md5, nome, ipP2P, pP2P):
        self.md5 = md5
        self.nome = nome
        self.ipP2P = ipP2P
        self.pP2P = pP2P

class Descrittore:
    def __init__(self, md5, nome):
        self.md5 = md5
        self.nome = nome

def Menu():
    print('Menù di scelta:')
    print('1) Aggiunta')
    print('2) Rimozione')
    print('3) Ricerca')
    print('4) Download')
    print('5) Logout')
    return input('Cosa si desidera fare? ')

def CalcolaIp(ipIn):
    split = ipIn.split('.')
    ip = ""
    for i in range (len(split)):
        if len(split[i]) == 2:
            split[i] = '0' + split[i][0] + split[i][1]
        elif len(split[i]) == 1:
            split[i] = '00' + split[i][0]
        ip += split[i]+'.'
    return ip [0:15]

def FindMd5(path,filename):
    file = open('%s/%s' %(path,filename), 'rb')
    contenuto = file.read()
    file.close()
    return str(hashlib.md5(contenuto).hexdigest())

def openSocketConnection(hostname, porta):      
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, int(porta)))
    return s

def ScomponiDownload(pacchetto, filename, path):
    fd = os.open('%s/%s' %(path,filename), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o777)    #inserire path generico
    nChunk = int(pacchetto[4:10].decode())
    i = 10
    for chunk in range(nChunk):
        lenchunk = pacchetto[i:i+5].decode()
        lenchunk = int(lenchunk)
        i+=5          #sposto puntatore dopo la lenchunk
        buffer = pacchetto[i:i+lenchunk]
        os.write(fd, buffer)
        i += lenchunk     #sposto il puntaotre dopo i byte di quel chunk
    os.close(fd)

def ScomponiRicerca(risposta):
    k = 7
    files = []
    for i in range(int(risposta[4:7])):
        md5 = risposta[k:k+32]
        nome = risposta[k+32:k+132].strip()
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
    return files

