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
                mutex_desafiando.acquire()
                desafiando[0] = out.split()[1]
                mutex_desafiando.release()
                command = bytearray(out.encode())
                s.sendall(command)

            elif out.split()[0] == 'accept':
                mutex_desafiante.acquire()
                if not desafiante[0]:
                    print("Você não foi desafiado.")
                else:
                    match_listener, match_port = create_listener_socket()
                    #Dar accept em match_listener e começar a partida
                    command = out.split()[0] + " " + desafiante[0] + " " + match_port
                    command = bytearray(command.encode())
                    s.sendall(command)
                mutex_desafiante.release()                


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

            if (message.split(": ") == str_desafio):
                message = message[len(str_desafio)+2:]
                mutex_desafiante.acquire()
                desafiante[0] = message.split()[0]
                mutex_desafiante.release()

            print()
            print(message + prompt, end='')


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
