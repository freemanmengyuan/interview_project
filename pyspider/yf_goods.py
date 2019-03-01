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
        self.s_tasks = self.read_log('/root/workspace/python/icode/category_2019-01-06.log')
        #self.goods = list()
        #self.db = pymysql.connect('localhost', 'root', '469312', 'yao_site', charset='utf8')

    #@every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        list_tasks = json.loads(self.s_tasks)
        #print(list_tasks[0:10:1])
        for task in list_tasks:
            #28079
            if task['catch_url'] == 'https://www.yaofang.cn/c/category?cat_id=28079':
                self.crawl(task['catch_url'], callback=self.switch_page,
                    save={'cate_id':task['id'], 'type':task['type'], 'catch_url':task['catch_url']}
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
        cate_url = response.save['catch_url']
        #str_page_count = response.doc('.fp_total').html()
        #print(str_page_count)
        #page_count = re.match('共(\d{1,})件商品', str_page_count).groups()
        page_count = response.doc('.fp_text i').html()
        if page_count is None:
            return
        if int(page_count) == 0:
            return
        if int(page_count) > 1:
            #点击分页列表
            #page_count = int(int(page_count[0])/40)
            #for i in range(page_count+1):
            count = int(page_count)
            for i in range(count):
                pageno = i * 40
                pageno = str(pageno)
                url = cate_url+'&page='+pageno
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
        #print(response.doc('.drug_item').items())
        for bprder in response.doc('.drug_item').items():
            self.crawl(bprder('.drug_item_img a').attr('href'),
                       callback=self.detail_page,
                       save={'cate_id': cate_id, 'type': 3}
                       )

    # 进入详情抽取结构化数据
    @config(priority=2)
    def detail_page(self, response):
        cate_id = response.save['cate_id']
        good_no = response.doc('#gids').val() #商品编号
        name = response.doc('#names').val()
        price = response.doc('#price').val()
        set_num = response.doc('#newKuc').text()
        detail = response.doc('.instructions').html()
        notice = response.doc('.afterSaleService').html()
        img_list = list()
        for img in response.doc('.detail_items img').items():
            img_list.append(img.attr('src'))
            #保存图片至本地
        pic = img_list
        result = {
            'name':name, 'cate_id':cate_id, 'good_no':good_no,
            'price':price,'set_num':set_num, 'pic':pic, 'detail':detail,
            'notice':notice,
        }
        #打印log
        self.write_log(json.dumps(result), 'goods')
        #写入数据库
        #self.add_Mysql(count, url, title, date, day, who, text, image)
        return result
        #self.goods.append(dect)
        #print(self.goods)
    '''
        def on_result(self, result):
        print(result)
    '''
    #写入数据
    def add_record(self, order_num, url, title, date, day, who, text, image):
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

    # 保存图片
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

    #打印log
    def write_log(self, str, name, dir_url='/root/workspace/python/log/'):
        try:
            date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            datetime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
            file = dir_url + name + '-' + date + '.log'
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

