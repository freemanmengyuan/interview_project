#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time

def write_log(str, name, dir_url='/root/workspace/python/log/'):
    try:
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        datetime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        file = dir_url + name +'-' + date + '.log'
        f = open(file, 'a+')
        str = datetime +' '+ str + '\n'
        f.write(str)
    finally:
        if f:
            f.close()


def read_log(file):
    try:
        f = open(file, 'r')
        ret = f.read()
    finally:
        if f:
            f.close()
    return ret

def test():
    while True:
        write_log('hello world', 'test')

if __name__ == '__main__':
    test()