#!/usr/bin/python3

from os import O_APPEND
import socket
import sys
import threading
import time

#Vou fazer arquivo dos connected_users

def main():

    if (len(sys.argv) != 2):
        print("Execução: " + sys.argv[0] + " [port]")
        exit(1)
    
    PORT = int(sys.argv[1])

    global listen_th

    listen_th = threading.Thread(target=listener_thread_function, args=(PORT,))
    listen_th.start()

    print("(Main Thread) Vou morrer, fui")

        

def listener_thread_function(PORT):
    
    HOST = ''

    #Tratar erros depois

    #Listening socket, TCP
    s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s_listen.bind((HOST, PORT))
    s_listen.listen()

    threads = list()
    

    while(True):
        #Dessa forma, o server pai fica travado a espera de novas conexões
        #Talvez eu deva paralelizar, e manter um processo armazenando tabelas e afins
        conn, addr = s_listen.accept()

        t = threading.Thread(target=Funcao_do_Lolo, args=(conn, addr,))
        threads.append(t)
        t.start()


#Connected user tem que ser adicionado aqui, pois é aqui dentro que será feita a autenticação
def Funcao_do_Lolo(socket, addr):
    print("Conectou pora ", addr)
    


    pass


class Log:
    def __init__(self):
        self.file = open("./log.txt", "a")

    def log_entry(self, entry: str) -> None:
        self.file.write(self.get_moment() + entry)

    def get_moment(self) -> str:
        current_time = time.localtime()
        return time.strftime("[%Y-%m-%d: %H:%M:%S] ", current_time)

    def init_server(self, sucess: bool) -> None:
        entry = "Servidor iniciado. "
        if (sucess):
            entry += "A última execução foi finalizada com sucesso\n"
        else:
            entry += "A última execução foi finalizada com uma falha\n"
        self.log_entry(entry)
    
    def client_connected(self, addr: str) -> None:
        entry = "Cliente de endereço IP " + addr + " conectado\n"
        self.log_entry(entry)

    def login_attempt(self, username: str, addr: str, sucess: bool) -> None:
        if (sucess):
            entry = "Login bem sucedido do "
        else:
            entry = "Tentativa de login mal sucedido no "
        entry += "usuário " + username + ", no endereço IP " + addr + "\n"
        self.log_entry(entry)

    def client_disconnected(self, addr: str) -> None:
        entry = "Cliente de endereço IP " + addr + " desconectado\n"
        self.log_entry(entry)

    def start_game(self, addr1: str, username1: str, addr2: str, username2: str) -> None:
        entry = "Partida iniciada entre os jogadores " + \
        username1 + "(" + addr1 + ")" + " e " + username2 + "(" + addr2 + ")\n"
        self.log_entry(entry)

    #Winner = 0 | 1 | 2, indicando qual player ganhou a partida (0 para empate)
    def end_game(self, addr1: str, username1: str, addr2: str, username2: str, winner: int) -> None:
        entry = "Partida encerrada entre os jogadores " + \
        username1 + "(" + addr1 + ")" + " e " + username2 + "(" + addr2 + "). "
        if (winner == 1):
            entry += "Vencedor: " + username1 + "\n"
        elif (winner == 2):
            entry += "Vencedor: " +  username2 + "\n"
        elif (winner == 0):
            entry += "A partida terminou empatada\n"

        self.log_entry(entry)

    def unexepected_disconnection(self, addr: str) -> None:
        entry = "Cliente de endereço IP " + addr + " desconectado de forma inesperada\n"
        self.log_entry(entry)

    def terminate_server(self) -> None:
        entry = "Servidor finalizado\n"
        self.log_entry(entry)




main()