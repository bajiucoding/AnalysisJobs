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
import telnetlib
from db.redisPool import getRedis
from job.spider.spiderHelper import get_agent

connR = getRedis()

def get_ip():
    '''
    获取一个ip
    :return: ip
    '''
    count = connR.scard('ip_new')
    print('当前有{}个待测ip'.format(count))
    if connR.scard('ip_new') < 10:
        # 如果剩余待检测ip数量小于10，就异步启动爬虫协程
        print('待测ip数量不足，开始爬取待测ip')
        pro.start()
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
from .GetProxy import GetProxy

pro = GetProxy()
async def test(proxy):
    '''
    异步协程检验ip
    :param queue:待检测ip队列
    :return:
    '''
    if connR.scard('ip_new') < 10:
        pro.start()
    url = 'https://ip.cn/'
    async with aiohttp.ClientSession() as session:
        try:
            print('当前获取到的ip：',proxy,'剩余待检测IP数量为：',connR.scard('ip_new'))
            go_ip,port = proxy.split(':')
            proxystr = 'http://'+proxy
            async with session.get(url,headers=get_agent(),proxy=proxystr,timeout=3) as res:
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


def getIP():
    while connR.scard('ip_new') < 10:
        pro.start()
#
# async def start():
#     await getIP()
#     tasks = [test() for _ in range(5)]
#     await asyncio.wait(tasks)
def control():
    while connR.scard('ip_able') < 10:
        try:
            loop = asyncio.get_event_loop()
            tasks = [test(ip) for ip in connR.smembers('ip_new')]
            loop.run_until_complete(asyncio.wait(tasks))
        except Exception as e:
            print('异步出现异常',e)

control()

