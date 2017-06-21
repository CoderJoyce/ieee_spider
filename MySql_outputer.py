# coding:utf8
'''
Created on 2017-06-09
ieee_spider MySql输出器
@author: xiejing
'''

#MySql输出器
class MySqlOutputer(object):
    
    def __init__(self,conn):
        self.conn = conn
  
    def output_basedatas(self, base_datas):   #将搜索结果页论文数据插入到数据库中
        cursor = self.conn.cursor()
        
        try:
            for data in base_datas: 
                url_search = data['url']
                url_document = ''
                title = data['title'].encode('utf-8')   #utf-8防止中文乱码
                abstract = data['abstract'].encode('utf-8')
                keywords = data['keywords'].encode('utf-8')
                journal = data['journal'].encode('utf-8')
                date = data['date'].encode('utf-8')
                            
                #先判断该标题的论文数据在数据库中是否已经存在，若不存在则插入，存在则不插入
                sql = "select * from IEEE_UHFRFID_Data where title = \"%s\"" %title
    #             print "output_dbData sql-select:"+sql 
                cursor.execute(sql)
                rs = cursor.fetchall()
    #             print "len(rs):",len(rs)
                if len(rs)==0:  #不存在，插入
                    sql = "insert into IEEE_UHFRFID_Data(url_search,url_document,title,abstract,keywords,journal,date) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(url_search,url_document,title,abstract,keywords,journal,date)
    #                 print "output_dbData sql-insert:"+sql  
                    cursor.execute(sql)               
                    self.conn.commit() 
        finally:
            cursor.close()                      
                
                   
    def output_detaildata(self,detail_data):   #用详细页论文信息补全更新数据库表原有信息
        cursor = self.conn.cursor()
        
        try:
            url_document = detail_data['url'].encode('utf-8') 
            title = detail_data['title'].encode('utf-8')   #utf-8防止中文乱码
            abstract = detail_data['abstract'].encode('utf-8')
            keywords = detail_data['keywords'].encode('utf-8')
            journal = detail_data['journal'].encode('utf-8')
            date = detail_data['date'].encode('utf-8')
                        
            #先判断该标题的论文数据在数据库中是否已经存在，若存在则修改,不存在则插入
            sql = "select * from IEEE_UHFRFID_Data where title = \"%s\"" %title
            cursor.execute(sql)
            rs = cursor.fetchall()
    #         print "len(rs):",len(rs)
            if len(rs)!=0:  #存在，修改更新
                sql = "update IEEE_UHFRFID_Data set url_document=\"%s\",abstract=\"%s\",keywords=\"%s\",journal=\"%s\",date=\"%s\" where title=\"%s\""%(url_document,abstract,keywords,journal,date,title)
    #             print "Update_dbDatas1:",sql  
                cursor.execute(sql)   
            else:   #不存在，插入
                sql = "insert into IEEE_UHFRFID_Data(url_document,title,abstract,keywords,journal,date) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(url_document,title,abstract,keywords,journal,date)
    #             print "Update_dbDatas2:",sql  
                cursor.execute(sql)
        finally:
            cursor.close()
            
                