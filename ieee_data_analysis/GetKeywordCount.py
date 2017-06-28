# coding:utf8
'''
Created on 2017-06-26
IEEE UHF RFID论文关键词词频统计分析
@author: xiejing
'''

import MySQLdb

ieeeuhfrfid_data_tablename = "ieee_uhfrfid_data"    #存储了各种数据的数据表名
keyword_count_tablename = "keyword_count_ieeeuhfrfid"   #关键字对应次数统计结果表名

Statistical_start_year = 2013   #min:1990
Statistical_end_year = 2017     #max:2017
keyword_count_tablename = keyword_count_tablename +str(Statistical_start_year)+"_"+str(Statistical_end_year)
print "keyword_count_tablename:"+keyword_count_tablename

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

# 1 从数据库中读出非空关键字信息
# print "从数据库中读出非空关键字信息..."
# sql = "Select keywords from "+ieeeuhfrfid_data_tablename+" where keywords!=''"

print "从数据库中读出近",Statistical_end_year-Statistical_start_year+1,"年的非空关键字信息..."
sql = "Select keywords from "+ieeeuhfrfid_data_tablename+" where keywords!='' and date_year>="+str(Statistical_start_year)
print sql

cursor.execute(sql)
print "cursor.rowcount=",cursor.rowcount
rs = cursor.fetchall()
  
keyword_dic = {}
  
print "按逗号进行分词并统计各个关键词出现的次数..."
for row in rs:
    #2 按逗号进行分词
#     print "keywords=",row
#     print row.__str__()
#     print row.__str__()[3:-3]
#     print row.__str__().split(',')
#     print row.__str__()[3:-3].split(',')   
    keyword_list = row.__str__()[3:-3].split(',') #元组tuple转字符串，去掉头尾的(u'和',)并按逗号分词=>获得关键词列表
       
    #3 字典分类统计关键词出现的次数
    for index in range(len(keyword_list)):
#         print index,keyword_list[index]
        cur_keyword = keyword_list[index].lower()   #获得当前的关键字,转换成小写字母
        if cur_keyword in keyword_dic:
            #如果当前关键字已在字典中存在，则增加该关键字的次数一次
            keyword_dic[cur_keyword]=keyword_dic[cur_keyword]+1
#             print keyword_dic[cur_keyword]
        else:
            #当前关键字在字典中不存在，则初始化关键字次数为1
            keyword_dic[cur_keyword]=1
#             print "初始化成功：",cur_keyword,keyword_dic[cur_keyword]
           
#         print "keyword_dic:",keyword_dic     
   
print "len(keyword_dic)=",len(keyword_dic)
   
#4 统计结果输出到数据库中
print "统计结果输出到数据库中..."
sql = "delete from "+keyword_count_tablename    #先清空数据库
print sql
cursor.execute(sql)
for key in keyword_dic:
#     print key,keyword_dic[key]
    sql = "insert into "+keyword_count_tablename+"(keyword,count) values(\"" +key+"\","+str(keyword_dic[key])+")"
#     print sql
    cursor.execute(sql)
try:
    conn.commit()
except Exception as e:
    print "出现问题：",str(e)
  
print "finish"
  
cursor.close()
conn.close()

