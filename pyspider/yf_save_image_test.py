#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-10-28
# Project: yao-site

'''
保存远程图片到本地
'''

from pyspider.libs.base_handler import *
import json
import time
import re
import os

class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.url_list = ['https://img.yaofang.cn/images0/goods/83/5a/7a/IMG_3285293.jpg',
                         'https://img.yaofang.cn/images0/goods/58/78/9a/15830.jpg',
                         'https://img.yaofang.cn/images0/goods/5c/bc/e9/1496.jpg']

    #@every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        #print(list_tasks[0:10:1])
        for url in self.url_list:
            if url:
                self.crawl(url, callback=self.save_img,
                    save={'file_name':url, 'dir_name':'/root/workspace/python/public/images/'}
                ) #添加任务至调度器
        '''
        print(self.goods)
        str_goods = json.dumps(self.goods)
        self.write_log(str_goods)
        '''

    #打印log
    def write_log(self, str, name, file_url='/root/workspace/python/log/'):
        try:
            date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            datetime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
            file = file_url + 'log-' + date + name + '.log'
            f = open(file, 'a+')
            str = datetime + ' ' + str + '\n'
            f.write(str)
        finally:
            if f:
                f.close()

    #保存图片
    def save_img(self, response):
        content = response.content
        base_name = os.path.basename(response.save['file_name'])
        dir_name = response.save['dir_name']
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        file = dir_name + base_name
        if response.status_code == 200:
            if os.path.exists(dir_name):
                f = open(file, 'wb')
                f.write(content)
                self.write_log(file, 'image')
                f.close()
            else:
                self.write_log(dir_name + ' dir error', 'image')
        else:
            self.write_log(file + 'save error', 'image')

