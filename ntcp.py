#!/usr/bin/env python3
#coding: utf-8

#nc

import sys
import socket
import getopt
import threading
import subprocess

#定义常量
listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
input_file          = ""
port                = 0

def usage():
    print("Net      Tools")
    print
    print("Usage: ntcp.py   -t target_host -p port")
    print("-l   --listen                listen on [host]:[port] for receiving")
    print("-e   --execute=command       execute the given command upon receiving a connecion")
    print("-c   --command               initialize a command shell, Ctrl+D to start")
    print("-u   --upload=destination    upon receiving connection upload a file and write to [destination]")
    print("-i   --input_file=filename   upload a executable file reading by rb mode")
    print("-h   --help                  print this")
    print
    print
    print("Examples:")
    print("ntcp.py -t 127.0.0.1 -p 5555 -l -c")
    print("ntcp.py -t 127.0.0.1 -p 5555 -l -u=/home/test.exe")
    print("ntcp.py -t 127.0.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'Hello' | ./ntcp.py -t 127.0.0.1 -p 5555")
    sys.exit(0)

def client_sender(buff):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        
        #print('[*] connected to %s:%d' % (target, port))
        #print('[*] Ctrl + D to to start!')

        if len(buff):
            l = client.send(buff)
            print('[*] send %d B to %s:%d' % (l, target, port))
        
        while True:

            #现在接收返回数据
            response = ''

            while True:

                data = client.recv(4096)
                recv_len = len(data)
                response = data.decode('utf-8')
                if recv_len < 4096:
                    break

            print(response, end='')

            buff = input()
            buff += "\n"
            client.send(buff.encode('utf-8'))

    except KeyboardInterrupt:
        print()
        print('[*] exiting, goodbey!')
        client.close()
        sys.exit(0)

    except BaseException as e:
        print('[*] Exception: %s' % e)
        client.close()
        sys.exit(1)

def server_loop():
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)
        
        while True:
            client_socket, addr = server.accept()
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print()
        print('[*] exiting, goodbey!')
        sys.exit(0)


def run_command(command):

    command = command.rstrip()

    try:
        output = subprocess.run(command, check=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, shell=True).stdout
    except:
        output = "Failed to execute command.\n".encode('ASCII')

    return output

def client_handler(client_socket):

    global execute
    global command

    try:
        if len(upload_destination):
            file_buff = ''.encode('utf-8')
            while True:
                data = client_socket.recv(4096)
                file_buff += data

                if len(data) < 4096:
                    break
            try:
                f = open(upload_destination, 'wb')
                f.write(file_buff)
                f.close()
                client_socket.send(('Successfully save file to ' +
                        '%s\n' % upload_destination).encode('ASCII'))
                #client_socket.close()
                #sys.exit(0)
            except:
                client_socket.send(('Fail to save file to {0}\n'.format(upload_destination)).encode('ASCII'))
                client_socke.close()
                sys.exit(1)

        if len(execute):
            output = run_command(execute)
            client_socket.send(output)
            client_socket.close()
            sys.exit(1)

        if command:
            while True:
                client_socket.send(b'NTCP:#')
                cmd_buff = ''
                while '\n' not in cmd_buff:
                    cmd_buff += client_socket.recv(1024).decode('utf-8')
                response = run_command(cmd_buff)
                client_socket.send(response)
    except KeyboardInterrupt:
        print()
        print('[*] exiting, goodbey!')
        client_socket.close()
        sys.exit(0)

def main():
    global listen
    global command
    global execute
    global target
    global upload_destination
    global port
    global input_file

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hlcu:e:t:p:i:', \
                ['help', 'listen', 'command=', 'upload=', \
                 'execute=', 'target=', 'port=', 'input_file='])
    except getopt.GetoptError as e:
        print(e)
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            #upload = True
            upload_destination = a
        elif o in ('-e', '--execute'):
            execute = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-i', '--input_file'):
            input_file = a

    #是监听还是从标准输入发生数据
    if not listen and len(target) and port > 0:

        if len(input_file):
            with open(input_file, 'rb') as f:
                buff = f.read()
            client_sender(buff)
        else:
            #读取标准输入数据
            buff = sys.stdin.read()

            #发送数据
            client_sender(buff.encode('utf-8'))

    if listen and len(target) and port > 0:
        server_loop()

if __name__ == '__main__':
    main()

