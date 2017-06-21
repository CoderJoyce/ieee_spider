# coding:utf8
'''
Created on 2017-06-09
ieee_spider html下载器
@author: xiejing
'''
import urllib2

from selenium import webdriver #引入selenium中的webdriver
import time

import logging
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='ieee_spider.log',
                filemode='a')

import sys
reload(sys)
sys.setdefaultencoding('utf-8') #解决错误"'ascii' codec can't encode character u'\xa0' in position 14885:ordinal not in range(128)"

#HTML下载器
class HtmlDownloader(object):

    
    def _save_html_to_file(self, url, page_source):    #将下载的Html源码保存到文件中
        #1 根据url获得存储路径和文件名
        #论文详情页url前缀：http://ieeexplore.ieee.org/document/
        #搜索结果页url样例：http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=126&newsearch=true
        if url[:36] == "http://ieeexplore.ieee.org/document/":
            filePath = "downloadhtml/document"+url[36:-1]+".txt"
        else:
            filePath = "downloadhtml/search"+url[83:-15]+".txt"
        
#         print "filePath:",filePath
        
        #2 将页面源码保存到文件路径中
        try:   
            fobj = open(filePath,'w')
        except IOError as e:
            print "open error:",filePath
            raise e
        else:
#             print 'write begin...'
            fobj.write(url)
            fobj.write("\n")
            fobj.write(page_source) 
            fobj.close()
            logging.info("_save_html_to_file: %s successed." %filePath) 
#             print 'write finished'
           
    def download_ajax(self,url,waitTimeSec): #下载动态网页的Html源码
        print "download url:",url
        logging.info("download url:%s"%url)
        
        if url is None:
            return None
        
        #动态网页下载：Selenium+浏览器(Phantomjs/Chrome/...)
        #webdriver中的PhantomJS方法可以打开一个我们下载的静默浏览器。
        #输入executable_path为当前文件夹下的phantomjs.exe以启动浏览器
        #driver =webdriver.PhantomJS(executable_path="phantomjs.exe")
        print "html download driver.Chrome()..."
        logging.info("html download driver.Chrome()...")
        driver =webdriver.Chrome()
        
        print "get..." 
        logging.info("driver.get...")
        #使用浏览器请求页面
        driver.get(url) 
         
        print "wait..."
        logging.info("wait:time.sleep(%s)..."%waitTimeSec)
        #加载N秒，等待所有数据加载完毕
        time.sleep(waitTimeSec)
        
        #如果是搜索结果页则下拉浏览器滚动条使其加载出全部搜索结果（若不下拉滚动条只会加载前10条搜索结果）
        searchResult_preUrl = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID"
        if url[:71] == searchResult_preUrl:
            print "下拉滚动条..."
            logging.info("下拉滚动条...")
            js="var q=document.body.scrollTop=100000"
            driver.execute_script(js)
            time.sleep(2)
            js="var q=document.body.scrollTop=100000"   #要下拉至少两次才能把所有结果都加载出来
            driver.execute_script(js) 
            time.sleep(2)
            js="var q=document.body.scrollTop=100000"
            driver.execute_script(js) 
            time.sleep(2)
                
        print 'page_source:'
        logging.info("download page_source successed.")
        #print driver.page_source
        page_source = driver.page_source
        #将下载的html源码写入文本文件中
        self._save_html_to_file(url,page_source)
              
        #关闭浏览器
        driver.close()

        return page_source
    
    
    def download_static(self,url): #下载静态网页的Html源码
        print "url:",url
        
        if url is None:
            return None
        
        response = urllib2.urlopen(url)   
        
        if response.getcode()!=200:
            return        
        
        return response.read()  #返回html页面内容


if __name__=="__main__":
    print 'Test ieee_html_downloader:'

#     url = "http://pythonscraping.com/pages/javascript/ajaxDemo.html"
#     url = "http://ieeexplore.ieee.org/document/7583685/"
#     url = "http://ieeexplore.ieee.org/document/7939286/"
#     url = "http://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=UHF%20RFID"
    url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=126&newsearch=true"
    print 'craw: %s' %(url)
  
#     obj_HtmlDownloader = HtmlDownloader()
#     obj_HtmlDownloader._save_html_to_file(url,url)
        
#     response = urllib2.urlopen(url)
#     print response.read()
    
    #webdriver中的PhantomJS方法可以打开一个我们下载的静默浏览器。
    #输入executable_path为当前文件夹下的phantomjs.exe以启动浏览器
#     driver =webdriver.Chrome()
#     
#     print "get..." 
#     #使用浏览器请求页面
#     driver.get(url) 
#      
#     print "wait..."
#     #加载3秒，等待所有数据加载完毕
#     time.sleep(10)
#      
#     print "text:"
#     #通过class来定位元素，
#     #.text获取元素的文本数据
# #     print driver.find_element_by_class_name('description u-mb-1').text
# #     print driver.find_element_by_class_name('document-title').text
# #     print driver.find_element_by_id('content').text
#      
#     print 'page_source:'
#     try:
#         fobj = open("page_source.txt",'w')
#     except IOError:
#         print "page_source.txt open error"
#     else:
#         print 'write begin...'
#         fobj.write(driver.page_source)
#         fobj.close()
#         print 'write finished'
#     
# #     print driver.page_source
#       
#     #关闭浏览器
#     driver.close()
    