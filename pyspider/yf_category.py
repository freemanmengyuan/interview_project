#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-08-16 02:18:24
# Project: yao-site

'''
获取分类信息
基础的抓取信息
抓取单页面数据
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
        self.url = 'https://www.yaofang.cn/c/autokey/categoryAll'


    @every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        print(self.url)  # 打印连接
        self.crawl(self.url, callback=self.index_page)  # 添加任务至调度器

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        cate = list()
        one_num = 1
        two_num = 20
        three_num = 200
        # 获取顶级分类
        for menu in response.doc('.yMenuList').items():
            one_cate = menu('.fenleiTit').html()
            one_cate_true = one_cate[50:-1:1] #切片
            #print(one_cate_true)
            dect = {'id':one_num, 'name':one_cate_true, 'type':1, 'parent_id':0, 'catch_url': ''}
            cate.append(dect)
            # 获取二级分类
            for two_menu in menu('dl').items():
                #print(min_menu)
                two_cate_name = two_menu('dt a').text()
                two_cate_url = two_menu('dt a').attr('href')
                dect = {'id':two_num, 'name':two_cate_name, 'type':2, 'parent_id':one_num, 'catch_url':two_cate_url}
                cate.append(dect)
                #获取三级分类
                for min_menu in two_menu('dd a').items():
                    #print(min_menu)
                    min_cate_name = min_menu.text()
                    min_cate_url = min_menu.attr('href')
                    dect = {'id':three_num, 'name':min_cate_name, 'type':3, 'parent_id':two_num, 'catch_url':min_cate_url}
                    cate.append(dect)
                    three_num = three_num + 1
                two_num = two_num + 1
            one_num = one_num + 1
        result = json.dumps(cate)
        print(result)
        self.write_log(result)

        #self.write_data(cate)

    def write_log(self, str):
        try:
            ctime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            f = open('/root/workspace/python/category_'+ctime+'.log', 'w')
            f.write(str)
        finally:
            if f:
                f.close()


    def write_data(self, data):
        # 打开数据库连接
        db = MySQLdb.connect("localhost", "root", "469312", "yao_site", charset='utf8')

        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # SQL批量写入
        try:
            for item in data:
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                sql = "INSERT INTO yf_category(id," \
                      "name, type, parent_id, catch_url, time) \
                      VALUES ('%d', '%s', '%d', '%d', '%s', '%s')" % \
                      (item['id'], item['name'], item['type'], item['parent_id'], item['catch_url'], ctime)
                # 执行sql语句
                print(sql)
                ret = cursor.execute(sql)
                print(ret)
                # 提交到数据库执行
                db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()

        # 关闭数据库连接
        db.close()



