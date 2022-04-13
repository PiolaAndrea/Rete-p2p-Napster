import socket
from MetodiDirectory import *

            
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 80))
    s.listen(10)

    while True:
        conn, addr = s.accept()
        pacchetto = conn.recv(4096).decode()        
        richiesta = pacchetto[0:4]
        print(pacchetto)
        print(richiesta)
        if richiesta == "LOGI":
            risposta = MetodiDirectory.Login(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "ADDF":
            risposta = MetodiDirectory.Aggiunta(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "FIND":
            risposta = MetodiDirectory.Ricerca(pacchetto)
            print(risposta)
            conn.send(risposta.encode())
            
        elif richiesta == "DELF":
            risposta = MetodiDirectory.Rimozione(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "RREG":
            risposta = MetodiDirectory.Download(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        elif richiesta == "LOGO":
            risposta = MetodiDirectory.Logout(pacchetto)
            print(risposta)
            conn.send(risposta.encode())

        else:
            risposta = "ERRO"
            print(risposta)
            conn.send(risposta.encode())
        conn.close()

