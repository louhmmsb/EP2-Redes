#!/usr/bin/python3

import ssl
import socket
import sys
import threading
import time
import os
from typing import List

#Vou fazer arquivo dos connected_users

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
        self.filename = "./leaderboard.txt"
        self.Mutex = threading.Lock()
        with open(self.filename, 'a') as f:
            pass
        self.leaderboard = self.get_leaderboard()
        self.sort_leaderboard()

    def get_leaderboard(self) -> List:
        leaderboard = []
        with open(self.filename, "r") as file:
            for line in file:
                list_line = line.split(" ")
                ldb_entry = (list_line[0], int(list_line[1]))
                leaderboard.append(ldb_entry)

            leaderboard = dict(leaderboard)
        return leaderboard
            
    def add_user(self, usr: str) -> None:
        self.Mutex.acquire()

        with open(self.filename, "r+") as file:
            entry = usr + " " + ("0"*5) + "\n"
            file.write(entry)

        self.Mutex.release()

    def update_score(self, usr: str, points_won: int) -> None:
        if (not usr in self.leaderboard):
            print("Usuário não encontrado na leaderboard")
            return
        new_score = self.get_score(usr) + points_won

        self.leaderboard[usr] = new_score
        self.sort_leaderboard()
        self.__update_score_on_file(usr, new_score)

    def __update_score_on_file(self, usr: str, new_score: int) -> None:
        self.Mutex.acquire()

        with open(self.filename, "r+") as file:
            offset = 0

            for line in file:
                pos = line.split(" ")
                offset += len(pos[0]) + 1
                if (pos[0] == usr):
                    #Falta travar o arquivo (6 = 5 zeros + 1 \n)
                    file.seek(offset, os.SEEK_SET)
                    file.write("{0:05d}".format(new_score))
                    break
                offset += 5 + 1
        
        self.Mutex.release()

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


class UserList:
    def __init__(self):
        self.loginFile = 'userList.txt'
        self.userListMutex = threading.Lock()
        with open(self.loginFile, 'a') as f:
            pass

    def createLogin(self, username, passw):
        self.userListMutex.acquire()
        usernameUsed = False
        with open(self.loginFile, 'r') as f:
           lines = f.readlines()
           for line in lines:
               user = line.split(', ')[0]
               if user == username:
                   usernameUsed = True
                   break

        if usernameUsed:
            self.userListMutex.release()
            return False
        else:
            with open(self.loginFile, 'a') as f:
                f.write(f'{username}, {passw}\n')
            self.userListMutex.release()
            return True

    def login(self, username, passw):
        logged = False
        with open(self.loginFile, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.split(', ')
                u = line[0]
                p = line[1]
                if u == username and p[:-1] == passw:
                    logged = True

                    break

        return logged

    def changePassw(self, user, oldPassw, newPassw):
        lines = None
        done = False
        self.userListMutex.acquire()
        with open(self.loginFile, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                line = lines[i].split(', ')
                print(line[0] + '//' + user)
                print(line[1][:-1] + '//' + oldPassw)
                if line[0] == user and line[1][:-1] == oldPassw:
                    lines[i] = f'{user}, {newPassw}\n'
                    done = True

        if not done:
            self.userListMutex.release()
            return False

        with open(self.loginFile, 'w') as f:
            for line in lines:
                f.write(line)
        self.userListMutex.release()
        return True


#Talvez guardar IP dos players que estavam logados?
class LoggedUsers:
    def __init__(self) -> None:
        self.filename = 'logged_users.txt'
        self.fileMutex = threading.Lock()
        self.listMutex = threading.Lock()
        with open(self.filename, 'a') as f:
            pass
        self.list = self.get_users_from_file()
        if (self.list):
            #Aqui trataremos se ainda tinha um user logado na última execução do server
            pass


    def get_users_from_file(self) -> List:

        logged_list = []
        with open(self.filename, "r") as file:
            for line in file:
                usr = line.strip("\n")
                logged_list.append(usr)

        return logged_list

    def logout(self, usr: str) -> None:
        self.fileMutex.acquire()
        self.listMutex.acquire()

        self.list.remove(usr)

        self.listMutex.release()

        with open(self.filename, "w") as file:
            for usr in self.list:
                file.write(usr + "\n")
        
        self.fileMutex.release()

    def login(self, usr: str) -> None:
        self.fileMutex.acquire()
        self.listMutex.acquire()

        self.list.append(usr)

        self.listMutex.release()

        with open(self.filename, "a") as file:
            entry = usr + "\n"
            file.write(entry)

        self.fileMutex.release()

    def get_logged_users(self) -> str:
        self.listMutex.acquire()
        logged = ""
        for usr in self.list:
            logged += usr + "\n"
        self.listMutex.release()
        return logged


leaderboard = Leaderboard()
log = Log()
userList = UserList()
logged_users = LoggedUsers()


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




def sslInterpreter(user, logged, ss, addr):
    while True:
        command = ''

        try:
            command = ss.recv(1024).decode('utf-8')
        except:
            print(f'Cliente {addr} encerrou a conexão. SSL saindo')
            logged[0] = False
            break

        command = command.split()
        if not command:
            print(f'Cliente {addr} encerrou a conexão. SSL saindo')
            logged[0] = False
            break

        if logged[0] and command[0] == 'logout':
            print(f'Cliente {addr} deslogou! SSL saindo')
            logged_users.logout(user[0])
            logged[0] = False
            user[0] = None
            ss.sendall(bytearray('Logout realizado com sucesso!'.encode()))

        elif not logged[0] and len(command) == 3 and command[0] == 'adduser':
            print(f'Cliente {command[1]} quer se cadastrar!')
            username = command[1]
            passw = command[2]
            created = userList.createLogin(username, passw)
            if created:
                ss.sendall(bytearray('Usuário criado com sucesso!'.encode()))
            if not created:
                ss.sendall(bytearray('Usuário não foi criado!'.encode()))

        elif not logged[0] and len(command) == 3 and command[0] == 'login':
            loggedIn = userList.login(command[1], command[2])
            if loggedIn:
                logged[0] = loggedIn
                user[0] = command[1]
                logged_users.login(user[0])
                ss.sendall(bytearray('Logado com sucesso!'.encode()))
            else:
                ss.sendall(bytearray('Usuário ou senha desconhecido!'.encode()))

        elif logged[0] and len(command) == 3 and command[0] == 'passwd':
            changed = userList.changePassw(user[0], command[1], command[2])
            if changed:
                ss.sendall(bytearray('Senha alterada com sucesso!'.encode()))
            else:
                ss.sendall(bytearray('Senha não foi alterada!'.encode()))


        else:
            resp = bytearray('Comando errado'.encode())
            ss.sendall(resp)


#Connected user tem que ser adicionado aqui, pois é aqui dentro que será feita a autenticação
def Funcao_do_Lolo(sock : socket.socket, addr):
    logged = [False]
    user = [None]
    # Fecha o socket automaticamente quando sai do loop
    with sock as s:
        s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_listen.bind(('', 0))
        _, port = s_listen.getsockname()
        s.sendall(bytearray(str(port).encode()))

        s_listen.listen(5)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server.pem', 'server.key', password = 'servidor')
        ssock = context.wrap_socket(s_listen, server_side = True)
        #ssock.listen(5)
        ss, addr2 = ssock.accept()
        print(f'Cliente {(addr, addr2)} conectou')
        sslThread = threading.Thread(target=sslInterpreter, args=(user, logged, ss, addr))
        sslThread.start()
        while True:
            command = s.recv(1024).decode('utf-8')
            command = command.split()
            # Se o cliente desconectou, command será b''
            if not command:
                print(f'Cliente {addr} encerrou a conexão. Normal saindo')
                break

            if command[0] == 'logout':
                print(f'Cliente {addr} deslogou! Normal saindo')

            elif command[0] == 'leaders':
                resp = bytearray(leaderboard.get_formatted_leaderboard().encode())
                s.sendall(resp)

            elif command[0] == 'list':
                resp = bytearray(logged_users.get_logged_users().encode)
                s.sendall(resp)

            else:
                resp = bytearray('Comando errado'.encode())
                ss.sendall(resp)


main()