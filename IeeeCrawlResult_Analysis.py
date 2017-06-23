# coding:utf8
'''
Created on 2017-06-21
IEEE爬取数据库表ieee_uhfrfid_data爬取结果分析（漏爬补爬）
@author: xiejing
'''
import MySQLdb

class IeeeCrawlResultAnalysis(object):
    def __init__(self,conn):
        self.conn = conn
    
    def get_UrlSearch_Count(self):  #统计ieee_uhfrfid_data表中不同url_search的个数存入UrlSearchCount表中
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
    
    def classify_UrlSearch_by_failReason(self): #将爬取论文数目小于25的搜索结果页url按失败原因划分到不同的数据库表（urlset_QuoteAbnormal\FormatAbnormal\SameTitle\DownloadLost）中
        #执行前注意清空相应数据库表数据，否则会重复插入
        print "classify_UrlSearch_by_failReason:"
        cursor = self.conn.cursor()
        try:
            sql = "Select * from UrlSearchCount where result_count<25"
            cursor.execute(sql)
                
            rs = cursor.fetchall()
            print "len(rs):",len(rs)
            for row in rs:
#                 print row[0],row[1]
                url_search = row[0]
                result_count = row[1]
#                 print url_search
#                 print url_search[83:-15]    #获得页码
                if url_search[83:-15] == "82" or url_search[83:-15] == "85" or url_search[83:-15] == "89" or url_search[83:-15] == "103" or url_search[83:-15] == "126":
                    sql = "insert into urlset_FormatAbnormal(url,isCrawled) values('%s',%s)"%(url_search,False)
                    cursor.execute(sql)               
                elif result_count==0 or url_search[83:-15]=="23" or url_search[83:-15]=="93":
                    sql = "insert into urlset_DownloadLost(url,isCrawled) values('%s',%s)"%(url_search,False)
                    cursor.execute(sql)
                elif result_count>=1 and result_count <=20:
                    sql = "insert into urlset_QuoteAbnormal(url,isCrawled) values('%s',%s)"%(url_search,False)
                    cursor.execute(sql)
                elif result_count==23 or result_count==24:
                    sql = "insert into urlset_SameTitle(url,isCrawled) values('%s',%s)"%(url_search,False)
                    cursor.execute(sql)
                    
        finally:
            cursor.close() 
    
if __name__=="__main__":
    print 'Test IeeeCrawlResultAnalysis:'
         
    #数据库连接
    conn = MySQLdb.connect(
                    host = '127.0.0.1',
                    port = 3306,
                    user = 'root',
                    passwd = 'ruijie@123',
                    db = 'spider_db',
                    charset = 'utf8'
                   )
            
    obj_IeeeDataAnalysis = IeeeCrawlResultAnalysis(conn) 
    
    try:
#         obj_IeeeDataAnalysis.get_UrlSearch_Count()
#         obj_IeeeDataAnalysis.classify_UrlSearch_by_failReason()    #执行前要清空对应数据库表
            
        conn.commit()   
    except Exception as e:
        conn.rollback()
        print "出现问题："+str(e)
    finally:
        conn.close()
    