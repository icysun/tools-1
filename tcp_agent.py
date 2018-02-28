#!/usr/bin/env python3
#encoding: utf-8

#tcp代理
#可用于转发，或者估计基于网络的软件
#因为经过这个代理的数据都会以16进制输出
#可以查看相关的数据包，从而理解协议

import sys
import socket
import threading

#这个漂亮的十六进制导出函数是从http://code.activestate.com/recipes/142812-hex-dumper/
#获得[
#修改为python3, 把isinstance(src,unicode), 改为str
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = (' '.join(["%0*X" % (digits, x) for x in s]))
        text = (''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s]))
        result.append('%04X  %-*s  %s' % (i, length*(digits + 1), hexa, text))
    print(('\n'.join(result)))

#hexdump(b"USER testy..")

#接收数据
def receive_from(connection):

    buff = b''

    #设置两秒超时， 这取决于目标的情况，可能需要调整
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)
            buff += data
            if len(data) < 4096:
                break
    except:
        pass

    return buff


#绑定代理的服务器
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
        server.listen(5)
    except:
        print('[!!] Failed to listen on {0}:{1}'.format(local_host, local_port))
        print('[!!] Check for other listening sockets or correct permissions or other port')
        sys.exit(0)

    print('[*] Listening on {0}:{1}'.format(local_host, local_port))

    while True:
        client_socket, addr = server.accept()

        print('[==>] Received incoming connection from {0}:{1}'.format(addr[0],
            addr[1]))
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,
            remote_host, remote_port, receive_first))
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    remote_socket.connect((remote_host, remote_port))

    if receive_first:

        remote_buff = receive_from(remote)

        if len(remote_buff):
            hexdump(remote_buff)
            remote_buff = response_handler(remote_buff)
            print('[<==] Sending {0} bytes to localhost!'.format(len(remote_buff)))
            client_socket.send(remote_buff)
            print('[<==] Sent to remote')

    #循环读取数据， 发送给远程主机和本地主机
    while True:

        #先从本地 --> 远程
        local_buff = receive_from(client_socket)

        if len(local_buff):
            hexdump(local_buff)
            local_buff = request_handler(local_buff)
            print('[==>] Sending {0} bytes to remote!'.format(len(local_buff)))
            remote_socket.send(local_buff)
            print('[==>] Sent to remote')

        remote_buff = receive_from(remote_socket)
        
        if len(remote_buff):
            hexdump(remote_buff)
            remote_buff = response_handler(remote_buff)
            print('[==>] Send {0} bytes to local!'.format(len(remote_buff)))
            client_socket.send(remote_buff)
            print('[==>] Sent to local')

        if not len(local_buff) and not len(remote_buff):
            client_socket.close()
            remote_socket.close()
            print('[*] No more data. Closing connections.')
            break

# 对目标是远程主机的请求进行修改
def request_handler(buff):
    
    #执行包修改

    return buff

# 对目标是本地主机的响应进行修改
def response_handler(buff):

    #执行包修改

    return buff

def main():

    #简单提示
    if len(sys.argv[1:]) != 5:
        print('Usage: ./tcp_agent.py [localhost] [localport] [remotehost] [remoteport] [receive_first]')
        print('Example: ./tcp_agent.py 127.0.0.1 1080 10.10.10.1 1080 True')
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
