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
        three_num = 100
        # 获取顶级分类
        for menu in response.doc('.yMenuList').items():
            one_cate = menu('.fenleiTit').html()
            one_cate_true = one_cate[50:-1:1] #切片
            #print(one_cate_true)
            dect = {'id':one_num, 'name':one_cate_true, 'parent_id':0, 'catch_url': ''}
            cate.append(dect)
            # 获取二级分类
            for two_menu in menu('dl').items():
                #print(min_menu)
                two_cate_name = two_menu('dt a').text()
                two_cate_url = two_menu('dt a').attr('href')
                dect = {'id': two_num, 'name': two_cate_name, 'parent_id': one_num, 'catch_url': two_cate_url}
                cate.append(dect)
                #获取三级分类
                for min_menu in two_menu('dd a').items():
                    #print(min_menu)
                    min_cate_name = min_menu.text()
                    min_cate_url = min_menu.attr('href')
                    dect = {'id': three_num, 'name': min_cate_name, 'parent_id': two_num, 'catch_url': min_cate_url}
                    cate.append(dect)
                    three_num = three_num + 1
                two_num = two_num + 1
            one_num = one_num + 1
        result = json.dumps(cate)
        print(result)
        self.write_log(result)

    def write_log(self, str):
        try:
            f = open('/root/python/2018-09-24.log', 'w')
            f.write(str)
        finally:
            if f:
                f.close()



