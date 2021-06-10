#!/usr/bin/python3

import socket
import sys
import threading
import time
import os
from typing import List

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

    def end_game(self, addr1: str, username1: str, addr2: str, username2: str, winner: int) -> None:
        """Winner = 0 | 1 | 2, indicando qual player ganhou a partida (0 para empate)"""

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

"""Por enquanto, o formato do arquivo leaderboard será:
username1 pontuacao1
username2 pontuacao2
username3 pontuacao3
username4 pontuacao4

De forma que as entradas estejam ordenadas por pontuacaoN

pontuacaoN terá tamanho fixado? Com 5 dígitos, a leaderboard só explodiria ao passar
de 99999 pontos, que equivale a pelo menos 50000 partidas

"""
class Leaderboard:
    def __init__(self):
        try:
            self.file = open("./leaderboard.txt", "r+")
        except FileNotFoundError:
            self.file = open("./leaderboard.txt", "w+")
        self.leaderboard = self.get_leaderboard()
        self.sort_leaderboard()

    def get_leaderboard(self) -> List:
        leaderboard = []
        self.file.seek(0, os.SEEK_SET)
        for line in self.file:
            list_line = line.split(" ")
            ldb_entry = (list_line[0], int(list_line[1]))
            leaderboard.append(ldb_entry)

        leaderboard = dict(leaderboard)
        return leaderboard
            
    def add_user(self, usr: str) -> None:
        self.file.seek(0, os.SEEK_END)

        entry = usr + " " + ("0"*5) + "\n"
        self.file.write(entry)

    def update_score(self, usr: str, points_won: int) -> None:
        if (not usr in self.leaderboard):
            print("Usuário não encontrado na leaderboard")
            return
        new_score = self.get_score(usr) + points_won

        self.leaderboard[usr] = new_score
        self.sort_leaderboard()
        self.__update_score_on_file(usr, new_score)

    def __update_score_on_file(self, usr: str, new_score: int) -> None:
        self.file.seek(0, os.SEEK_SET)

        offset = 0

        for line in self.file:
            pos = line.split(" ")
            offset += len(pos[0]) + 1
            if (pos[0] == usr):
                #Falta travar o arquivo (6 = 5 zeros + 1 \n)
                self.file.seek(offset, os.SEEK_SET)
                self.file.write("{0:05d}".format(new_score))
                break
            offset += 5 + 1

    def get_score(self, usr: str) -> int:
        return self.leaderboard[usr]

    def sort_leaderboard(self) -> None:
        self.leaderboard = dict(sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True))

    def get_formatted_leaderboard(self) -> str:
        ldb_str = ""
        i = 1
        for user in self.leaderboard:
            ldb_str += str(i) + ". " + user + ": " + str(self.leaderboard[user]) + " pontos\n"
            i += 1
        return ldb_str

main()