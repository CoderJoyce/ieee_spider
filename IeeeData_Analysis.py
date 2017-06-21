# coding:utf8
'''
Created on 2017-06-21
IEEE爬取数据库表ieee_uhfrfid_data分析
@author: xiejing
'''
import MySQLdb

class IeeeDataAnalysis(object):
    def __init__(self,conn):
        self.conn = conn
    
    def get_UrlSearch_Count(self):  #统计ieee_uhfrfid_data表中不同url_search的个数
        cursor = self.conn.cursor()
        try:
            for page_id in range(1,127):
            
                url_search = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber="+str(page_id)+"&newsearch=true"
                print url_search
                sql = "select count(1) FROM `ieee_uhfrfid_data` WHERE url_search='%s'"%url_search
                cursor.execute(sql)
                
                rs = cursor.fetchone()
                count = rs[0]
    #             print "url_search:",url_search
    #             print "count:",count
                
                sql = "select * from UrlSearchCount where url_search='%s'"%url_search
                cursor.execute(sql)
                rs = cursor.fetchall()            
                if len(rs) == 0: #不存在插入
                    print "不存在插入:"+url_search
                    sql = "insert into UrlSearchCount(url_search,result_count) values('%s',%d)" %(url_search,count)
                    cursor.execute(sql)
                else:   #已存在更新
                    print "已存在更新:"+url_search
                    sql = "update UrlSearchCount set url_search='%s',result_count=%d where url_search='%s'" %(url_search,count,url_search)
                    cursor.execute(sql)           
        finally:
            cursor.close()  
        
        
        
if __name__=="__main__":
    print 'Test IeeeDataAnalysis:'
     
    #数据库连接
    conn = MySQLdb.connect(
                    host = '127.0.0.1',
                    port = 3306,
                    user = 'root',
                    passwd = 'ruijie@123',
                    db = 'spider_db',
                    charset = 'utf8'
                   )
          
    obj_IeeeDataAnalysis = IeeeDataAnalysis(conn)
      
    try:
        obj_IeeeDataAnalysis.get_UrlSearch_Count()
        conn.commit()   
    except Exception as e:
        conn.rollback()
        print "出现问题："+str(e)
    finally:
        conn.close()
    