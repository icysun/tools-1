#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#ssh服务器，与sshRcmd.py一起使用，负责发生命令
#实际是一个以ssh服务器形式的客户端

import socket
import paramiko
import threading
import sys

#使用paramiko示例文件的密钥
host_key = paramiko.RSAKey(filename='test_rsa.key')

#继承ssh服务类
class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'justin') and (password == 'lovethepython'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

if len(sys.argv[1:]) != 2:
    print('Usage: ./sshserver.py server_ip server_port')
    print('Example: ./sshserver.py 127.0.0.1 9090')
    sys.exit(1)

server = sys.argv[1]

ssh_port = int(sys.argv[2])

#监听服务器，等待socket连接
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Listening for connection ...')
    client, addr = sock.accept()
except Exception as e:
    print('[-] Listen failed: ' + str(e))
    sys.exit(1)

print('[+] Got a connection!')

#给socket连接配置ssh管道并配置认证模式
try:
    session = paramiko.Transport(client)
    session.add_server_key(host_key)
    server = Server()
    
    try:
        session.start_server(server = server)
    except paramiko.SSHException as x:
        print('[-] SSH negotiation failed.')

    chan = session.accept(20)
    print('[+] Authenticated!')

    print(chan.recv(1024))

    chan.send('Welcome to ssh!')

    while True:
        try:
            command = input('Enter command: ').strip('\n')

            if command != 'exit':
                chan.send(command)
                print(chan.recv(4096).decode('utf-8'))
            else:
                chan.send('exit')
                print(chanrecv(1024).decode('utf-8'))
                print('exiting')
                session.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            session.close()
except Exception as e:
    print('[-] Caught exception: ' + str(e))
    try:
        session.close()
    except:
        pass
    sys.exit(1)

            
