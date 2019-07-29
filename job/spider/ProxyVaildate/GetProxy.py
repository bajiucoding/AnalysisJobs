#coding=utf-8
'''
*************************
file:       AnalysisJobs GetProxy
author:     gongyi
date:       2019/7/19 10:16
****************************
change activity:
            2019/7/19 10:16
'''
#爬取免费代理，存入redis中
import random
import requests,re
from bs4 import BeautifulSoup
from db.redisPool import getRedis
from job.spider.spiderHelper import get_agent


hai_ip = 'http://www.iphai.com/free/ng'                     #ip海，只有一页


class GetProxy():
    '''
    爬取代理网站，获取ip存入redis
    '''
    def __init__(self):
        self.connR = getRedis()     #建立一个redis链接
        self.proxies = {'http':'http://','https':'https://'}    #代理，之后有代理ip后，就直接用代理ip
        self.ips = 'ip_new'         #存放爬取下来ip的集合名字
        self.ip_able = 'ip_able'    #存放可用集合

    def download(self,url):
        '''
        下载网页
        :param url:待下载页面url
        :return:
        '''
        try:
            res = requests.get(url,headers=get_agent())
            if res.status_code == 200:
                res.encoding = 'utf-8'
                return res.text
            else:
                print('下载网页失败',url)
        except Exception as e:
            print(e,'requests请求网页失败',url)

    def parse(self,url,html):
        '''
        转换解析网页内容
        :param html: 下载下来的html.text部分
        :return:
        '''
        # soup = BeautifulSoup(html,'html.parser')

        ip_list,port_list = [],[]
        if 'kuaidaili' in url:
            #快代理页面解析
            ip_list = re.findall(r'<td data-title="IP">\d+.\d+.\d+.\d+</td>',html)
            port_list = re.findall(r'<td data-title="PORT">[\d]*</td>',html)
        elif 'xici' in url:
            #西刺代理爬取
            ip_list = re.findall(r'<td>\d+.\d+.\d+.\d+</td>',html)
            port_list = re.findall(r'<td>[\d]*</td>',html)
        else:
            pass
        #ip海代理网站，已经打不开了
        # elif 'iphai' in url:
        #     #ip海免费代理爬取
        #     ip_list = re.findall(r'<td>\d+.\d+.\d+.\d+</td>')
        #     port_list = re.findall(r'<td>[\d]*</td>', html)

        for i in range(len(ip_list)):
            #正则匹配得出ip和port
            ip = re.findall(r'\d+.\d+.\d+.\d+',ip_list[i])[0]
            port = re.findall(r'\d+',port_list[i])[0]
            #将得到的ip和port存入集合
            self.connR.sadd(self.ips,ip+':'+port)

    def start(self):
        #启动代理ip爬虫程序
        page = 1
        kuai_ip = 'https://www.kuaidaili.com/free/inha/' + str(page-20) + '/'  # 快代理
        xici_ip = 'https://www.xicidaili.com/nn/' + str(page)  # 西刺代理
        url = xici_ip if page < 20 else kuai_ip            #爬取西刺ip前20页，之后爬取快ip
        page += 1
        html = self.download(url)
        self.parse(url,html)

# pro = GetProxy()
# url = 'https://www.kuaidaili.com/free/inha/1'
# res = pro.download(url)
# pro.parse(url,res)