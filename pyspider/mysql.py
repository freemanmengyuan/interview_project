#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import json
import time
'''
try:
    f = open('/root/python/cateropy.log', 'r')
    f.read(f)
finally:
    if f:
        f.close()
# 打开数据库连接
db = MySQLdb.connect("localhost", "root", "469312", "test", charset='utf8' )

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# 使用execute方法执行SQL语句
cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取一条数据
data = cursor.fetchone()

print "Database version : %s " % data

# 关闭数据库连接
db.close()
'''


def read_log():
    try:
        f = open('./cateropy.log', 'r')
        ret = f.read()
    finally:
        if f:
            f.close()
    return ret

def write_data(data):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "root", "469312", "yao_site", charset='utf8')

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

print("读取文件。。。。")

str = read_log()
data = json.loads(str)
#data = list[4:6:1]

write_data(data)