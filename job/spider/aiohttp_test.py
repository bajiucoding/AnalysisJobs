#coding=utf-8
'''
*************************
file:       AnalysisJobs aiohttp_test
author:     gongyi
date:       2019/7/15 9:23
****************************
change activity:
            2019/7/15 9:23
'''
import aiohttp
import asyncio
import time
start = time.time()

async def get(url):
    '''
    利用aiohttp获取url页面
    :param url:
    :return:
    '''
    session = aiohttp.ClientSession()
    res = await session.get(url)
    result = await res.text()
    session.close()
    return result

async def request():
    url = 'http://127.0.0.1:5000'
    print('waiting for ',url)
    result = await get(url)
    print('get response from ',url,'result',result)

tasks = [asyncio.ensure_future(request()) for _ in range(5)]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

end = time.time()
print('cost:',end-start)