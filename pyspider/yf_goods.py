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
# import MySQLdb
import time
import re
import pymysql

import os
import sys

import random


class Handler(BaseHandler):
    crawl_config = {
        #'headers':
    }

    def __init__(self):
        #str_log_dir = '/root/workspace/python/icode/category_2019-01-06.log'
        self.s_tasks = self.read_log('/root/workspace/python/icode/category_2019-01-06.log')
        # self.goods = list()
        self.db = pymysql.connect('101.37.125.202', '', '', 'yaodian', charset='utf8')

    # @every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        # 解决图片文件保存失败 报'ascii' codec can't encode characters
        reload(sys)
        sys.setdefaultencoding('utf-8')
        list_tasks = json.loads(self.s_tasks)
        # print(list_tasks[0:10:1])
        #list_tasks = list_tasks[0:10:1]
        for task in list_tasks:
            # 28079 2473
            #if task['catch_url'] == 'https://www.yaofang.cn/c/category?cat_id=2473':
            if task['type'] == 2:
                self.crawl(task['catch_url'], callback=self.switch_page, headers={"User-Agent": self.user_agent()},
                           save={'cate_id': task['id'], 'type': task['type'], 'catch_url': task['catch_url']}
                           )  # 添加任务至调度器
        '''
        print(self.goods)
        str_goods = json.dumps(self.goods)
        self.write_log(str_goods)
        '''

    # 判断是否需要请求分页
    # @config(age=10 * 24 * 60 * 60)
    def switch_page(self, response):
        # 获取分类id 标示药品分类
        cate_id = response.save['cate_id']
        cate_url = response.save['catch_url']
        # str_page_count = response.doc('.fp_total').html()
        # print(str_page_count)
        # page_count = re.match('共(\d{1,})件商品', str_page_count).groups()
        page_count = response.doc('.fp_text i').html()
        if page_count is None:
            return
        if int(page_count) == 0:
            return
        if int(page_count) > 1:
            # 点击分页列表
            # page_count = int(int(page_count[0])/40)
            # for i in range(page_count+1):
            count = int(page_count)
            for i in range(count):
                pageno = i * 40
                pageno = str(pageno)
                url = cate_url + '&page=' + pageno
                self.crawl(url, callback=self.more_page, save={'cate_id': cate_id}, headers={"User-Agent": self.user_agent()},)
        else:
            #pass
            self.index_page(response, cate_id)

    def more_page(self, response):
        # 获取分类id 标示药品分类
        cate_id = response.save['cate_id']
        self.index_page(response, cate_id)

    # 点击每个商品
    def index_page(self, response, cate_id):
        # print(response.doc('.drug_item').items())
        for bprder in response.doc('.drug_item').items():
            self.crawl(bprder('.drug_item_img a').attr('href'),
                       callback=self.detail_page,
                       save={'cate_id': cate_id, 'type': 3}, headers={"User-Agent": self.user_agent()})

    # 进入详情抽取结构化数据
    @config(priority=2)
    def detail_page(self, response):
        name = response.doc('#names').val()  # 商品名
        cate_id = response.save['cate_id']
        good_no = response.doc('#gids').val()  # 商品编号
        # 药品规格 批文号 生产商家 python3版本的正则 字符串截取失效 气人 先保存
        size = response.doc('.info').html()
        # str_info = info.decode('unicode-escape').encode('utf-8')
        # l_info = info.split(u"<br/>")
        # l_info = re.match('规格', info)

        price = response.doc('#price').val()  # 商品价格
        set_num = response.doc('#newKuc').text()  # 库存
        detail = response.doc('.list1').html()  # 说明书
        notice = response.doc('.afterSaleService').html()  # 售后说明
        remote_img_list = list()
        local_img_list = list()
        for img in response.doc('.detail_items img').items():
            url = img.attr('src')
            remote_img_list.append(url)
            # 保存图片至本地
            if url:
                file_name = os.path.basename(url)
                file_name = 'bakserver_'+str(time.time()) + file_name
                local_img_list.append(file_name)
                self.crawl(url, callback=self.save_img,
                    save={'file_name':file_name, 'dir_name':'/root/workspace/public/images/'},
                           headers={"User-Agent": self.user_agent()},
                ) #添加任务至调度器

        remote_img_str = json.dumps(remote_img_list)
        local_img_str = json.dumps(local_img_list)
        ota_name = response.doc('.right_property h1').text()  #供应商名称
        address = response.doc('#alias').val()  #地址
        license = response.doc('.right_property .dll').html()  #许可证
        #local_img_str = ''
        result = {
            'name': name, 'cate_id': cate_id, 'good_no': good_no, 'size': size,
            'price': price, 'set_num': set_num, 'remote_pic': remote_img_str, 'local_pic': local_img_str,
            'detail': detail,
            'notice': notice, 'ota_name':ota_name, 'address':address, 'license':license
        }
        # 打印log
        self.write_log(json.dumps(result), 'goods')
        # 写入数据库
        map_detail = detail.replace("'", "\'")

        self.add_record(name, cate_id, good_no, size, price, set_num, remote_img_str, local_img_str,
                        map_detail, notice, ota_name, address, license)
        return result
        # self.goods.append(dect)
        # print(self.goods)

    '''
        def on_result(self, result):
        print(result)
    '''

    # 写入数据
    def add_record(self, name, cate_id, good_no, size, price, set_num, remote_img_str, local_img_str, detail, notice,
                   ota_name, address, license):
        try:
            cursor = self.db.cursor()
            # 插入数据库的SQL语句
            ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            sql = "INSERT INTO yf_goods(name," \
                  "category_id, good_no, size, price, set_num, remote_pic, local_pic, notice, detail, ota_name, address, license, ctime) \
                  VALUES ('%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s', '%s', '%s', '%s')" % \
                  (name, cate_id, good_no, size, price, set_num, remote_img_str, local_img_str, notice, detail, ota_name, address, license, ctime)
            cursor.execute(sql)
            ret = cursor.lastrowid
            self.db.commit()
            self.write_log('sql success' + str(ret), 'sql')
        except Exception as e:
            # print(e)
            self.write_log('sql success' + str(e), 'sql')
            self.db.rollback()

    # 保存图片
    def save_img(self, response):
        content = response.content
        base_name = response.save['file_name']
        dir_name = response.save['dir_name']
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        file = dir_name + base_name
        if response.status_code == 200:
            if os.path.exists(dir_name):
                f = open(file, 'wb')
                f.write(content)
                f.close()
                self.write_log(file, 'success_image')
            else:
                # self.write_log(dir_name + ' dir error', 'image')
                pass
        else:
            self.write_log(file + 'save error', 'err_image')

    # 打印log
    def write_log(self, str, name, dir_url='/root/workspace/python/pyspider/log/'):
        try:
            date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            file = dir_url + name + '-' + date + '.log'
            f = open(file, 'a+')
            str = datetime + ' ' + str + '\n'
            f.write(str)
        finally:
            if f:
                f.close()

    # 读取log
    def read_log(self, file):
        try:
            f = open(file, 'r')
            ret = f.read()
        finally:
            if f:
                f.close()
        return ret

    # 随机获取user_agent
    def user_agent(self):
        my_headers = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.6.0.18627"
        ]
        return random.choice(my_headers)

    #self.crawl('url', callback=self.index_page,headers={"User-Agent": user_agent()})
