#!/usr/bin/python
# -*- coding: UTF-8 -*-


import pymysql
import json

'''
import MySQLdb

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

#连接数据库
db = pymysql.connect("localhost","root","469312","test")

#使用cursor()方法创建一个游标对象
cursor = db.cursor()

#使用execute()方法执行SQL语句
cursor.execute("SELECT VERSION()")

#使用fetall()获取全部数据
data = cursor.fetchone()

#打印获取到的数据
print(data)

#关闭游标和数据库的连接
cursor.close()
db.close()
