# coding:utf8
'''
Created on 2017-06-09
ieee_spider MySql输出器
@author: xiejing
'''
import re

#MySql输出器
class MySqlOutputer(object):
    
    def __init__(self,conn):
        self.conn = conn
  
    def _replace_double_quotoes(self, data_str):    #将字符串中的双引号替换成单引号
        #将字符串中的一个或多个连续的双引号替换成单个引号
#         print "data_str:",data_str
        strinfo = re.compile(r'"')
#         print "strinfo:",strinfo
        data_res =strinfo.sub("'",data_str)
#         print "data_res:",data_res
        return data_res
    
    def output_basedatas(self, base_datas,data_table_name):   #将搜索结果页论文数据插入到数据库中
        cursor = self.conn.cursor()
        
        try:
            for data in base_datas: 
                url_search = self._replace_double_quotoes(data['url'])
                url_document = ''
                title = self._replace_double_quotoes(data['title'])
                abstract = self._replace_double_quotoes(data['abstract'])
                keywords = self._replace_double_quotoes(data['keywords'])
                journal = self._replace_double_quotoes(data['journal'])
                date = self._replace_double_quotoes(data['date'])
                
                #IEEE_UHFRFID_Data
                #先判断该标题的论文数据在数据库中是否已经存在，若不存在则插入，存在则不插入(注意双引号的使用！)
                sql = "select * from %s where title = \"%s\"" %(data_table_name,title)
    #             print "output_dbData sql-select:"+sql 
                cursor.execute(sql)
                rs = cursor.fetchall()
    #             print "len(rs):",len(rs)
                if len(rs)==0:  #不存在，插入
                    sql = "insert into %s(url_search,url_document,title,abstract,keywords,journal,date) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(data_table_name,url_search,url_document,title,abstract,keywords,journal,date)
    #                 print "output_dbData sql-insert:"+sql  
                    cursor.execute(sql)               
                else:
                #存在，只更新url_search
                    sql = "update %s set url_search=\"%s\" where title=\"%s\""%(data_table_name,url_search,title)
    #                 print "output_dbData sql-insert:"+sql  
                    cursor.execute(sql)               
                
                self.conn.commit()  #提交数据库事务                
        finally:
            cursor.close()                      
                
                   
    def output_detaildata(self,detail_data,data_table_name):   #用详细页论文信息补全更新数据库表原有信息
        cursor = self.conn.cursor()
        
        try:
            url_document = self._replace_double_quotoes(detail_data['url'])
            title = self._replace_double_quotoes(detail_data['title'])
            abstract = self._replace_double_quotoes(detail_data['abstract'])
            keywords = self._replace_double_quotoes(detail_data['keywords'])
            journal = self._replace_double_quotoes(detail_data['journal'])
            date = self._replace_double_quotoes(detail_data['date'])
                        
            #先判断该标题的论文数据在数据库中是否已经存在，若存在则修改,不存在则插入
            sql = "select * from %s where title = \"%s\"" %(data_table_name,title)
            cursor.execute(sql)
            rs = cursor.fetchall()
    #         print "len(rs):",len(rs)
            if len(rs)!=0:  #存在，修改更新(注意判断插入的数据是否为空以防将原有信息覆盖)
                if journal != '' and date != '':
                    sql = "update %s set url_document=\"%s\",abstract=\"%s\",keywords=\"%s\",journal=\"%s\",date=\"%s\" where title=\"%s\""%(data_table_name,url_document,abstract,keywords,journal,date,title)
    #             print "Update_dbDatas1:",sql  
                elif journal == '' and date != '':
                    sql = "update %s set url_document=\"%s\",abstract=\"%s\",keywords=\"%s\",date=\"%s\" where title=\"%s\""%(data_table_name,url_document,abstract,keywords,date,title)
                elif journal!='' and date == '':
                    sql = "update %s set url_document=\"%s\",abstract=\"%s\",keywords=\"%s\",journal=\"%s\" where title=\"%s\""%(data_table_name,url_document,abstract,keywords,journal,title)
                else:
                    sql = "update %s set url_document=\"%s\",abstract=\"%s\",keywords=\"%s\" where title=\"%s\""%(data_table_name,url_document,abstract,keywords,title)
                
                cursor.execute(sql)   
            else:   #不存在，插入
                sql = "insert into %s(url_document,title,abstract,keywords,journal,date) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(data_table_name,url_document,title,abstract,keywords,journal,date)
    #             print "Update_dbDatas2:",sql  
                cursor.execute(sql)
            
            self.conn.commit()  #提交数据库事务  
        finally:
            cursor.close()
            
                