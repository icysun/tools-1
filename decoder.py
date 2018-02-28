#!/usr/bin/env python3
#-*- coding:utf-8 -*-

####################################################
#解码器 编码器
#可以实现url unicode html ASCII hex base 解码 编码
####################################################

import sys
import getopt
import string
from base64 import b64encode, b64decode
from urllib.parse import quote, unquote

def usage():
    print('+----------------------------------------------------------------------------+')
    print(' -h                          打印帮助文档')
    print(' -a                          ASCII 编码')
    print(' -b                          ASCII 解码, 只支持单个字符解码，0x - 16,')
    print('                                 0o - 8进制， 没有前缀代表10进制')
    print(' -c                          url 全编码,对于中文等非ascii字符，')
    print('                                 可以指定编码的类型，如gb2312,默认为utf-8')
    print(' -d                          url 部分编码,同样可以指定编码类型，默认为utf-8')
    print(' -e                          url 解码, 可以指定解码的类型，如 gb2312,')
    print('                                 默认为 utf-8')
    print(' -f                          unicode 编码,只支持ascii码，')
    print('                                 如：abc --> \\u0097\\u0098\\0099')
    print(' -g                          unicode 解码,需指定编码类型，如gb2312,')
    print('                                 默认为 utf-8,支持\\x,\\u,\%u模式')
    print(' -k                          hex 编码')
    print(' -i                          hex 解码')
    print(' -j                          url 长编码，可指定编码如utf-32,utf-16,')
    print('                                 把空字符也一起输出如:%00a%00b')
    print('                                 只支持ascii字符，主要用于过waf')
    print(' -n                          html编码,只支持ascii码')
    print(' -l                          html部分编码。')
    print(' -m                          html解码')
    print(' -o                          base编码')
    print(' -p                          base解码')
    print('Example:')
    print('     ./decoder -c str gb2312     //对str进行url编码，对于非ascii码字符将')
    print('                                 //进行gb2312编码')
    print('     ./decoder -e str gb2312     //对str进行url解码，对于非ascii码字符将')
    print('                                 //进行gb2312编码')
    print('     ./decoder -f str gb2312     //对str进行gb2312编码')
    print('     ./decoder -g str gb2312     //对str进行gb2312解码，可以接受\\x,\\u两者模式')
    print('+----------------------------------------------------------------------------+')

def main():
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ha:b:c:d:e:f:g:k:i:j:n:m:o:p:l:')
    except getopt.GetoptError as e:
        print(e)
        usage()
        sys.exit(1)

    for o,a in opts:
        if o == '-h':
            usage()
        elif o == '-a':
            ascii_encode(a)
        elif o == '-b':
            ascii_decode(a)
        elif o == '-c':
            url_all_encode(a, args[0] if args else 'utf-8')
        elif o == '-d':
            url_encode(a, args[0] if args else 'utf-8')
        elif o == '-e':
            url_decode(a, args[0] if args else 'utf-8')
        elif o == '-f':
            unicode_encode(a, args[0] if args else 'utf-8')
        elif o == '-g':
            unicode_decode(a, args[0] if args else 'utf-8')
        elif o == '-k':
            hex_encode(a)
        elif o == '-i':
            hex_decode(a)
        elif o == '-j':
            url_long_decode(a, args[0] if args else 'utf-8')
        elif o == '-n':
            html_all_encode(a)
        elif o == '-l':
            html_encode(a)
        elif o == '-m':
            html_decode(a)
        elif o == '-o':
            base_encode(a)
        elif o == '-p':
            base_decode(a)

def ascii_encode(s):
    result  = ''
    result1 = ''
    result2 = ''
    result3 = ''
    result4 = ''
    for i in s:
        result  = result + str(ord(i))
        result1 = result1 + str(oct(ord(i)))[2:]
        result2 = result2 + str(hex(ord(i)))[2:]
        result3 = result3 + '\\' + str(oct(ord(i)))[2:]
        result4 = result4 + '\\x' + str(hex(ord(i)))[2:]
    print('Result:')
    print('十进制   ：{0}'.format(result))
    print('八进制   ：0o{0}'.format(result1))
    print('十六进制 ：0x{0}'.format(result2))
    print('八进制   ：{}'.format(result3))
    print('十六进制 ：{}'.format(result4))


def ascii_decode(s):
    result  = ''
    result1 = ''
    result2 = ''

    if s[:2] == '0x':
        result2 = result2 + chr(int(ss,16))
        print('Result: {}'.format(result2))

    elif s[:2] == '0o':
        result1 = result1 + chr(int(s,8))
        print('Result: {}'.format(result1))
    else:
        result = result + chr(int(s))
        print('Result: {}'.format(result))

def url_all_encode(s, t):
    result = ''
    for i in s:
        if i in string.printable:
            result = result + '%' + hex(ord(i))[2:]
        else:
            result = result + quote(i, encoding=t)
    print("Result: {}".format(result))

def url_encode(s, t):
    print("Result: {}".format(quote(s, encoding=t)))

def url_decode(s, t):
    print("Result: {}".format(unquote(s,encoding=t)))

def url_long_decode(s, t):
    s = str(s.encode(t))[1:]
    print("Result:  {}".format(s.replace('\\x', '%')))

def unicode_encode(s, t):
    result = ''
    for ss in s:
        result = result + '\\u00' + str(hex(ord(ss))[2:])
    print('Result: {}'.format(result))

def unicode_decode(s, t):
    re = []
    if s[0:2] == '\\x':
        for i in s.split('\\x')[1:]:
            j = 0
            while j < len(i):
                re.append(int(i[j:j+2], 16))
                j = j + 2
        ss = bytearray(re)
    elif s[0:2] == '\\u':
        for i in s.split('\\u')[1:]:
            j = 0
            while j < len(i):
                re.append(int(i[j:j+2], 16))
                j = j +2
        print(re)
        ss = bytearray(re)
        print(ss)
    elif s[0:2] == '%u':
        for i in s.split('%u')[1:]:
            j = 0
            while j < len(i):
                re.append(int(i[j:j+2], 16))
                j = j + 2
        ss = bytearray(re)
    print('Result: {}'.format(ss.decode(t)))

def hex_encode(s):
    result = ''
    for ss in s:
        result = result + str(hex(ord(ss))[2:])
    print('Result:  {}'.format(result))

def hex_decode(s, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = (' '.join(["%0*X" % (digits, x) for x in s]))
        text = (''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s]))
        result.append('%04X  %-*s  %s' % (i, length*(digits + 1), hexa, text))
    print(('\n'.join(result)))

def html_all_encode(s):
    result = ''
    for ss in s:
        result = result + '&#' + str((ord(ss))) + ';'
    print('Result:  {}'.format(result))

def html_encode(s):
    result = ''
    dic = {' ': '&nbsp;', '<': '&lt;', '>': '&gt;', 
            '&': '&amp;', '"': '&quot;', '\'': '&apos;',
            '   ': '&Tab;', '(': '&lpar;', ')': '&rpar;',
            '.': '&period;', ':': '&colon;'}

    for ss in s:
        if ss in dic.keys():
            result = result + dic[ss]
        else:
            result = result + ss
    print('Result:  {}'.format(result))

def html_decode(s):
    result = ''
    for ss in s.split(';'):
        if ss:
            result = result + chr(int(ss[2:]))
    print('Result:  {}'.format(result))

def base_encode(s):
    print('Result:  {}'.format(b64encode(s.encode('utf-8')).decode('utf-8'))) 

def base_decode(s):
    print('Result:  {}'.format(b64decode(s.encode('utf-8')).decode('utf-8')))


if __name__ == '__main__':
    main()
