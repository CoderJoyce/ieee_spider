# coding:utf8
'''
Created on 2017-06-23
重新下载加载失败的页面
从文件夹中获得需重新下载的url并添加到数据库表urlset_tableName中
@author: xiejing
'''

from ieee_spider import html_downloader, url_manager, html_parser
import MySQLdb

import logging
from bs4 import BeautifulSoup
import os

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='ieee_spider.log',
                filemode='a')

searchResult_preUrl = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID"
document_preUrl = "http://ieeexplore.ieee.org/document/"

class SpiderMain(object):
    def __init__(self,conn):
        self.urls = url_manager.UrlManager(conn)    #实例化URL管理器
        self.downloader = html_downloader.HtmlDownloader()  #网页下载器
        self.parser = html_parser.HtmlParser()  #网页解析器

    def download_and_save_html(self,urlset_tableName,save_folder_name):
        #开始爬取        
        count = 1
        
        while self.urls.has_uncrawled_url(urlset_tableName):
            try:    
                #1 url管理器取出一个待爬取url
                uncrawled_url = self.urls.get_uncrawled_url(urlset_tableName)  
                print 'crawl %d : %s' %(count,uncrawled_url)
                logging.info('crawl %d : %s'%(count,uncrawled_url))
                
                #2 下载器下载页面
                html_cont = self.downloader.download_ajax(uncrawled_url,5,save_folder_name)  
    #           print html_cont
                print 'download successed'
                logging.info('download successed') 
                
                #【用于测试】：从文件中读取已下载的Html源码               
                #try:
                #    fobj = open("downloadhtml/search22.txt",'r')
                #except IOError:
                #    print "txt file open error"
                #else:
                #    print "读取文件内容..."
                #    html_cont = fobj.read()
                #    fobj.close()
                #    print "Read finished."
                
                #3 解析器解析页面
                #判断待爬取的页面是搜索结果页还是论文详情页：
                #(1)搜索列表页面解析出论文数据及详情页URL
                try:
                    if uncrawled_url[:71] == searchResult_preUrl: 
                        print "待爬取页为搜索结果页："
                        logging.info('待爬取页为搜索结果页') 
                        
                        print "解析结果页..."
                        logging.info('解析结果页...') 
                        
                        soup = BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
                        #print "soup:",soup
                        detail_urls= self.parser._get_detailPage_urls(uncrawled_url,soup)   #解析器解析页面url            
                        print "detail_urls:",detail_urls
                        
                        self.urls.add_uncrawled_urls(detail_urls,urlset_tableName)  #将解析出的多个新url加入到数据库urlset表中
                        
                except Exception as e:
                    #如果解析失败的，则将页面设置为已爬取，否则会一直重复爬取该页面
        #           print "uncrawled_url[:36]:",uncrawled_url[:36]                   
                    self.urls.set_url_crawled(uncrawled_url,urlset_tableName)
                    logging.info('将解析失败页面设置为已爬取: %s'%uncrawled_url) 
                    logging.info('【【解析失败】】: %s'%str(e))        
                    conn.commit()
                
                #5 将页面设置为已爬取
                self.urls.set_url_crawled(uncrawled_url,urlset_tableName)
                logging.info('将爬取成功页面设置为已爬取: %s'%uncrawled_url)  
                        
                try:
                    conn.commit()   #一次循环处理结束时提交所有数据库事务  
                except Exception as e:
                    print 'mysql commit failed'
                    logging.warning("【【mysql commit failed】】:%s"%str(e))
#                     conn.rollback() #回滚（是不是不需要回滚呢??）

                #【用于测试】：控制执行的次数                
#                 if count == 1:
#                     break               

                count = count + 1
            except IOError as e:
                #异常处理：若发生文件写入错误则将当前URL设置为已爬取
                print 'IOError'
                logging.warning("【【IOError】】:%s"%str(e))
                self.urls.set_url_crawled(uncrawled_url,urlset_tableName)
                logging.info('将发生错误异常页面设置为已爬取: %s'%uncrawled_url) 
                
            except Exception as e:            
                print 'crawl failed:',str(e)
                logging.warning("【【crawl failed】】:%s"%str(e))
                                                    
        print '【crawl finished】: crawl count=%d'%count
        logging.info('【crawl finished】: crawl count=%d'%count) 

    
    def get_and_add_url_to_urlset(self, save_folder_name, urlset_tableName):
        count=0
        for file_name in os.listdir(save_folder_name):  
            #print count, file_name 
            if file_name[:6]=="search":
                #print file_name
                page_num = file_name[6:-4]
                #print page_num
                url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber="+page_num+"&newsearch=true"
                #print url
            else:   #document
                #print file_name
                document_num = file_name[8:-4]
                #print document_num
                url = "http://ieeexplore.ieee.org/document/"+document_num+"/"
                #print url
            
            #把获得的url插入数据库表中
            self.urls.add_uncrawled_url(url,urlset_tableName)              
            count= count+1
        
        print "get_and_add_url_to_urlset success!count=",count
    
    
        
#【主入口函数】
if __name__=="__main__":
    print 'ieee_spider crawl begin...' 
    logging.info('【ieee_spider crawl begin】...')
    
    #数据库连接
    conn = MySQLdb.connect(
                    host = '127.0.0.1',
                    port = 3306,
                    user = 'root',
                    passwd = 'ruijie@123',
                    db = 'spider_db',
                    charset = 'utf8'
                   )
    try:
        urlset_tableName = "urlset_Redownload"    #urlset_DownloadLost/urlset_FormatAbnormal
        save_folder_name = "downloadhtml_Redownload"
        obj_spider = SpiderMain(conn)
        
        #从文件夹中获得需重新下载的url并添加到数据库表urlset_tableName中
        obj_spider.get_and_add_url_to_urlset(save_folder_name,urlset_tableName)
           
        obj_spider.download_and_save_html(urlset_tableName,save_folder_name)
        
    except Exception as e:
        print "出现问题："+str(e)
        logging.warning("【【出现问题】】:%s"%str(e))
    finally:
        conn.close()