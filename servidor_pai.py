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
    # A prompt é sempre a mesma, o diff é basicamente alguma adição na prompt dependendo do comando que foi recebido
    prompt = '>>> '
    diff = ''
    # Fecha o socket automaticamente quando sai do loop
    with socket:
        print(f'Cliente {addr} conectou')
        socket.sendall(bytearray(prompt.encode()))
        while True:
            command = socket.recv(1024)
            # Se o cliente desconectou, command será b''
            if not command:
                print(f'Cliente {addr} encerrou a conexão')
                break
            # Precisamos criptografar ainda, links possivelmente úteis para isso:
            # https://www.ppgia.pucpr.br/~jamhour/Pessoal/Graduacao/Ciencia/SocketsC/sslpython.html
            # https://stackoverflow.com/questions/11027865/python-client-authentication-using-ssl-and-socket
            # https://docs.python.org/3/library/ssl.html
            if command == b'login':
                print(f'Cliente {addr} quer logar!')
                diff = 'Digite seu username: '
                socket.sendall(bytearray((prompt + diff).encode()))
                username = socket.recv(1024).decode('utf-8')
                diff = 'Digite sua senha: '
                socket.sendall(bytearray((prompt + diff).encode()))
                passw = socket.recv(1024).decode('utf-8')
                print(f'Usuário: {username}\nSenha: {passw}')

            socket.sendall(bytearray((prompt).encode()))




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
        self.file = open("./leaderboard.txt", "r+")
    
    def add_user():
        pass

    def update_score(self, usr: str, points_won: int) -> None:
        self.file.seek(os.SEEK_SET)

        new_score = 0
        offset = 0
        index = -1

        lines = self.file.readlines()
        for i in range (len(lines)):
            pos = lines[i].split(" ")
            if (pos[0] == usr):
                new_score = int(pos[1]) + points_won
                index = i
                break
            offset += len(lines[i])
        if (index == -1):
            #Usuário não encontrado na leaderboard
            pass

        #Falta travar o arquivo
        self.file.seek(offset + len(usr) + 1)
        self.file.write("{0:05d}".format(new_score))




main()