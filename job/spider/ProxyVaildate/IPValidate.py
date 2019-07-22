#coding=utf-8
'''
*************************
file:       AnalysisJobs IPValidate
author:     gongyi
date:       2019/7/19 11:41
****************************
change activity:
            2019/7/19 11:41
'''
#检验ip是否可用
import aiohttp,asyncio
import telnetlib
from db.redisPool import getRedis
from job.spider.spiderHelper import get_agent

connR = getRedis()

def get_ip():
    '''
    获取一个ip
    :return: ip
    '''
    ip = connR.spop('ip_new')
    return ip

def testTel(proxy):
    ip,port = proxy.split(':')

    try:
        telnetlib.Telnet(ip,port=port,timeout=10)
    except:
        print('当前ip不可用',proxy)
    else:
        connR.sadd('ip_able',proxy)
        print('当前代理可用',proxy)

# if __name__ == '__main__':
#     ip = get_ip()
#     testTel(ip)


import asyncio,aiohttp,re
from bs4 import BeautifulSoup
async def test():
    '''
    异步协程检验ip
    :param queue:待检测ip队列
    :return:
    '''
    url = 'https://ip.cn/'
    count = connR.scard('ip_new')
    print('当前有{}个待测ip'.format(count))
    async with aiohttp.ClientSession() as session:
        while count > 0:
            try:
                proxy = get_ip()
                print('当前获取到的ip：',proxy)
                go_ip,port = proxy.split(':')
                proxystr = 'http://'+proxy
                async with session.get(url,headers=get_agent(),proxy=proxystr,timeout=5) as res:
                    if res.status == 200:
                        res.encoding = 'utf-8'
                        soup = BeautifulSoup(res.text, 'html.parser')
                        script = soup.find('div', 'container-fluid').find_next('script').string
                        ip = re.findall(r'\d+.\d+.\d+.\d+', script)[0]
                        print('爬取到的ip值是：', ip, '当前代理ip是', go_ip)
                        if ip == go_ip:
                            print('########测试通过,当前ip是', go_ip)
                            connR.sadd('ip_able',proxy)
                    connR.sadd('ip_able',proxy)
                    print('访问失败，状态码是：',res.status)
            except Exception as e:
                print('访问异常',e)
import time

from .GetProxy import GetProxy

pro = GetProxy()
async def getIP():
    while connR.scard('ip_new') < 10:
       await pro.start()

async def start():
    await getIP()
    tasks = [test() for _ in range(5)]
    await asyncio.wait(tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(start())

