# coding:utf8
'''
Created on 2017-06-09
ieee_spider 爬取主函数
@author: xiejing
'''
from ieee_spider import html_downloader, url_manager, html_parser
from ieee_spider import MySql_outputer
import MySQLdb

import logging

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
        self.outputer = MySql_outputer.MySqlOutputer(conn)    #网页输出器
    
    def craw(self, SearchResult_urls_list):
        
        #把所有搜索结果页插入数据库中
        self.urls.add_uncrawled_urls(SearchResult_urls_list)        
        try:  
            conn.commit()   #提交数据库事务
        except Exception as e:
            print 'mysql commit failed'
            logging.warning("【【mysql commit failed】】:%s"%str(e))
#             conn.rollback()   #回滚
                       
        #开始爬取        
        count = 1
        while self.urls.has_uncrawled_url():
            try:    
                #1 url管理器取出一个待爬取url
                uncrawled_url = self.urls.get_uncrawled_url()  
                print 'crawl %d : %s' %(count,uncrawled_url)
                logging.info('crawl %d : %s'%(count,uncrawled_url))
                
                #2 下载器下载页面
                html_cont = self.downloader.download_ajax(uncrawled_url,5)  
    #           print html_cont
                print 'download successed'
                logging.info('download successed') 
                
                #【用于测试】：从文件中读取已下载的Html源码
#                 uncrawled_url = "http://ieeexplore.ieee.org/document/7939286/"
#                 try:
#                     fobj = open("page_source_document7939286.txt",'r')
#                 except IOError:
#                     print "txt file open error"
#                 else:
#                     print "读取文件内容..."
#                     html_cont = fobj.read()
#                     fobj.close()
#                     print "Read finished."
                    
                #3 解析器解析页面
                #判断待爬取的页面是搜索结果页还是论文详情页：
                #(1)搜索列表页面解析出论文数据及详情页URL
                try:
                    if uncrawled_url[:71] == searchResult_preUrl: 
                        print "待爬取页为搜索结果页："
                        logging.info('待爬取页为搜索结果页') 
                        
                        print "解析结果页..."
                        logging.info('解析结果页...') 
                        detail_urls,base_datas= self.parser.parse_searchResPage(uncrawled_url,html_cont)   #解析器解析页面url            
                        
                        self.urls.add_uncrawled_urls(detail_urls)  #将解析出的多个新url加入到数据库urlset表中
                        
                        #4 输出器：将解析出的数据插入数据库爬取结果表ieee_uhfrfid_data中
                        print "结果页解析结果输出..."
                        logging.info('结果页解析结果输出..') 
                        self.outputer.output_basedatas(base_datas)  
                        
                    #(2)文章详细页面只解析数据
                    else:                    
                        print "待爬取页为论文详情页："
                        logging.info('待爬取页为论文详情页') 
                            
                        print "解析详情页..."
                        logging.info('解析详情页...') 
                            
                        detail_data = self.parser.parse_detailsPage(uncrawled_url,html_cont)    #解析器解析页面数据
                                                
                        #4 输出器：用详情页解析出的数据（详情页url、摘要、关键词）修改补全数据库爬取结果表ieee_uhfrfid_data中的数据
                        print "详情页解析结果输出..."
                        logging.info('详情页解析结果输出...') 
                        self.outputer.output_detaildata(detail_data)
                        
                except Exception as e:
                    #如果解析失败的，则将页面设置为已爬取，否则会一直重复爬取该页面
        #           print "uncrawled_url[:36]:",uncrawled_url[:36]                   
                    self.urls.set_url_crawled(uncrawled_url)
                    logging.info('将解析失败页面设置为已爬取: %s'%uncrawled_url) 
                    logging.info('【【解析失败】】: %s'%str(e))        
                    conn.commit()
                
                #5 将页面设置为已爬取
                self.urls.set_url_crawled(uncrawled_url)
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
                self.urls.set_url_crawled(uncrawled_url)
                logging.info('将发生错误异常页面设置为已爬取: %s'%uncrawled_url) 
                
            except Exception as e:            
                print 'crawl failed:',str(e)
                logging.warning("【【crawl failed】】:%s"%str(e))
                                                    
        print '【crawl finished】: crawl count=%d'%count
        logging.info('【crawl finished】: crawl count=%d'%count) 
        
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
        #将第1页到最大页数的页面加入数据库表中
        SearchResult_urls_list = []
        maxPagenum = 126    #搜索结果的最大页数
        pagenum = 1
        while pagenum<=maxPagenum:
            #"http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=1&newsearch=true"
            SearchResult_url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber="+str(pagenum)+"&newsearch=true"
#             print SearchResult_url
#             print '取前面71个：'+SearchResult_url[:71]
            SearchResult_urls_list.append(SearchResult_url)
            pagenum = pagenum + 1
        
        obj_spider = SpiderMain(conn)
        obj_spider.craw(SearchResult_urls_list)
        
    except Exception as e:
        print "出现问题："+str(e)
        logging.warning("【【出现问题】】:%s"%str(e))
    finally:
        conn.close()
