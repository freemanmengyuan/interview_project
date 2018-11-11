#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-10-28
# Project: yao-site

'''
获取商品信息
嵌套抓取
考虑入库效率先写入文件
后续多线程入库
'''

from pyspider.libs.base_handler import *
import json
#import MySQLdb
import time

class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.s_tasks = self.read_log('/root/workspace/python/category_2018-10-21.log')


    @every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        list_tasks = json.loads(self.s_tasks)
        #print(list_tasks[0:10:1])
        for task in list_tasks:
            if task['type'] == 3:
                self.crawl(task['catch_url'], callback=self.index_page, save={'cate_id':task['id'], 'type':task['type']})
        #self.crawl(self.url, callback=self.index_page)  # 添加任务至调度器

    #@config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        #获取分类id 标示药品分类
        cate_id  = response.save['cate_id']
        str_page_count = response.doc('.fp_total').html()
        list_page = list(str_page_count)
        print(list_page)

    def write_log(self, str):
        try:
            ctime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            f = open('/root/workspace/python/category_'+ctime+'.log', 'w')
            f.write(str)
        finally:
            if f:
                f.close()
    def read_log(self, file):
        try:
            f = open(file, 'r')
            ret = f.read()
        finally:
            if f:
                f.close()
        return ret


