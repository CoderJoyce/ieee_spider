# coding:utf8
'''
Created on 2017-06-27
IEEE UHF RFID论文年份统计
@author: xiejing
'''

import MySQLdb
 
ieeeuhfrfid_data_tablename = "ieee_uhfrfid_data"    #存储了各种数据的数据表名
 
conn = MySQLdb.connect(
                        host = '127.0.0.1',
                        port = 3306,
                        user = 'root',
                        passwd = 'ruijie@123',
                        db = 'spider_db',
                        charset = 'utf8'
                       )
 
cursor = conn.cursor()
 
# print conn
# print cursor
 
#1 从数据库中读出非空日期信息&对应标题信息
print "从数据库中读出非空日期信息&对应标题信息..."
sql = "Select date,title from "+ieeeuhfrfid_data_tablename+" where date!=''"
cursor.execute(sql)
print "cursor.rowcount=",cursor.rowcount
rs = cursor.fetchall()
 
#2 依次截取日期后四位后的年份
print "依次截取日期后四位后的年份..."
for row in rs:
    print row[0]
    year = row[0][-4:]
    print year
     
    #3 将截取到的年份依次添加数据库表中
    sql = "update "+ieeeuhfrfid_data_tablename+" set date_year="+year+" where title=\""+row[1]+"\""
    print sql
    cursor.execute(sql)
      
#一次性统一提交数据库事务
try:
    conn.commit()
except Exception as e:
    print "出现问题：",str(e),",回滚..."
    conn.rollback()
 
print "finish"
 
cursor.close()
conn.close()