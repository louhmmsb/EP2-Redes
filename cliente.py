#!/bin/env python3

import ssl
import socket
import sys
import threading
import time
from typing import List, Tuple


prompt = '>>> '

desafiando = [None]
mutex_desafiando = threading.Lock()
desafiante = [None]
mutex_desafiante = threading.Lock()

# Código simples do cliente, por enquanto apenas enviando os comandos e recebendo a prompt
def main():
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
        
        back_thread = threading.Thread(target=background_listener, args=(backsocket, ))
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

            if out.split()[0] == 'login' or out.split()[0] == 'adduser' or out.split()[0] == 'passwd':
                command = bytearray(out.encode())
                ss.sendall(command)
                resp = ss.recv(1024).decode('utf-8')
                print(resp)

            elif out.split()[0] == 'logout':
                command = bytearray(out.encode())
                s.sendall(command)
                ss.sendall(command)
                resp = ss.recv(1024).decode('utf-8')
                print(resp)

            elif out.split()[0] == 'list':
                command = bytearray(out.encode())
                s.sendall(command)
                resp = s.recv(1024).decode('utf-8')
                print(resp)

            elif out.split()[0] == 'begin':
                desafiando[0] = out.split()[1]
                command = bytearray(out.encode())

                s.sendall(command)
                
                resp = s.recv(1024).decode('utf-8')
                if resp.split()[0] != 'accept':
                    print(resp)
                else:
                    match_port = resp.split()[1]
                    match_ip = resp.split()[2]
                    print(match_port, match_ip)
                    #Conectar no inimigo
                    #Aqui, começa o jogo (tenta conectar no endereço fornecido pelo server)

            elif out.split()[0] == 'accept':
                
                match_listener, match_port = create_listener_socket()
                match_listener.listen()
                #Dar accept em match_listener e começar a partida
                command = out.split()[0] + " " + match_port
                command = bytearray(command.encode())
        
                s.sendall(command)

                resp = s.recv(1024).decode('utf-8')
                if resp != 'ok':
                    match_listener.close()
                else:
                    print("Ta no socket do jogo")
                    match_socket, match_addr = match_listener.accept()
                    #chamar nova função e passar prompt do jogo
            
            elif out.split()[0] == 'refuse':
                command = bytearray(out.encode())
                s.sendall(command)
                resp = s.recv(1024).decode('utf-8')
                if resp != 'ok':
                    print(resp)

            elif out.split()[0] == 'exit':
                ss.close()
                backsocket.close()
                break

            else:
                command = bytearray(out.encode())
                ss.sendall(command)
                resp = ss.recv(1024).decode('utf-8')
                print(resp)


def background_listener(s: socket.socket):

    str_desafio = 'Desafio'

    with s as backsocket:
        while True:
            message = ''
            try:
                while not message:
                    message = backsocket.recv(1024).decode('utf-8')
            except:
                break

            if message.split(": ")[0] == str_desafio:
                print("\n" + message + "\n" + prompt, end='')
                sys.stdout.flush()

                




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
