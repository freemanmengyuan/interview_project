#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import json
import time

def read_log(file):
    try:
        f = open(file, 'r')
        ret = f.read()
    finally:
        if f:
            f.close()
    return ret

def write_data(data):
    # 打开数据库连接
    db = MySQLdb.connect("ip", "user", "paw", "data_base", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 批量插入
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

print("脚本开始执行。。。。")
file = '/root/workspace/python/category_2019-01-06.log'
str = read_log(file)

print("读取完毕。。。。")
data = json.loads(str)
#print(data)
#data = list[4:6:1]
print("开始写入。。。。")
write_data(data)