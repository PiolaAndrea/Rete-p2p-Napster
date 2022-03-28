import socket
import sys
from random import *

porta = sys.argv[1]
hostname = sys.argv[2]

class Metodi:
    def Login(ip):
            p = randint(50000,52000)
            pacchetto = 'LOGI'+ip+ str(p) 
            return pacchetto
            
    def Logout():
            pacchetto = 1

    def Aggiungi():
            pacchetto = 1

    def Rimuovi():
            pacchetto = 1

    def Ricerca():
            pacchetto = 1

    def download():
            pacchetto = 1

class L_File:
    def __init__(self, nome, md5, ipP2P, pP2P, n_copie):
        self.nome = nome
        self.md5 = md5
        self.ipP2P = ipP2P
        self.pP2P = pP2P
        self.n_copie = n_copie

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
