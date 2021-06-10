#!/bin/env python3

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
        while True:
            prompt = s.recv(1024)
            out = ''
            while not out:
                out = input(prompt.decode('utf-8'))
            command = bytearray(out.encode())
            s.sendall(command)

main()
