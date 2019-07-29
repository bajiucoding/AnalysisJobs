#coding=utf-8
'''
*************************
file:       AnalysisJobs HTMLDownload
author:     gongyi
date:       2019/7/14 17:19
****************************
change activity:
            2019/7/14 17:19
'''
import requests,logging,re
# from job.spider.log import logger
from job.spider.spiderHelper import Proxy,get_agent
from job.spider.ProxyVaildate.proxyProvider import able_ip
from bs4 import BeautifulSoup
import logging
# logger = logger('HTMLdownload')

class HTMLDownload():
    #下载html

    def __init__(self):
        # 获取一个随机ip
        self.ip = able_ip()
        # 获取一个随机agent
        self.headers = get_agent()
        #模拟生成代理
        self.proxies = {'http':'http://'+self.ip,
                        'https':'https://'+self.ip
                        }

    def download(self,url):
        '''
        根据传进来的url下载对应页面
        :param url:
        :return:
        '''
        if 'www.zhipin.com' in url:
            logger = logging.getLogger('boss')
        else:
            logger = logging.getLogger('kanzhun')
        logger.info('开始下载当前url[' + str(url) + ']')
        #测试ip是否可用

        # res = requests.get(url,headers=self.headers,proxies=self.proxies,timeout=5)
        res = requests.get(url,headers=self.headers,timeout=5)
        if res.status_code == 200:
            logger.info('下载当前url[' + str(url) + ']成功')
            res.encoding = 'utf-8'
            return res.text
        logger.info('下载当前url['+url+']失败，状态码：'+str(res.status_code))
        return None

    def test_ip(self,test_ip):
        '''
        测试ip是否有效
        :param ip:
        :return:
        '''
        url = 'https://ip.cn/'
        res = requests.get(url,headers=self.headers,proxies=self.proxies,time_out=5)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text,'html.parser')
            script = soup.find('div', 'container-fluid').find_next('script').string
            ip = re.findall(r'\d+.\d+.\d+.\d+', script)[0]
            print(ip)
            if ip == test_ip:
                print('测试通过')
                return True
            return False

