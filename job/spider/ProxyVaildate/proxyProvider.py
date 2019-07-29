#coding=utf-8
'''
*************************
file:       AnalysisJobs proxyProvider
author:     gongyi
date:       2019/7/28 21:50
****************************
change activity:
            2019/7/28 21:50
'''
#提供正常可用的代理
#从ip_able中获取代理后，先进行检测，符合条件就返回
from db.redisPool import getRedis
from job.spider.spiderHelper import get_agent
from bs4 import BeautifulSoup
import requests,re
from .IPValidate import control
def able_ip():
    found = False
    connR = getRedis()
    url = 'https://ip.cn/'
    while not found:
        proxy = connR.spop('ip_able')
        control()
        go_ip, port = proxy.split(':')
        proxy_test = {'http':'http://'+proxy,'https':'https://'+proxy}

        res = requests.get(url,headers=get_agent(),proxies=proxy_test,timeout=2)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            script = soup.find('div', 'container-fluid').find_next('script').string
            ip = re.findall(r'\d+.\d+.\d+.\d+', script)[0]
            print('爬取到的ip值是：', ip, '当前代理ip是', go_ip)
            if ip == go_ip:
                print('########测试通过,当前ip是', go_ip)
                found = True
                return ip

# ip = able_ip()
# print(ip)