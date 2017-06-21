# coding:utf8
'''
Created on 2017-06-09
ieee_spider HTML解析器
@author: xiejing
'''
from bs4 import BeautifulSoup

import re
import urlparse
from ieee_spider.MySql_outputer import MySqlOutputer
import MySQLdb

 
#HTML解析器
class HtmlParser(object):
      
    def _get_detailPage_urls(self, page_url, soup):     #解析出搜索结果页面中所有结果详情页的url
#         print '所有结果详情页的url...'
        
        new_urls = []   #链表，有序
#         print soup
#         以/document/123+/结尾
        links = soup.find_all('a',href = re.compile(r"/document/\d+/$"))     #正则匹配
#         print "links:"
#         print links
        for link in links:
            new_url = link['href']
            new_full_url = urlparse.urljoin(page_url,new_url) #补全url
#             print new_full_url
            new_urls.append(new_full_url)
        return new_urls
      
    def _get_base_Data(self, page_url, soup):    #解析出搜索结果页面中的论文数据（题目、摘要（不全）、期刊、日期）
#         print '_get_base_Data解析数据...'
        res_datas = []       #返回数据（所有论文的数据）
                
        # 题目格式:<h2>***</h2>
        title_nodes = soup.find_all('h2')
#         print '题目：',title_nodes
            
        # 摘要格式:<span ng-bind-html="::record.abstract" class="ng-binding">...</span>
        abstract_nodes = soup.find_all('span',attrs={'ng-bind-html':'::record.abstract'})
#         print '摘要：',abstract_nodes
         
        # 关键字：无
        KeyWord = ''
#         print '关键字：',KeyWord
         
        # 期刊格式：<a ... ng-bind-html="::record.displayPublicationTitle">...</a>
        journal_nodes = soup.find_all('a',attrs={'ng-bind-html':'::record.displayPublicationTitle'})
#         print '期刊：',journal_nodes
         
        # 日期格式：<span ng-if="::record.publicationYear"...class="ng-binding ng-scope">...</span>
        date_nodes = soup.find_all('span',attrs={'ng-if':'::record.publicationYear'},class_="ng-binding ng-scope")
#         print "日期：",date_nodes
        
        for index in range(len(title_nodes)):
#             print index           
#             print "url:",page_url
#             print "题目：",title_nodes[index].get_text()
#             print "摘要：",abstract_nodes[index].get_text()
#             print "关键词："
#             print "期刊：",journal_nodes[index].get_text()
#             print "时间：",date_nodes[index].get_text()
            paper_data = {}     #单个论文的相关数据
            paper_data['url'] = page_url
            paper_data['title'] = title_nodes[index].get_text().strip() #strip()方法去除字符串两边的空格
            paper_data['abstract'] = abstract_nodes[index].get_text().strip()   
            paper_data['keywords'] = KeyWord
            paper_data['journal'] = journal_nodes[index].get_text().strip()
            paper_data['date'] = date_nodes[index].get_text().strip()
            
            res_datas.append(paper_data)
            
#         print res_datas         
#             fobj=open("parser_result.txt",'a')
#             fobj.write('\n'+title_nodes[index].get_text())
#             fobj.close()
           
        return res_datas
        
    def _get_detail_Data(self, page_url, soup):  #解析出论文详情页面中的论文数据（题目、完整摘要、关键字、期刊、具体日期）& 详情页url
#         print '_get_detail_Data解析数据...'
                
        # 题目格式:<h1 class="document-title">***</h1>
#         print '题目：' 
        title_node = soup.find('h1',class_="document-title")
#         print "title_node:",title_node.get_text()
            
        # 摘要格式:<div class="abstract-text ng-binding">...</div>
#         print '摘要：'
        abstract_node = soup.find('div',class_="abstract-text ng-binding")
#         print "abstract_node:",abstract_node.get_text()
         
        # 关键字格式:<li class="doc-all-keywords-list-item ng-scope"...><div>...</div></li>
#         print '关键字：'
        KeyWord_nodes = soup.find('li',class_="doc-all-keywords-list-item ng-scope").find_all('span')
#         print "KeyWord_node:",KeyWord_nodes
                      
        #去除关键字与关键字之间的空格
        keyword_str = ''
        for keyword_node in KeyWord_nodes:
            keyword_str = keyword_str + keyword_node.get_text().strip()  #strip()方法去除字符串两边的空格
#         print "keyword_str:",keyword_str
        
        # 期刊格式：<div class="u-pd-1 stats-document-abstract-publishedIn ng-scope"...><a...>...</a></div>
        journal_node = soup.find('div',class_="u-pb-1 stats-document-abstract-publishedIn ng-scope").find('a')
#         print 'journal_node:',journal_node
         
        # 日期格式：<div class="u-pd-1 doc-abstract-confdate ng-binding ng-scope"...>...</span>
        date_node = soup.find('div',class_="u-pb-1 doc-abstract-confdate ng-binding ng-scope")
#         print "date_node:",date_node
        #去掉日期中的Date of Conference:及空格
        date_text = date_node.get_text().strip()
        date_str = date_text[19:].strip()
        
        paper_data = {}       #返回数据（单篇论文的数据）
        paper_data['url'] = page_url
        paper_data['title'] = title_node.get_text().strip() #strip()方法去除字符串两边的空格
        paper_data['abstract'] = abstract_node.get_text().strip()   
        paper_data['keywords'] = keyword_str
        paper_data['journal'] = journal_node.get_text().strip()
        paper_data['date'] = date_str
        
#         print "paper_data:",paper_data
        return paper_data
        
                
    def parse_searchResPage(self,page_url,html_cont): #获得搜索结果页面中的所有详情页url和论文基础数据
        if page_url is None or html_cont is None:
            return
        
        soup = BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
        
        detail_urls = self._get_detailPage_urls(page_url,soup)
        base_datas = self._get_base_Data(page_url,soup)
        
        return detail_urls,base_datas
        
    def parse_detailsPage(self,page_url,html_cont):
        if page_url is None or html_cont is None:
            return
        
        soup = BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
        
        detail_datas = self._get_detail_Data(page_url,soup)
        
        return detail_datas
    
    

if __name__=="__main__":
    print 'Test ieee_html_parser:'

    #测试二：测试解析器&输出器
#     url = "http://pythonscraping.com/pages/javascript/ajaxDemo.html"
#     url = "http://ieeexplore.ieee.org/document/7583685/"
#     url = "http://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=UHF%20RFID"
#     url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=2&newsearch=true"
    
    url = "http://ieeexplore.ieee.org/document/7939286/"
    print 'craw: %s' %(url)
          
    #用读取已下载txt文件内容来模拟下载器下载网页
    print 'page_source:'
    try:
#         fobj = open("page_source_result01.txt",'r')
        fobj = open("page_source_document7939286.txt",'r')
    except IOError:
        print "txt file open error"
    else:
        print "读取文件内容..."
        html_cont = fobj.read()
        fobj.close()
        print "Read finished."
#         print html_cont
     
    obj_parser = HtmlParser()
     
    paper_data = obj_parser.parse_detailsPage(url, html_cont)
 
    #数据库连接
    conn = MySQLdb.connect(
                    host = '127.0.0.1',
                    port = 3306,
                    user = 'root',
                    passwd = 'ruijie@123',
                    db = 'spider_db',
                    charset = 'utf8'
                   )
          
    obj_outputer = MySqlOutputer(conn)
      
    try:
#         obj_outputer.output_basedata(paper_datas)
        obj_outputer.output_detaildata(paper_data)
        conn.commit()   
    except Exception as e:
        conn.rollback()
        print "出现问题："+str(e)
    finally:
        conn.close()
    

    #测试二：测试解析程序正则表达式匹配以/document/123+/结尾
    #html_doc用于测试
    html_doc = """
    <html><head><title>The Dormouse's story</title></head>
    <body>
    <p class="title"><b>The Dormouse's story</b></p>
    
    <p class="story">Once upon a time there were three little sisters; and their names were
    <a href="http://ieeexplore.ieee.org/document/7138648/" class="sister" id="link1">Elsie</a>,
    <a href="http://ieeexplore.ieee.org/document/7138648/citations?tabFilter=papers" id="link2">Lacie</a> and
    <a href="http://ieeexplore.ieee.org/document/7808807/media" id="link3">Tillie</a>;
    and they lived at the bottom of a well.</p>
    
    <p class="story">...</p>
    """
    soup = BeautifulSoup(html_doc,'html.parser',from_encoding='utf-8')
    obj_parser = HtmlParser() 
    paper_data = obj_parser._get_detailPage_urls(url, soup)
    
    
    
        