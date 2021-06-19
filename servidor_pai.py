#!/usr/bin/python3

import ssl
import socket
import sys
import threading
import time
import os
from typing import List, Tuple

managers = list()

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

        self.leaderboard[usr] = 0

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
"""
Formato do arquivo de users logados:
username IP jogando(0|1)\n
"""
class LoggedUsers:
    def __init__(self) -> None:
        self.filename = 'logged_users.txt'
        self.fileMutex = threading.Lock()
        self.listMutex = threading.Lock()
        with open(self.filename, 'a') as f:
            pass
        self.list = self.get_users_from_file()
        if (self.list):
            print("tinha alguem")
            #Aqui trataremos se ainda tinha um user logado na última execução do server
            pass


    def get_users_from_file(self) -> List:

        logged_list = []
        with open(self.filename, "r") as file:
            for line in file:
                line_split = line.split(" ")
                usr = line_split[0]
                addr_ip = line_split[1]
                playing = int(line_split[2])
                logged_list.append([usr, addr_ip, playing])

        return logged_list

    def get_user_from_index(self, i: int) -> str:
        return self.list[i][0]

    def is_playing(self, usr: str) -> int:
        playing = -1
        self.listMutex.acquire()
        for i in range (len(self.list)):
            if (self.get_user_from_index(i) == usr):
                playing = self.list[i][2]
                break
        self.listMutex.release()
        return playing


    def logout(self, usr: str) -> None:
        if not usr:
            return
        self.fileMutex.acquire()
        self.listMutex.acquire()

        for i in range (len(self.list)):
            if (self.get_user_from_index(i) == usr):
                removed_entry = self.list.pop(i)
                break

        self.listMutex.release()

        with open(self.filename, "w") as file:
            for usr_tuple in self.list:
                entry = f'{usr_tuple[0]} {usr_tuple[1]} {usr_tuple[2]}\n'
                file.write(entry)
        
        self.fileMutex.release()

    def login(self, usr: str, addr, sock: socket.socket) -> None:
        self.fileMutex.acquire()
        self.listMutex.acquire()

        playing = 0

        entry = [usr, addr[0], playing, sock]

        self.list.append(entry)

        self.listMutex.release()

        with open(self.filename, "a") as file:
            entry = f'{usr} {addr[0]} {playing}\n'
            file.write(entry)

        self.fileMutex.release()

    def get_logged_users(self) -> str:
        self.listMutex.acquire()

        TAB_SIZE = 8
        N_TABS = 4

        logged = "Username" + ("\t"*(N_TABS-1)) + "Estado\n\n"
        for usr_tuple in self.list:
            username = usr_tuple[0]
            playing = usr_tuple[2]
            if (playing):
                play_str = "Jogando"
            else:
                play_str = "Disponível"
            tabs = "\t" * self.n_tabs(len(username), TAB_SIZE, N_TABS)
            logged += f'{username}{tabs}{play_str}\n'
        self.listMutex.release()
        return logged

    def change_state(self, usr: str, playing: int) -> None:
        self.listMutex.acquire()
        
        for i in range (len(self.list)):
            if self.get_user_from_index(i) == usr:
                self.list[i][2] = playing
                break
        self.listMutex.release()
        
        self.__change_state_on_file(usr, playing)


    def __change_state_on_file(self, usr: str, playing: int) -> None:        
        self.fileMutex.acquire()
        
        with open(self.filename, 'r+') as file:
            offset = 0

            for line in file:
                pos = line.split()
                offset += len(pos[0]) + 1 + len(pos[1]) + 1
                if (pos[0] == usr):
                    file.seek(offset, os.SEEK_SET)
                    file.write(f'{playing}')
                    break
                offset += 1 + 1

        self.fileMutex.release()


    def n_tabs(self, len: int, TAB_SIZE: int, N_TABS: int) -> int:
        ntabs = (TAB_SIZE*N_TABS - len)//TAB_SIZE
        if ((TAB_SIZE*N_TABS - len) % TAB_SIZE != 0):
            ntabs += 1
        return ntabs

class clientManager:
    def __init__(self, socket: socket.socket, addr):
        self.s = socket
        self.addr = addr

        s_listen, port = create_listener_socket()
        self.s.sendall(bytearray(port.encode()))

        self.s_sender, addr_background = s_listen.accept()

        self.ss, addr_SSL = setup_SSL_socket(s_listen)
        self.logged = False
        self.user = None
        self.desafiando = None
        self.desafiante = None

        self.buffer = None
        self.escreveu = 0
        self.leu = 1
        self.leu_mutex = threading.Lock()
        self.escreveu_mutex = threading.Lock()

        print(f'Cliente {(addr, addr_SSL, addr_background)} conectou')

    def write_buffer(self, manager, msg: str):
        """Recebe um client manager e uma mensagem e a escreve no buffer deste manager.
        Retorna 1 caso tenha conseguido escrever, 0 caso contrário (já possui mensagem 
        não lida no buffer)
        """
        return manager.write_my_buffer(msg)

    def read_buffer(self, manager):
        """Recebe um client manager e retorna a mensagem no buffer desse manager.
        Retorna None caso não tenha nada no buffer
        """
        return manager.read_my_buffer()

    def write_my_buffer(self, msg: str):
        self.escreveu_mutex.acquire()
        if self.escreveu == 0:
            self.buffer = msg
            self.escreveu = 1
            self.escreveu_mutex.release()
            self.reset_my_leu()
            retval = 1
        else:
            #Ainda tem mensagem a ser lida no buffer
            self.escreveu_mutex.release()
            retval = 0
        return retval

    def read_my_buffer(self):
        msg = None
        self.leu_mutex.acquire()
        if self.leu == 0:
            msg = self.buffer
            self.leu = 1
            self.leu_mutex.release()
            self.reset_my_escreveu()
        else:
            self.leu_mutex.release()
        return msg

    def reset_my_leu(self):
        self.leu_mutex.acquire()
        self.leu = 0
        self.leu_mutex.release()
        

    def reset_my_escreveu(self):
        self.escreveu_mutex.acquire()
        self.escreveu = 0
        self.buffer = None
        self.escreveu_mutex.release()

    def interpret_buffer_message(self, msg: str):
        
        if msg.split()[0] == 'begin':
            self.desafiante = msg.split()[1]
            send_begin(self.s_sender, self.desafiante)
            return 'begin'
        
        elif msg.split()[0] == 'accept':
            send_message_to_sock(self.s, msg)
            return 'accept'

        elif msg.split()[0] == 'refuse':
            msg = "Seu desafio foi recusado :("
            send_message_to_sock(self.s, msg)
            return 'refuse'
        else:
            return 'unknown'

    def send_to_manager(self, manager_str: str, msg: str):
        for man in managers:
            if man.user == manager_str:
                while not self.write_buffer(man, msg):
                    #Fica tentando escrever. Não vai dar deadlock pois o server sempre vai limpar o buffer
                    #Uma hora ficará disponível
                    time.sleep(0.01)
                return 1
        return -1


    def interpreter(self):
        sslThread = threading.Thread(target=self.sslInterpreter, args=())
        sslThread.start()
        mainThread = threading.Thread(target=self.manage, args=())
        mainThread.start()

    def manage(self):
        global logged_users
        global log
        global userList
        global leaderboard

        #self.s.setblocking(0)
        self.s.settimeout(0.01)

        with self.s as s:
            counter = 0
            while True:
                try:
                    command = s.recv(1024).decode('utf-8')
                    command = command.split()
                    if (self.normalInterpreter(command) == -1):
                        break
                except:
                    counter += 1
                    #espera ocupada
                    #time.sleep(1)
                    if counter == 300:
                        #print('Oloko, vou mandar ping')
                        self.s_sender.sendall(bytearray('Ping'.encode()))
                        self.s_sender.settimeout(5)
                        try:
                            resp = self.s_sender.recv(1024).decode()
                        except:
                            #print('Ihh morreu')
                            pass
                        #print('Deu bom')
                        self.s_sender.settimeout(None)
                        counter = 0
                    self.get_and_treat_buffer_content()
    
    def get_and_treat_buffer_content(self):
        buff_content = self.read_my_buffer()
        if buff_content:
            return self.interpret_buffer_message(buff_content)
        return 0
    
    def normalInterpreter(self, command):
        
        if not command:
            print(f'Cliente {self.user} {self.addr} encerrou a conexão. Normal saindo')
            logged_users.logout(self.user)
            self.s_sender.close()
            return -1
        

        if self.logged:
            if command[0] == 'logout':
                print(f'Cliente {self.user} {self.addr} deslogou! Normal saindo')
                logged_users.logout(self.user)
                self.logged = False
                self.user = None
                self.s.sendall(bytearray('Logout realizado com sucesso!'.encode()))

            elif command[0] == 'leaders':
                resp = bytearray(leaderboard.get_formatted_leaderboard().encode())
                self.s.sendall(resp)

            elif command[0] == 'list':
                resp = bytearray(logged_users.get_logged_users().encode())
                self.s.sendall(resp)

            elif command[0] == 'begin':
                self.desafiando = command[1]
                msg = command[0] + " " + self.user
                if logged_users.is_playing(self.desafiando) == 1:
                    resp = "Este usuário está em uma partida!"
                    self.s.sendall(bytearray(resp.encode()))
                elif self.send_to_manager(self.desafiando, msg) == -1:
                    resp = "Este usuário não está logado!"
                    self.s.sendall(bytearray(resp.encode()))
                else:
                    #Aqui, a thread deve ler o buffer até que tenha uma resposta 
                    #(caso queiramos que o shell fique travado ao usar o begin)
                    buff = self.get_and_treat_buffer_content()
                    while not buff:
                        time.sleep(0.01)
                        buff = self.get_and_treat_buffer_content()
                    if buff == 'accept':
                        logged_users.change_state(self.user, 1)
                    elif buff == 'refuse':
                        self.desafiando = None

            #Formato do accept:
            #accept PORTA
            elif command[0] == 'accept':
                if not self.desafiante:
                    resp = "Você não recebeu nenhum desafio!"
                    self.s.sendall(bytearray(resp.encode()))
                else:
                    game_port = command[1]
                    msg = command[0] + " " + game_port + " " + self.addr[0]
                    self.send_to_manager(self.desafiante, msg)
                    resp = "ok"
                    self.s.sendall(bytearray(resp.encode()))
                    logged_users.change_state(self.user, 1)

            elif command[0] == 'refuse':
                if not self.desafiante:
                    resp = "Você não recebeu nenhum desafio!"
                    self.s.sendall(bytearray(resp.encode()))
                else:
                    resp = "ok"
                    self.desafiante = None
                    self.s.sendall(bytearray(resp.encode()))
                    self.send_to_manager(self.desafiante, command[0])

            elif command[0] == 'empate':
                print(f'Ih empatou')
                leaderboard.update_score(self.user, 1)
                self.end_of_game()

            elif command[0] == 'vitoria':
                print(f'Ih {self.user} ganhou')
                leaderboard.update_score(self.user, 2)
                self.end_of_game()

            elif command[0] == 'derrota':
                print(f'Ih {self.user} perdeu')
                self.end_of_game()

        else:
            resp = "Você precisa estar logado para usar este comando"
            self.s.sendall(bytearray(resp.encode()))

    def end_of_game(self) -> None:
        logged_users.change_state(self.user, 0)
        self.desafiante = None
        self.desafiando = None

    def sslInterpreter(self):
        global logged_users
        global log
        global userList
        global leaderboard

        with self.ss as ss:
            while True:
                command = ''

                try:
                    command = ss.recv(1024).decode('utf-8')
                except:
                    print(f'Cliente {self.user} {self.addr} encerrou a conexão. SSL saindo')
                    self.logged = False
                    break

                command = command.split()
                if not command:
                    print(f'Cliente {self.user} {self.addr} encerrou a conexão. SSL saindo')
                    self.logged = False
                    break

                if self.logged and command[0] == 'logout':
                    print(f'Cliente {self.user} {self.addr} deslogou! SSL saindo')
                    # logged_users.logout(self.user)
                    # self.logged = False
                    # self.user = None
                    # self.ss.sendall(bytearray('Logout realizado com sucesso!'.encode()))

                elif not self.logged and len(command) == 3 and command[0] == 'adduser':
                    print(f'Cliente {command[1]} quer se cadastrar!')
                    username = command[1]
                    passw = command[2]
                    created = userList.createLogin(username, passw)
                    if created:
                        leaderboard.add_user(username)
                        ss.sendall(bytearray('Usuário criado com sucesso!'.encode()))
                    if not created:
                        ss.sendall(bytearray('Usuário não foi criado!'.encode()))

                elif not self.logged and len(command) == 3 and command[0] == 'login':
                    loggedIn = userList.login(command[1], command[2])
                    if loggedIn:
                        self.logged = loggedIn
                        self.user = command[1]
                        logged_users.login(self.user, self.addr, self.s)
                        ss.sendall(bytearray('Logado com sucesso!'.encode()))
                    else:
                        ss.sendall(bytearray('Usuário ou senha desconhecido!'.encode()))

                elif self.logged and len(command) == 3 and command[0] == 'passwd':
                    changed = userList.changePassw(self.user, command[1], command[2])
                    if changed:
                        ss.sendall(bytearray('Senha alterada com sucesso!'.encode()))
                    else:
                        ss.sendall(bytearray('Senha não foi alterada!'.encode()))

                else:
                    resp = bytearray('Comando errado'.encode())
                    ss.sendall(resp)



leaderboard = Leaderboard()
log = Log()
userList = UserList()
logged_users = LoggedUsers()


def main():
    if (len(sys.argv) != 2):
        print("Execução: " + sys.argv[0] + " porta")
        exit(1)
    
    PORT = int(sys.argv[1])
    HOST = ''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_listen:

        s_listen.bind((HOST, PORT))
        s_listen.listen()
        
        while(True):
            try:
                conn, addr = s_listen.accept()
            except:
                break
            cm = clientManager(conn, addr)

            managers.append(cm)
            cm.interpreter()






def create_listener_socket() -> Tuple[socket.socket, str]:
    """Cria um socket de listen usando uma porta disponível.
       Retorna o socket (pronto para accept) e sua porta em 
       uma string com 5 caracteres."""

    s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_listen.bind(('', 0))
    s_listen.listen(5)
    _, port1 = s_listen.getsockname()
    str_port1 = '%05d' % port1
    return s_listen, str_port1


def setup_SSL_socket(s_listen: socket.socket):
    """Recebe um socket de listen (pronto) e cria um socket
       SSL a partir daquele. Retorna o socket e seu endereço."""

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server.pem', 'server.key', password = 'servidor')
    ssock = context.wrap_socket(s_listen, server_side = True)
    #ssock.listen(5)
    return ssock.accept()


def send_begin(s: socket.socket, usr: str):
    msg = 'Desafio: '
    msg += usr + " o desafiou a uma partida! (accept|refuse)"
    send_message_to_sock(s, msg)

def send_message_to_sock(s: socket.socket, msg: str):
    s.sendall(bytearray(msg.encode()))

main()