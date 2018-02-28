#/usr/bin/env python3
#-*- coding:utf-8 -*-

from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import re
import os
import sys


#获取web 的banner 
#顺便使用OPTIONS测试一下可以使用那些HTTP 方法


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.flag = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.flag = False

    def handle_data(self, data):
        if self.flag:
            self.title = data


if len(sys.argv[1:]) != 2:
    print("Usage:" + "\n" +
                "getbanner.py infile outfile" )
    sys.exit(0)

infile = sys.argv[1]
outfile = sys.argv[2]
try:
    os.remove(outfile)
except:
    pass
headers = {'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}

def getbanner(r):
    with urlopen(r, timeout=5) as h:
        try:
            conent = h.read().decode('utf-8')
        except:
            conent = h.read().decode('gb2312')
        p = MyHTMLParser()
        p.feed(conent)
        return p.title

def outputbanner(outfile, url, code, title='', method='', error=''):

    print('Url:     %s' % url)
    print('Code:    %d' % code)
    print('Title:   %s' % title)
    print('Method:  %s' % method)
    if error != '':
        print('Error:   %s' % error)
    
    print('-' * 100)
    with open(outfile, 'a') as f:
        f.write('Url:       %s\n' % url)
        f.write('Code:      %d\n' % code)
        f.write('Title:     %s\n' % title)
        f.write('Method:    %s\n' % method)
        if error != '':
            f.write('Error:   %s\n' % error)
        f.write('-' * 100)

def getmethod(url, headers):
    r = Request(url=url, headers=headers, method='OPTIONS')
    try:
        with urlopen(r) as h:
            return h.headers['Allow']
    except HTTPError as e:
        return str(e)
    except:
        return

with open(infile) as f:
    for url in f:
        try:
            url = 'http://' + url.strip()
            r = Request(url=url, headers=headers)
            title = getbanner(r)
            method = getmethod(url, headers)
            outputbanner(outfile, url, 200,  title, method)
        except KeyboardInterrupt:
            sys.exit(0)

        except HTTPError as e:
            outputbanner(outfile, url, e.code, error=str(e))

        except URLError as e:
            outputbanner(outfile, url, 0, error=str(e))

        except Exception as e:
            outputbanner(outfile, url, 0, error=str(e))
