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

class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.s_tasks = self.read_log('/root/workspace/python/category_2018-10-21.log')
        self.goods = list()

    #@every(minutes=24 * 60)
    def on_start(self):  # 脚本入口
        list_tasks = json.loads(self.s_tasks)
        #print(list_tasks[0:10:1])
        for task in list_tasks:
            if task['type'] == 3:
                self.crawl(
                    task['catch_url'], callback=self.switch_page,
                    save={'cate_id':task['id'], 'type':task['type']}
                )
        '''
        print(self.goods)
        str_goods = json.dumps(self.goods)
        self.write_log(str_goods)
        '''
        #self.crawl(self.url, callback=self.index_page)  # 添加任务至调度器

    # 判断是否需要请求分页
    #@config(age=10 * 24 * 60 * 60)
    def switch_page(self, response):
        #获取分类id 标示药品分类
        cate_id  = response.save['cate_id']
        str_page_count = response.doc('.fp_total').html()
        #print(str_page_count)
        page_count = re.match('共(\d{1,2})件商品', str_page_count).groups()
        if int(page_count[0]) != 0:
            print(page_count) #打印分页数
            if int(page_count[0]) > 20:
                pass
                #self.reload_page(response, cate_id)
            else:
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

    # 点击进入详情
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
    def write_log(self, str):
        try:
            ctime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            f = open('/root/workspace/python/goods_'+ctime+'.log', 'w')
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


