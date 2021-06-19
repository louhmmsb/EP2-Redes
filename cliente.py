#!/bin/env python3

import random
import timeit
import ssl
import socket
import sys
import threading
import time
from tictactoe import *
from typing import List, Tuple


prompt = '>>> '

desafiando = [None]
mutex_desafiando = threading.Lock()
desafiante = [None]
mutex_desafiante = threading.Lock()

s = None
ss = None
backsocket = None

# Código simples do cliente, por enquanto apenas enviando os comandos e recebendo a prompt
def main():
    global user
    global IP
    global PORT
    user = None

    IP = '127.0.0.1'
    PORT = int(sys.argv[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))
        SSLPORT = int(s.recv(5).decode('utf-8'))
        print(SSLPORT)

        backsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backsocket.connect((IP, SSLPORT))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ss = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = IP)
        ss.connect((IP, SSLPORT))

        ok = bytearray('ok'.encode())
        ss.sendall(ok)
        
        back_thread = threading.Thread(target=background_server_listener, args=(backsocket, ))
        back_thread.start()

        while True:

            out = ''
            try:
                while not out:
                    out = input(prompt)
            except:
                ss.close()
                backsocket.close()
                break

            first = out.split()[0]

            if first == 'login' or first == 'adduser' or first == 'passwd':
                send_command_to_socket(out, ss)
                resp = receive_string_from_socket(ss)
                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, ss)
                    resp = receive_string_from_socket(ss)
                
                if resp == 'Logado com sucesso!':
                    user = out.split()[1]
                
                print(resp)

            elif first == 'logout' or first == 'list' or first == 'leaders':
                send_command_to_socket(out, s)
                resp = receive_string_from_socket(s)
                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, s)
                    resp = receive_string_from_socket(s)
                if first == 'logout':
                    user = None
                print(resp)

            elif first == 'begin':
                desafiando[0] = out.split()[1]

                send_command_to_socket(out, s)
                
                resp = receive_string_from_socket(s)

                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, s)
                    resp = receive_string_from_socket(s)

                if resp.split()[0] != 'accept':
                    print(resp)
                else:
                    game_port = int(resp.split()[1])
                    game_ip = resp.split()[2]
                    #print(game_port, game_ip)
                    #Conectar no inimigo
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as game_socket:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as delay_socket:
                            #Aqui, começa o jogo (tenta conectar no endereço fornecido pelo server)
                            game_socket.connect((game_ip, game_port))
                            delay_socket.connect((game_ip, game_port))
                            playGame(game_socket, delay_socket, 1, s)


            elif first == 'accept':
                
                game_listener, game_port = create_listener_socket()
                game_listener.listen()
                #Dar accept em game_listener e começar a partida
                command = first + " " + game_port
                
                send_command_to_socket(command, s)

                resp = receive_string_from_socket(s)
                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, s)
                    resp = receive_string_from_socket(s)

                if resp != 'ok':
                    game_listener.close()
                else:
                    game_socket, game_addr = game_listener.accept()
                    delay_socket, delay_addr = game_listener.accept()
                    game_listener.close()
                    #chamar nova função e passar prompt do jogo
                    with game_socket:
                        with delay_socket:
                            playGame(game_socket, delay_socket, 0, s)

            elif first == 'refuse':
                send_command_to_socket(out, s)
                resp = receive_string_from_socket(s)
                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, s)
                    resp = receive_string_from_socket(s)

                if resp != 'ok':
                    print(resp)

            elif first == 'exit':
                ss.close()
                backsocket.close()
                break

            else:
                send_command_to_socket(out, ss)
                resp = receive_string_from_socket(ss)
                while resp == '':
                    #Conexão fechada (internamente por timeout ou pelo servidor)
                    success, s, backsocket, ss = reconnect()
                    if not success:
                        #avisar o cliente q o server morreu e fechar
                        return
                    send_command_to_socket(out, s)
                    resp = receive_string_from_socket(s)
                print(resp)

    
def send_command_to_socket(command: str, s: socket.socket):
    command = bytearray(command.encode())
    s.sendall(command)


def receive_string_from_socket(s: socket.socket):
    return s.recv(1024).decode('utf-8')


mutex_try_reconnect = threading.Lock()
tried_to_reconnect = 0
mutex_reconnected = threading.Lock()
reconnected = 0

def reconnect():
    global s
    global ss
    global backsocket

    global user
    global IP
    global PORT
    
    global tried_to_reconnect
    global reconnected
    mutex_try_reconnect.acquire()
    if tried_to_reconnect == 1:
        
        mutex_reconnected.acquire()
        r = reconnected
        mutex_reconnected.release()
        while r == 0:
            time.sleep(1)
            mutex_reconnected.acquire()
            r = reconnected
            mutex_reconnected.release()

        mutex_reconnected.acquire()
        reconnected = 0
        mutex_reconnected.release()

        if r == 1:
            tried_to_reconnect = 0
            mutex_try_reconnect.release()
            return 1, s, backsocket, ss
        else:
            tried_to_reconnect = 0
            mutex_try_reconnect.release()
            return 0, None, None, None

    tried_to_reconnect = 1
    mutex_try_reconnect.release()

    print("Conexão com o servidor perdida... reconectando")  
    connected = False  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t_wait = 0
    while not connected and t_wait < 180:
        try:  
            s.connect((IP, PORT))  
            connected = True  
            print("Reconexão bem sucedida!")  
        except socket.error:  
            time.sleep(2)
            t_wait += 2

    if t_wait >= 180:
        print("A tentativa de reconexão falhou. O processo do servidor foi morto")
        mutex_reconnected.acquire()
        reconnected = -1
        mutex_reconnected.release()
        return 0, None, None, None


    SSLPORT = int(s.recv(5).decode('utf-8'))

    backsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backsocket.connect((IP, SSLPORT))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ss = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = IP)
    ss.connect((IP, SSLPORT))

    if user:
        user = 'user ' + user
    else:
        user = 'ok'
    user_bytes = bytearray(user.encode())
    ss.sendall(user_bytes)

    mutex_reconnected.acquire()
    reconnected = 1
    mutex_reconnected.release()


    return 1, s, backsocket, ss

def background_server_listener(backsocket: socket.socket):

    str_desafio = 'Desafio'

    while True:
        message = ''
        try:
            message = backsocket.recv(1024).decode('utf-8')
            if not message:
                success, _, backsocket, _ = reconnect()
                if not success:
                    break
        except:
            break

        if message.split(": ")[0] == str_desafio:
            print("\n" + message + "\n" + prompt, end='')
            sys.stdout.flush()

        elif message == 'Ping':
            #print('Sente o pong saindo')
            backsocket.sendall(bytearray('Pong'.encode()))



def playGame(game_socket :socket.socket, delay_socket :socket.socket, requisitou: int, default_socket :socket.socket):

    player = 0
    game = TicTacToe()
    ping_list = []
    play = input("Pedra, papel e tesoura para decidir quem começa (Pedra = 1, Papel = 2, Tesoura = 3): ")
    game_socket.sendall(bytearray(play.encode()))
    play = int(play)
    op_play = int(game_socket.recv(1024).decode('utf-8'))
    while play == op_play:
        play = input("Empate! Mais uma vez: ")
        game_socket.sendall(bytearray(play.encode()))
        play = int(play)
        op_play = int(game_socket.recv(1024).decode('utf-8'))

    if (play == 1 and op_play == 3) or (play == op_play+1):
        print("Você ganhou! Você começa o jogo e é o jogador X")
        player = 1
    else:
        print("Você perdeu! O oponente começa o jogo e você é o jogador O")
        player = 2

    delay_thread = threading.Thread(target=background_client_communication, args=(delay_socket, requisitou, ping_list))
    delay_thread.start()

    game.printGame()
    while game.state == 0:
        if game.turn == player:
            command = ''
            while not command :
                command = input(">>> ")
            splitted = command.split(' ')
            if splitted[0] == 'send':
                game_socket.sendall(bytearray(command.encode()))
                move = tuple(map(int, splitted[1:]))
                game.makeMove(move)
                game.updateState()
                game.printGame()

            elif splitted[0] == 'delay':
                i = len(ping_list)-1
                prints = 0
                while i >= 0 and prints < 3:
                    print(f'{prints}. {ping_list[i]:.03f} ms')
                    i -= 1
                    prints += 1

            elif splitted[0] == 'end':
                game_socket.sendall(bytearray(command.encode()))
                print('Vocẽ terminou o jogo')
                return

        else:
            command = game_socket.recv(1024).decode('utf-8').split(' ')
            if command[0] == 'send':
                move = tuple(map(int, command[1:]))
                game.makeMove(move)
                game.updateState()
                game.printGame()
            elif command[0] == 'end':
                print(f'Player {(player%2) + 1} terminou o jogo antecipadamente')
                return

    if game.winner == None:
        print("Empate!")
        default_socket.sendall(bytearray('empate'.encode()))
    elif game.winner == player:
        print("Você ganhou!")
        default_socket.sendall(bytearray('vitoria'.encode()))
    else:
        print("Você perdeu :(")
        default_socket.sendall(bytearray('derrota'.encode()))


def background_client_communication(delay_socekt: socket.socket, n_cliente: int, ping_list: list):
    #Cada ping consistirá de 3 pacotes:
    #O primeiro, enviado pelo cliente que requisitou a partida
    #O segundo, uma resposta do outro cliente (com isso o que requisitou mede o delay)
    #O terceiro, enviado novamente pelo que requisitou a partida em resposta ao segundo pacote (para que
    #o outro cliente possa calcular o delay também)
    #Depois, troca a ordem
    delay = 0
    t1 = 0
    t2 = 0
    ping = "ping"
    ping = bytearray(ping.encode())
    npack = 0
    while True:
        if n_cliente:
            #Aqui vai o sleep entre delays pra nao ficar dando ping a rodo
            if npack == 3:
                time.sleep(0.5) #Arbitrário
                npack = 0
            t1 = time.time()
            t2 = 0

            try:
                delay_socekt.sendall(ping)
            except:
                break

            n_cliente -= 1
            npack += 1
        else:
            if npack == 3:
                t1 = 0
                npack = 0

            resp = ''
            try:
                while not resp:
                    resp = delay_socekt.recv(5).decode('utf-8')
            except:
                break

            t2 = time.time()
            n_cliente += 1
            npack += 1
        
        #Por enquanto isso parece injusto, o outro cara tem que esperar eu calcular meu delay
        if t1 and t2:
            delay = (t2 - t1)*1000
            t1 = 0
            t2 = 0
            #Mutexar a lista?
            ping_list.append(delay)
            if (len(ping_list) > 3):
                ping_list.pop(0)


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

main()
