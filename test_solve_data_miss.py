# coding:utf8
'''
Created on 2017-06-23
IEEE爬虫漏爬数据情况解决方法测试实现
@author: xiejing
'''
import re
from bs4 import BeautifulSoup

class SolveDataMiss(object):
    def Solve_QuoteAbnormal(self,data_str):  #解决双引号引起的异常
        #将字符串中的一个或多个连续的双引号替换成单个引号
#         print "data_str:",data_str
        strinfo = re.compile(r'"')
#         print "strinfo:",strinfo
        data_res =strinfo.sub("'",data_str)
#         print "data_res:",data_res
        return data_res
    
    def get_downloaded_html_cont(self,page_url): #获得已下载html源码
        #用读取已下载txt文件内容来模拟下载器下载网页
        #1 根据url获得存储路径和文件名
        #论文详情页url前缀：http://ieeexplore.ieee.org/document/
        #搜索结果页url样例：http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=126&newsearch=true
        if page_url[:36] == "http://ieeexplore.ieee.org/document/":
            filePath = "downloadhtml/document"+page_url[36:-1]+".txt"
        else:
            filePath = "downloadhtml/search"+page_url[83:-15]+".txt"
        
        print "filePath:",filePath
        
        #2 根据路径读取已下载的html源码文件
        print 'page_source:'
        try:
    #         fobj = open("page_source_result01.txt",'r')
            fobj = open(filePath,'r')
        except IOError:
            print "txt file open error"
        else:
            print "读取文件内容..."
            html_cont = fobj.read()
            fobj.close()
            
        return html_cont
    
    def _get_base_Data(self, page_url, soup):    #解析出搜索结果页面中的论文数据（题目、摘要（不全）、期刊、日期）
#         print '_get_base_Data解析数据...'
        res_datas = []       #返回数据（所有论文的数据）
                
        # 题目格式:<a ng-if="::(!(record.ephemera))" href="/document/123/"...>...</a>
        title_nodes = soup.find_all('a',href = re.compile(r"/document/\d+/$"),attrs={'ng-if':'::(!(record.ephemera))'})
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
        
        print "len(title_nodes)=",len(title_nodes)
        print "len(abstract_nodes)=",len(abstract_nodes)
        print "len(journal_nodes)=",len(journal_nodes)
        print "len(date_nodes)=",len(date_nodes)
        
        if(len(title_nodes)==len(abstract_nodes)==len(journal_nodes)==len(date_nodes)):
            #当解析出的题目、摘要、期刊、日期数目相同时，表示不存在格式异常的论文条目
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
#                 print index,paper_data
                res_datas.append(paper_data)

        else:
            #当解析出的题目、摘要、期刊、日期数目不同时，表示存在格式异常的论文条目（只获得正在格式论文的题目和摘要信息，期刊与日期由于数目不对称则丢弃）
            for index in range(len(title_nodes)):
                paper_data = {}     #单个论文的相关数据
                paper_data['url'] = page_url
                paper_data['title'] = title_nodes[index].get_text().strip() #strip()方法去除字符串两边的空格
                paper_data['abstract'] = abstract_nodes[index].get_text().strip()   
                paper_data['keywords'] = KeyWord
                paper_data['journal'] = ''
                paper_data['date'] = ''
#                 print index,paper_data
                                  
                res_datas.append(paper_data)
                
#         print "res_datas:",res_datas[0]
#             fobj=open("parser_result.txt",'a')
#             fobj.write('\n'+title_nodes[index].get_text())
#             fobj.close()
           
        return res_datas
          
    def Solve_FormatAbnormal(self): #解决搜索结果论文条目格式异常
        page_url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=UHF%20RFID&pageNumber=82&newsearch=true"
        filePath = "downloadhtml/search1.txt"
        html_cont = self.get_downloaded_html_cont(page_url)
        
        soup = BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
#         print "soup:",soup
        
        base_datas = self._get_base_Data(page_url, soup)
        print "base_datas:",base_datas  
    
    
if __name__=="__main__":
    print 'Test SolveDataMiss:'
    obj_SolveDataMiss = SolveDataMiss()  
 
#测试双引号异常的解决方法    
    data_str = 'EPC "Gen 2""""”as a reference standard. In this paper, we analyze the anti-collision procedure of EPC "Gen 2" to find ' 
    print "before data_str:",data_str
    data_str = obj_SolveDataMiss.Solve_QuoteAbnormal(data_str)
    print "after data_str:",data_str
    
    #测试格式异常的解决方法
    #obj_SolveDataMiss.Solve_FormatAbnormal()
    
    
    


    
    
    