# ieee_spider
爬取IEEE网站上UHF RFID相关论文题目、摘要、关键字、期刊、日期信息

遇到的一些坑：
1、下载器：
(1)动态加载网页下载
(2)网站不稳定（时而加载成功，时而超时失败，下载特别慢）
(3)搜索结果页需要控制浏览器下拉滚动条至少两次才能加载出完整的页面

2、解析器：
(1)attrs的提取方式
(2)提取的信息前后空格太多，不同关键字之间也有较多空格
(3)日期提取时单个逗号与日期格式类似需增加解析条件排除逗号
(4)结果页的正则匹配要精确（以/document/123+/结尾,否则会多解析出一些不需要的链接，导致保存下载的页面源码到本地时路径文件名错误）

3、输出器：
(1)摘要等信息字符串中存在'或”，会造成SQL语句语法错误，导致异常

爬取运行后还有些异常没有预见到：如格式异常（如搜索结果页有些条目没有摘要，题目也无链接）、下载器下载的页面源码不全、详情页期刊或日期为空时的异常处理、详情页若爬取的期刊或日期信息为空则会覆盖已有期刊或日期信息等

结果搜索页：爬取基本信息（题目、摘要（不全）、期刊、日期），主要是为了当论文详情页没有任何信息时获得论文的部分信息，注意对缺少信息（如无摘要）的格式异常的处理。
论文详情页：爬取详细信息（题目、摘要、关键字、期刊、日期），主要是为了补全摘要和关键字，注意对异常情况（如期刊或日期缺失）的处理。

通过运行、查看运行结果和日志信息来发现异常并查找异常出现的原因，从而针对原因来制定解决办法。