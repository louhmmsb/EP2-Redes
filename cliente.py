#!/bin/env python3

import ssl
import socket
import sys
import threading
import time
import os
from typing import List



# Código simples do cliente, por enquanto apenas enviando os comandos e recebendo a prompt
def main():
    IP = '127.0.0.1'
    PORT = int(sys.argv[1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))
        SSLPORT = int(s.recv(6).decode('utf-8'))
        print(SSLPORT)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ss = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = IP)
        ss.connect((IP, SSLPORT))

        while True:

            prompt = '>>> '
            out = ''
            try:
                while not out:
                    out = input(prompt)
            except:
                ss.close()
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

            else:
                command = bytearray(out.encode())
                s.sendall(command)
                ss.sendall(command)



main()
