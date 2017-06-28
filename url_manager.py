# coding:utf8
'''
Created on 2017-06-09
ieee_spider url管理器
@author: xiejing
'''
import MySQLdb

#URL管理器
class UrlManager(object):
    def __init__(self,conn):
        self.conn = conn    #数据库连接
        
    def is_url_exist(self, url, UrlSet_tableName):
        cursor = self.conn.cursor()
        try:
            sql = "select * from %s where url=\"%s\"" %(UrlSet_tableName,url)    #注意%s要加''符号表示是字符串
#             print "is_url_exist:"+sql
            cursor.execute(sql)
            rs = cursor.fetchall()
#             print "len(rs):",len(rs)
            if len(rs)!=0:  #查询结果个数不为0，则表示该url已在表中存在
#                 print 'URL已存在：%s'%url
                return True
            else:
                return False              
        finally:
            cursor.close()
        
    
    def add_url_to_dbUrlSetTable(self, url, UrlSet_tableName):
        cursor = self.conn.cursor()         
        try:                            
            sql = "insert into %s(url,isCrawled) values(\"%s\",%s)" %(UrlSet_tableName,url,False)
            cursor.execute(sql)
            self.conn.commit()  #提交数据库事务 
        finally:
            cursor.close()
    
    def add_uncrawled_url(self,url,UrlSet_tableName):
        if url is None:
            return
        
        if(self.is_url_exist(url,UrlSet_tableName)): #判断是否已经存在
            return
        else:
            self.add_url_to_dbUrlSetTable(url,UrlSet_tableName)      
        
         
    def add_uncrawled_urls(self,urls,UrlSet_tableName):  #添加多个新的url到待爬取集合中
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_uncrawled_url(url,UrlSet_tableName)
    
    def has_uncrawled_url(self,UrlSet_tableName):    #是否还有待爬取的Url
        cursor = self.conn.cursor()
        try:
            sql = "select * from %s where isCrawled=%s" %(UrlSet_tableName,False)
#             print "has_uncrawled_url:"+sql
            cursor.execute(sql)
            rs = cursor.fetchall()
#             print len(rs)
            if len(rs)!=0:  #查询结果个数不为0，则表示还有待爬取的url
#                 print '还有待爬取的URL'
                return True
            else:
#                 print '无待爬取的URL'
                return False              
        finally:
            cursor.close()
         
         
    def get_uncrawled_url(self,UrlSet_tableName):  #从数据库中获得新待爬取的url
        cursor = self.conn.cursor()
        try:
            sql = "select url from %s where isCrawled=%s" %(UrlSet_tableName,False)
#             print "get_uncrawled_url:"+sql
            cursor.execute(sql)
            uncrawled_url = cursor.fetchone()[0]
            #print "url=%s" %uncrawled_url
        finally:
            cursor.close()
        return uncrawled_url

    
    def set_url_crawled(self, uncrawled_url,UrlSet_tableName):
        cursor = self.conn.cursor()
                                            
#         print uncrawled_url
        try:
            sql = "update %s set iscrawled=%s where url=\"%s\"" %(UrlSet_tableName,True,uncrawled_url)
            cursor.execute(sql)
            self.conn.commit()  #提交数据库事务 
        finally:
            cursor.close()    
    
if __name__=="__main__":
    print 'Test ieee_url_manager:'
    #数据库连接
    conn = MySQLdb.connect(
                    host = '127.0.0.1',
                    port = 3306,
                    user = 'root',
                    passwd = 'ruijie@123',
                    db = 'spider_db',
                    charset = 'utf8'
                   )
        
    obj_UrlManager = UrlManager(conn)
    
    url = "http://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=UHF%20RFID"
    
    try:
        obj_UrlManager.add_uncrawled_url(url)
        
        obj_UrlManager.has_uncrawled_url()
        
        uncrawled_url=obj_UrlManager.get_uncrawled_url()
        print "uncrawled_url = %s" %uncrawled_url
        
        obj_UrlManager.set_url_crawled(uncrawled_url)
        
        conn.commit() 
    except Exception as e:
        conn.rollback()
        print "出现问题："+str(e)
    finally:
        conn.close()
    
    