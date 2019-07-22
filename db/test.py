#coding=utf-8
'''
*************************
file:       AnalysisJobs redis-test
author:     gongyi
date:       2019/7/14 15:08
****************************
change activity:
            2019/7/14 15:08
'''
import re,requests
from bs4 import BeautifulSoup
def test_ip():
    '''
    测试ip是否有效
    :param ip:
    :return:
    '''
    headers = {'User-Agent':'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0'}

    url = 'https://ip.cn/'
    proxies = {'http': 'http://58.253.154.189:9999', 'https': 'https://58.253.154.189:9999'}
    print('正在使用的代理：', proxies)
    go_ip = re.findall(r'\d+.\d+.\d+.\d+', proxies['http'])
    print('正在使用的ip：', go_ip)

    res = requests.get(url, headers=headers, proxies=proxies, timeout=10)

    if res.status_code == 200:
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        script = soup.find('div', 'container-fluid').find_next('script').string
        ip = re.findall(r'\d+.\d+.\d+.\d+', script)[0]
        print('爬取到的ip值是：',ip,'当前代理ip是',go_ip)
        if ip == go_ip[0]:
            print('测试通过,当前ip是',go_ip)
            return True
    print('访问失败',res.status_code)
    return False

test_ip()
