import requests
import re 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from distutils.filelist import findall
import nltk
import jieba
from nltk.stem import WordNetLemmatizer

# 非法URL 1
invalidLink1='#'
# 非法URL 2
invalidLink2='javascript:void(0)'

#去指定链接获取网页HTML源码
def get_html(url):
    headers = {
        'User-Agent':'Mozilla/5.0(Macintosh; Intel Mac OS X 10_11_4)\
        AppleWebKit/537.36(KHTML, like Gecko) Chrome/52 .0.2743. 116 Safari/537.36'
    }     #模拟浏览器访问
    response = requests.get(url,headers = headers)      #请求访问网站
    html = response.content.decode('utf-8')             #获取网页源码
    return html                                         #返回网页源码

def download_process(ch_en, #英文或中文下载
    pattern,    #筛选链接时的正则表达式
    url_path,   #url的父路径
    begin_url,  #开始网页链接
    download_file_path,  #下载文件的文件夹路径
    download_file_name,  #下载的文件前缀
    save_file_path,      #保存文件的文件夹路径
    save_file_name,      #保存的文件前缀
    stopwords_filename,  #停用词文件名
    max_count   #下载网页的最大数量
    ):

    url_list=[]     #保存将要下载的网页链接
    num_of_url=0    #记录已下载的网页数量

    #分析网页源码获取新闻链接
    def get_url(html):
        for tag in html.find_all('a'):  #在当前网页查找所有网页链接的标签
            url = tag.get('href')
            url=urljoin(url_path,url)      #由相对路劲拼接得到绝对路径
            if(url is not None):
                #过滤非法链接
                if url==invalidLink1:      #非法链接1
                    pass
                elif url==invalidLink2:    #非法链接2
                    pass
                elif url.find("javascript:")!= -1:
                    pass
                else:
                    if not re.match(pattern,url):  #只选取满足条件链接的格式
                        continue          
                    if url not in url_list:         #是没有查找过的链接的话保存 
                        print(str(len(url_list))+"   :"+url)    #输出链接方便观察爬取过程
                        url_list.append(url)        #保存链接
                        if len(url_list) >= max_count:      #数量达到max后跳出循环
                            break
     
    #从起始网站开始爬取网页链接直到达到max
    url_list.append(begin_url)
    print('0'+"   :"+begin_url)
    count_url=1
    begin_index=0                   
    while len(url_list) < max_count:    #直到达到max_count为止
        count_url=len(url_list)
        for url in url_list[begin_index:]:
            html = BeautifulSoup(get_html(url),"html.parser")
            get_url(html)               #从现有链接的网页中爬取新的链接
        begin_index = count_url


    num_of_url = len(url_list)      #更新网页数量

    #开始从已得到的url中爬取文字内容并写入文件
    while len(url_list) != 0 :
        url = url_list.pop()
        html = BeautifulSoup(get_html(url),"html.parser")
        
        #中文网页
        if ch_en == 'ch':
            caption = html.find('div',class_='caption')         #标题 
            summary = html.find('div',class_='article-summary') #summary
            main_text = html.find('div',class_='main-text')     #正文内容
            #提取所有正文内容写入文件
            with open(download_file_path + download_file_name + str(len(url_list)) + ".txt","w",encoding='utf-8') as file:
                file.write(caption.get_text())
                print(str(len(url_list))+" downlaoded:"+caption.get_text())   #输出该百科的标题方便观察进度
                if summary:
                    file.write(summary.get_text())
                for text in main_text.find_all('p'):   
                    file.write(text.get_text())
                file.close()
        #英文网页
        elif ch_en == 'en':
            text = html.find('div',class_='mw-body').get_text()
            print(str(len(url_list))+" downloaded:")    #输出当前进度
            with open(download_file_path + download_file_name + str(len(url_list)) + ".txt","w",encoding='utf-8') as file:
                file.write(text)


    #对文件中内容进行文本预处理
    for num in range(0, num_of_url):
        with open(download_file_path + download_file_name + str(num) + ".txt","r",encoding="utf-8") as file:
            text = file.read()
            file.close()

        #转换为小写，删除特殊字符
        if ch_en == 'en':   #英文
            text = text.lower()                         #英文文本转换为小写
            en_char = re.compile("[^a-z^ ^-^']|'\w+")   #去掉'm  've类似的部分
            text = en_char.sub(' ',text)                #只留下英文中可能出现的字符
            text_list = text.split()                    #去所有多余的空格、换行、制表符，得到分词之后的列表
        elif ch_en == 'ch': #中文
            ch_char = re.compile("[^\u4E00-\u9FA5]")    #去掉英文数字
            text = ch_char.sub(' ',text)                #只留下中文
            text_list = text.split()                    #去所有多余的空格、换行、制表符，得到分词之后的列表
            text_list = jieba.lcut("".join(text_list))  #中文分词

        #停用词过滤
        word_list0 = []  #声明一个停用词过滤后的词列表
        with open('C:\\Users\\ljh\\OneDrive\\大三下\\互联网搜索引擎\\课程设计\\'+stopwords_filename+'.txt','r',encoding='utf-8') as file:
            stop_words=list(file.read().split('\n')) #将停用词读取到列表里
            for word in text_list:
                if word not in stop_words:
                    word_list0.append(word) #将词变为小写加入词列表
            file.close()
        text_list = word_list0

         #英文提取词干
        if ch_en == 'en':   
            word_list1 = []  #声明一个提取词干后的词列表
            for word in text_list:
                word_list1.append(nltk.PorterStemmer().stem(word))
            text_list=word_list1

        text = " ".join(text_list)  #词语之间加上空格
        with open(save_file_path + save_file_name + str(num) +".txt","w",encoding="utf-8") as file:
            file.write(text)
            print(str(num)+" processed:")
            file.close()

print("中文网页下载----strat:")
download_process('ch',
                 r'https://baike.baidu.com/tashuo/browse.*',
                'https://baike.baidu.com',
                'https://baike.baidu.com/tashuo/browse/content?id=5274c6266a5cfbfb8b4e83c4',
                "C:\\Users\\ljh\\OneDrive\\大三下\\互联网搜索引擎\\课程设计\\Ch\\",
                "baike_ch_",
                "C:\\Users\\ljh\\OneDrive\\大三下\\互联网搜索引擎\\课程设计\\Ch_processed\\",
                "baike_ch_processed_",
                "stopwords_ch",
                1000)


print("\n\n")
print("英文网页下载----strat:")
download_process('en',
                 r'https://en.wikipedia.org/wiki/.*',
                'https://en.wikipedia.org/wiki/',
                'https://en.wikipedia.org/wiki/China',
                "C:\\Users\\ljh\\OneDrive\\大三下\\互联网搜索引擎\\课程设计\\En\\",
                "wiki_en_",
                "C:\\Users\\ljh\\OneDrive\\大三下\\互联网搜索引擎\\课程设计\\En_processed\\",
                "wiki_en_processed_",
                "stopwords_en",
                1000)
