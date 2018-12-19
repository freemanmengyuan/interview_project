#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-10-28
# Project: yao-site

'''
获取商品信息
嵌套抓取
考虑入库效率先写入文件
后续协程入库
'''

from pyspider.libs.base_handler import *
import json
#import MySQLdb
import time
import re
import pymysql
import os

class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.s_tasks = self.read_log('/root/workspace/python/category_2018-10-21.log')
        #self.goods = list()
        self.db = pymysql.connect('localhost', 'root', '469312', 'yao_site', charset='utf8')

    #@every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        list_tasks = json.loads(self.s_tasks)
        #print(list_tasks[0:10:1])
        for task in list_tasks:
            if task['catch_url'] == 'https://www.yaofang.cn/c/category?cat_id=28079':
                self.crawl(task['catch_url'], callback=self.switch_page,
                    save={'cate_id':task['id'], 'type':task['type']}
                ) #添加任务至调度器
        '''
        print(self.goods)
        str_goods = json.dumps(self.goods)
        self.write_log(str_goods)
        '''

    # 判断是否需要请求分页
    #@config(age=10 * 24 * 60 * 60)
    def switch_page(self, response):
        #获取分类id 标示药品分类
        cate_id  = response.save['cate_id']
        str_page_count = response.doc('.fp_total').html()
        #print(str_page_count)
        page_count = re.match('共(\d{1,})件商品', str_page_count).groups()
        if int(page_count[0]) != 0:
            print(page_count) #打印分页数
            if int(page_count[0]) > 40:
                #点击分页列表
                page_count = int(int(page_count[0])/40)
                for i in range(page_count+1):
                    pageno = i * 40
                    pageno = str(pageno)
                    url = 'https://www.yaofang.cn/c/category/?cat_id=28079&page='+pageno
                    print(url)
                    self.crawl(url, callback=self.more_page,save={'cate_id': cate_id})
            else:
                pass
                #self.index_page(response, cate_id)

    def more_page(self, response):
        #获取分类id 标示药品分类
        cate_id  = response.save['cate_id']
        self.index_page(response, cate_id)

    # 点击每个商品
    def index_page(self, response, cate_id):
        print(cate_id)
        #print(response.doc('.drug_item').items())
        for bprder in response.doc('.drug_item').items():
            print(bprder)
            self.crawl(bprder('.drug_item_img a').attr('href'),
                       callback=self.detail_page,
                       save={'cate_id': cate_id, 'type': 3}
                       )

    # 进入详情抽取结构化数据
    @config(priority=2)
    def detail_page(self, response):
        cate_id = response.save['cate_id']
        good_no = response.doc('#gids').val()
        name = response.doc('#names').val()
        price = response.doc('#price').val()
        set_num = response.doc('#newKuc').text()
        detail = response.doc('.instructions').html()
        notice = response.doc('.afterSaleService').html()
        img_list = list()
        for img in response.doc('.detail_items img').items():
            img_list.append(img.attr('src'))
        pic = img_list
        #打印log
        #写入数据库
        #self.add_Mysql(count, url, title, date, day, who, text, image)
        return {
            'name':name, 'cate_id':cate_id, 'good_no':good_no,
            'price':price,'set_num':set_num, 'pic':pic, 'detail':detail,
            'notice':notice,
        }
        #self.goods.append(dect)
        #print(self.goods)
        #exit()
    '''
        def on_result(self, result):
        print(result)
    '''
    #写入数据
    def add_Mysql(self, order_num, url, title, date, day, who, text, image):
        try:
            cursor = self.db.cursor()
            sql = 'insert into qunar(order_num, url, title, date, day, who, text, image) values (%d,"%s","%s","%s","%s","%s","%s","%s")' % (
            order_num, url, title, date, day, who, text, image);  # 插入数据库的SQL语句
            print(sql)
            cursor.execute(sql)
            print(cursor.lastrowid)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()

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

    #读取log
    def read_log(self, file):
        try:
            f = open(file, 'r')
            ret = f.read()
        finally:
            if f:
                f.close()
        return ret

    #保存图片
    def save_img(self, response):
        content = response.content
        file_name = response.save['file_name']
        print(file_name)
        path = os.path.exists(response.save['dir_name'])
        if response.status_code == 200:
            if os.path.exists(path):
                f = open(file_name, 'wb')
                f.write(content)
                print('save img ok')
                f.close()
            else:
                print('dir error')
        else:
            print('save img error')

