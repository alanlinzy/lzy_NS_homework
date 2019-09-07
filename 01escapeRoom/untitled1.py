# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 01:14:34 2019

@author: lzy19
"""
import socket
s =socket.socket()
s.connect(("127.0.0.1",56500))

print(s.recv(1024).decode())
inp = "look mirror\nget hairpin\nunlock door with hairpin\nopen door\n<EOL>\n"
s.send(inp.encode())
print(s.recv(1024).decode())
print(s.recv(1024).decode())
print(s.recv(1024).decode())
print(s.recv(1024).decode())
