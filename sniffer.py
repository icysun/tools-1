#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#嗅探的数据包，对于tcp，udp的数据包，只嗅探指定端口的数据包
#仅适合64位的 linux系统
#使用socket 实现
#当然使用scapy 实现更加容易

import socket
import sys
import struct
import threading
from ctypes import *

"""
class IP(Structure):
    _fields_ = [
            ('ihl',                 c_ubyte, 4),
            ('version',             c_ubyte, 4),
            ('tos',                 c_ubyte),
            ('len',                 c_ushort),
            ('id',                  c_ushort),
            ('offset',              c_ushort),
            ('ttl',                 c_ubyte),
            ('protocol_num',        c_ubyte),
            ('sum',                 c_ushort),
            ('src',                 c_uint32),
            ('dst',                 c_uint32)
            ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        self.protocol_map = {1:'ICMP', 6:'TCP', 17:'UDP'}

        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):

    _fields_ = [
            ('type',                c_ubyte),
            ('code',                c_ubyte),
            ('checksum',            c_ushort),
            ('unused',              c_ushort),
            ('next_hop_mut',        c_ushort)
            ]
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        pass

class TCP(Structure):

    _fields_ = [
            ('sour_port',           c_ushort),
            ('dest_port',           c_ushort),
            ('seq_num',             c_uint32),
            ('ack_num',             c_uint32),
            ('header_len',          c_ubyte),
            ('flag',                c_ubyte),
            ('window_size',         c_ushort),
            ('checksum',            c_ushort),
            ('surgent_poiinter',    c_ushort)
            ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.header_len = self.header_len >> 4 

class UDP(Structure):

    _fields_ = [
            ('sour_port',           c_ushort),
            ('dest_port',           c_ushort),
            ('length',              c_ushort),
            ('checksum',            c_ushort)
            ]
    
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        pass
"""


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = (' '.join(["%0*X" % (digits, x) for x in s]))
        text = (''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s]))
        result.append('%04X  %-*s  %s' % (i, length*(digits + 1), hexa, text))
    print(('\n'.join(result)))

def ip_handler(raw_buffer):
           
    iph = struct.unpack('!BBHHHBBH4s4s', raw_buffer[:20])

    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF

    ttl = iph[5]
    protocol_map = {1:'ICMP', 6:'TCP', 17:'UDP'}
    try:
        protocol = protocol_map[iph[6]]
    except:
        protocol = str(iph[6])

    src_address = socket.inet_ntoa(iph[8])
    dst_address = socket.inet_ntoa(iph[9])

    return (ihl, protocol, src_address, dst_address) 

def tcp_handler(tcp_sniffer, port):
    try:
        while True: 
            raw_buffer = tcp_sniffer.recvfrom(65565)[0]

            iph = ip_handler(raw_buffer)
            offset = iph[0] * 4
            buf = raw_buffer[offset:offset + 20]
            tcph = struct.unpack('!HHLLBBHHH' , buf)
 
            sour_port = tcph[0]
            dest_port = tcph[1]
            tcph_length = tcph[4] >> 4
            protocol = iph[1]

            if sour_port == port or dest_port == port:

                print(protocol)
                print("TCP: {}:{} -> {}:{}"\
                        .format(iph[2],sour_port,
                            iph[3],dest_port))

                data = raw_buffer[offset + tcph_length * 4:]
                hexdump(data)

    except KeyboardInterrupt:
        print("Good Bye")
        os.kill(os.getpid(), signal.SIGINT)

    except Exception as e:
        print(e)

def udp_handler(udp_sniffer, port):
    try:
        while True:
            raw_buffer = udp_sniffer.recvfrom(65565)[0]
            
            iph = ip_handler(raw_buffer)
            offset = iph[0] * 4
            buf = raw_buffer[offset:offset + 8]
            udph = struct.unpack("!HHHH", buf)

            sour_port = udph[0]
            dest_port = udph[1]
            protocol = iph[1]

            if sour_port == port or dest_port == port:

                print(protocol)
                print("UDP: {}:{} -> {}:{}"\
                        .format(iph[2],sour_port,
                            iph[3],dest_port))

                data = raw_buffer[offset + 8:]
                hexdump(data)
    except KeyboardInterrupt:
        print("Good Bye")
        os.kill(os.getpid(), signal.SIGINT)

def icmp_handler(icmp_sniffer):
    try:
        while True:
    
            raw_buffer = icmp_sniffer.recvfrom(65565)[0]
            iph = ip_handler(raw_buffer)

            offset = iph[0] * 4
            buf = raw_buffer[offset:offset + 8]
            icmph = struct.unpack("!BBHHH", buf)
            protocol = iph[1]

            print(protocol)
            print("ICMP: {} -> {} type: {} Code: {}"\
                    .format(iph[2], iph[3],
                        icmph[0],icmph[1]))

    except KeyboardInterrupt:
        print("Good Bye")
        os.kill(os.getpid(), signal.SIGINT)

if __name__ == '__main__':

    if len(sys.argv[1:]) == 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("嗅探，指定端口的数据， 目前可以解析tcp, udp, icmp")
        print("Usage: ./sniffer.py host port")
        print("Example: ./sniffer.py 127.0.0.1 8085")
        sys.exit(1)

    sniffer_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    sniffer_tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    sniffer_udp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

    #sniffer_icmp.bind((host, 0))

    #sniffer_icmp.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    #sniffer_tcp.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    #sniffer_udp.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    icmp_thread = threading.Thread(target=icmp_handler, args=(sniffer_icmp,))
    tcp_thread  = threading.Thread(target=tcp_handler, args=(sniffer_tcp, port))
    udp_thread  = threading.Thread(target=udp_handler, args=(sniffer_udp, port))

    icmp_thread.start()
    tcp_thread.start()
    udp_thread.start()
