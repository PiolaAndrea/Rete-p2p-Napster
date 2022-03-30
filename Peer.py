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
            p = randint(50000,52000)
            pacchetto = 'LOGI'+ip+ str(p) 
            return pacchetto

    def Aggiungi(sessionId, filename):   
            file = open('%s/%s' %(path,filename), 'rb')
            contenuto = file.read()
            md5 = str(hashlib.md5(contenuto).digest())
            lunghezza = len(filename)
            for i in range (100-lunghezza):
                filename = 'Z' + filename
            return ('AADF'+sessionId+md5+filename)

    def Rimuovi(sessionId, md5):
            pacchetto = 'DELF' + sessionId + md5
            return pacchetto

    def Ricerca():
            pacchetto = 1

    def Download():
            pacchetto = 1

    def Logout(sessionId):
            pacchetto = 'LOGO' + sessionId
            return pacchetto

class L_File:
    def __init__(self, nome, md5, ipP2P, pP2P, n_copie):
        self.nome = nome
        self.md5 = md5
        self.ipP2P = ipP2P
        self.pP2P = pP2P
        self.n_copie = n_copie

def CalcolaIp():
    ipIn = '1.1.1.8'#s.getsockname()[0]
    split = ipIn.split('.')
    ip = ""
    for i in range (len(split)):
        if len(split[i]) == 2:
            split[i] = 'A' + split[i][0] + split[i][1]
        elif len(split[i]) == 1:
            split[i] = 'AA' + split[i][0]
        ip += split[i]+'.'
    return ip [0:15]

while True:
    selezione = Menu()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, int(porta)))

    if(selezione == '1'):
        pacchetto = Metodi.Login(CalcolaIp())
        s.send(pacchetto.encode())
        sessionId = s.recv(4096).decode()[4:20]
        if(sessionId == '0000000000000000'):
            print('Errore nel login si prega di riprovare')
        else:
            print('Login effettuato con successo, il tuo SessioId è: ', sessionId)

    elif(selezione == '2'):       
        for filename in os.listdir(path):
            pacchetto = Metodi.Aggiungi(sessionId, filename)
            print(pacchetto)
            s.send(pacchetto.encode())
            n_copie = s.recv(4096).decode()[4:7]
            print('Il file %s ha %s copie' %(filename, n_copie))

            
    elif(selezione == '3'):
        a=0

    elif(selezione == '4'):
        a=0

    elif(selezione == '5'):
        a=0

    elif(selezione == '6'):
        a=0

    s.close()

def CalcolaIp():
    ipIn = '1.1.1.1'
    split = ipIn.split('.')
    ip = ""
    for i in range (len(split)):
        if len(split[i]) == 2:
            split[i] = 'A' + split[i][0] + split[i][1]
        elif len(split[i]) == 1:
            split[i] = 'AA' + split[i][0]
        ip += split[i]+'.'
    return ip [0:15]

pacchetto = Metodi.Login(CalcolaIp())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((hostname, int(porta)))
s.send(pacchetto.encode())
risposta = s.recv(4096).decode()
print(risposta)
s.close()
