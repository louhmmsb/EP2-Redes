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


prompt = 'JogoDaVelha>'

ping_timeout = 180

desafiando = [None]
mutex_desafiando = threading.Lock()
desafiante = [None]
mutex_desafiante = threading.Lock()
manual_death = [False]

s_g = [None]
ss_g = [None]
backsocket_g = [None]

user = None
IP = None
PORT = None

# Código simples do cliente, por enquanto apenas enviando os comandos e recebendo a prompt
def main():
    global user
    global IP
    global PORT
    user = None

    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} ip porta")
        return

    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))
        SSLPORT = int(s.recv(5).decode('utf-8'))

        backsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backsocket.connect((IP, SSLPORT))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ss = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = IP)
        ss.connect((IP, SSLPORT))

        send_command_to_socket('ok', ss)
        
        back_thread = threading.Thread(target=background_server_listener, args=(backsocket, s, ss, manual_death))
        back_thread.start()

        while True:

            out = ''
            try:
                while not out:
                    out = input(prompt)
            except:
                manual_death[0] = True
                ss.close()
                backsocket.close()
                break

            first = out.split()[0]

            try:

                if first == 'login' or first == 'adduser' or first == 'passwd':

                    resp, s, backsocket, ss = try_to_send_command(out, ss, s, backsocket, ss)
                    if not resp:
                        return

                    if resp == 'Logado com sucesso!':
                        user = out.split()[1]

                    print(resp)

                elif first == 'logout' or first == 'list' or first == 'leaders':

                    resp, s, backsocket, ss = try_to_send_command(out, s, s, backsocket, ss)
                    if not resp:
                        return

                    if first == 'logout':
                        user = None
                    print(resp)

                elif first == 'begin':
                    desafiando[0] = out.split()[1]

                    resp, s, backsocket, ss = try_to_send_command(out, s, s, backsocket, ss)
                    if not resp:
                        return

                    if resp.split()[0] != 'accept':
                        print(resp)
                    else:
                        game_port = int(resp.split()[1])
                        game_ip = resp.split()[2]
                        
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as game_socket:
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as delay_socket:
                                #Aqui, começa o jogo (tenta conectar no endereço fornecido pelo server)
                                game_socket.connect((game_ip, game_port))
                                delay_socket.connect((game_ip, game_port))
                                ret = playGame(game_socket, delay_socket, 1, s)

                                resp, s, backsocket, ss = try_to_send_command(ret, s, s, backsocket, ss)
                                if not resp:
                                    return


                elif first == 'accept':
                    game_listener, game_port = create_listener_socket()
                    game_listener.listen()

                    command = first + " " + game_port

                    resp, s, backsocket, ss = try_to_send_command(command, s, s, backsocket, ss)
                    if not resp:
                        return

                    if resp != 'ok':
                        print(resp)
                        game_listener.close()
                    else:
                        game_socket, game_addr = game_listener.accept()
                        delay_socket, delay_addr = game_listener.accept()
                        game_listener.close()
                        #chamar nova função e passar prompt do jogo
                        with game_socket:
                            with delay_socket:
                                ret = playGame(game_socket, delay_socket, 0, s)

                                resp, s, backsocket, ss = try_to_send_command(ret, s, s, backsocket, ss)
                                if not resp:
                                    return

                elif first == 'refuse':
                    
                    resp, s, backsocket, ss = try_to_send_command(out, s, s, backsocket, ss)
                    if not resp:
                        return

                    if resp != 'ok':
                        print(resp)

                elif first == 'exit':
                    ss.close()
                    backsocket.close()
                    manual_death[0] = True
                    break

                else:

                    resp, s, backsocket, ss = try_to_send_command(out, ss, s, backsocket, ss)
                    if not resp:
                        return

                    print(resp)

            except:
                print("Terminando o programa")
                break
    
def send_command_to_socket(command: str, s: socket.socket):
    command = bytearray(command.encode())
    s.sendall(command)


def receive_string_from_socket(s: socket.socket):
    return s.recv(1024).decode('utf-8')

def try_to_send_command(command: str, used_socket: socket.socket, s: socket.socket, backsocket: socket.socket, ss: ssl.SSLSocket):
    send_command_to_socket(command, used_socket)
    resp = receive_string_from_socket(used_socket)

    while resp == '':
        #Conexão fechada
        success, s, backsocket, ss = update_sockets()
        if not success:
            break
        send_command_to_socket(command, s)
        resp = receive_string_from_socket(s)

    return resp, s, backsocket, ss


mutex_reconnected = threading.Lock()
reconnected = 0

def update_sockets():
    global reconnected

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
        return 1, s_g[0], backsocket_g[0], ss_g[0]
    else:
        return 0, None, None, None

def reconnect():

    global user
    global IP
    global PORT

    global reconnected
        

    print("\nConexão com o servidor perdida... reconectando")  
    connected = False
    s_g[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t_wait = 0
    while not connected and t_wait < 180:
        try:  
            s_g[0].connect((IP, PORT))  
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


    SSLPORT = int(s_g[0].recv(5).decode('utf-8'))

    backsocket_g[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backsocket_g[0].connect((IP, SSLPORT))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ss_g[0] = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = IP)
    ss_g[0].connect((IP, SSLPORT))

    if user:
        reply = 'user ' + user
    else:
        reply = 'ok'
    send_command_to_socket(reply, ss_g[0])

    mutex_reconnected.acquire()
    reconnected = 1
    mutex_reconnected.release()

    print(prompt, end='')
    sys.stdout.flush()

    return 1, s_g[0], backsocket_g[0], ss_g[0]


def background_server_listener(backsocket: socket.socket, normal_socket: socket.socket, ssl_socket: ssl.SSLSocket, manual_death):

    str_desafio = 'Desafio'
    backsocket.settimeout(ping_timeout)

    while True:
        message = ''
        try:
            message = receive_string_from_socket(backsocket)
            if not message:
                success, _, backsocket, _ = reconnect()
                if not success:
                    break
        except:
            if manual_death[0]:
                break
            print('\nNão foi possível restabelecer conexão com o servidor, digite qualquer coisa para terminar o cliente\n' + prompt, end="")
            sys.stdout.flush()
            normal_socket.close()
            ssl_socket.close()
            backsocket.close()
            break

        if message.split(": ")[0] == str_desafio:
            print("\n" + message + "\n" + prompt, end='')
            sys.stdout.flush()
    
        elif message == 'Ping':
            try:
                send_command_to_socket('Pong', backsocket)
            except:
                break



def playGame(game_socket :socket.socket, delay_socket :socket.socket, requisitou: int, default_socket :socket.socket):

    player = 0
    game = TicTacToe()
    ping_list = []
    play = input("Pedra, papel e tesoura para decidir quem começa (Pedra = 1, Papel = 2, Tesoura = 3): ")
    send_command_to_socket(play, game_socket)
    play = int(play)
    op_play = int(receive_string_from_socket(game_socket))
    while play == op_play:
        play = input("Empate! Mais uma vez: ")
        send_command_to_socket(play, game_socket)
        play = int(play)
        op_play = int(receive_string_from_socket(game_socket))

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
                send_command_to_socket(command, game_socket)
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
                send_command_to_socket(command, game_socket)
                print('Você terminou o jogo')
                return 'end'

        else:
            command = receive_string_from_socket(game_socket).split(' ')
            if command[0] == 'send':
                move = tuple(map(int, command[1:]))
                game.makeMove(move)
                game.updateState()
                game.printGame()
            elif command[0] == 'end':
                print(f'Player {(player%2) + 1} terminou o jogo antecipadamente')
                return 'end'

    if game.winner == None:
        print("Empate!")
        return 'empate'
    elif game.winner == player:
        print("Você ganhou!")
        return 'vitoria'
    else:
        print("Você perdeu :(")
        return 'derrota'


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
    ping = bytearray("ping".encode())
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
                    resp = receive_string_from_socket(delay_socekt)
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
