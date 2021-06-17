#!/bin/env python3

import ssl
import socket
import sys
import threading
import time
from typing import List


prompt = '>>> '
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
                command = bytearray(out.encode())
                s.sendall(command)

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

    #TA DANDO ERRO, PEDINDO PRA CONECTAR MUITO CEDO
    #O certo seria dar um accept antes de passar a porta, meio lixo pq precisa de mais uma thread
    with s as backsocket:
        while True:
            message = ''
            try:
                while not message:
                    message = backsocket.recv(1024).decode('utf-8')
            except:
                break
            print()
            print(message + prompt, end='')

main()
