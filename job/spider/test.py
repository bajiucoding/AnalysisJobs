#coding=utf-8
'''
*************************
file:       AnalysisJobs test
author:     gongyi
date:       2019/7/17 11:02
****************************
change activity:
            2019/7/17 11:02
'''
#测试某些网站的提取规则
import requests,logging,re
from bs4 import BeautifulSoup
from HTMLDownload import HTMLDownload
from spiderHelper import Proxy,get_agent
import asyncio,aiohttp
import pysnooper
count = 0
class ProxtValidator():
    #代理ip可用性验证

    def __init__(self):
        self.url = 'https://ip.cn/'
        self.headers = get_agent()
        self.timeout = 3.05
        self.coro_count = 30
        self.proxy_queue = None
        self.useableProxy = set()

    # @pysnooper.snoop()
    async def _validator(self,proxy_queue):
        '''
        测试代理。主体方法，包括发起请求
        '''
        if isinstance(proxy_queue,asyncio.Queue):
            async with aiohttp.ClientSession() as session:
                while not self.proxy_queue.empty():
                    try:
                        proxy = await proxy_queue.get()
                        go_ip = proxy[0]
                        # proxystr = {'http':'http://'+proxy[0]+':'+proxy[1],'https':'https://'+proxy[0]+':'+proxy[1]}
                        proxystr = 'https://'+proxy[0]+':'+proxy[1]
                        async with session.get(self.url,headers=self.headers,
                            proxy=proxystr,timeout=self.timeout) as res:
                            if res.status == 200:
                                res.encoding = 'utf-8'
                                soup = BeautifulSoup(res.text, 'html.parser')
                                script = soup.find('div', 'container-fluid').find_next('script').string
                                ip = re.findall(r'\d+.\d+.\d+.\d+', script)[0]
                                print('爬取到的ip值是：',ip,'当前代理ip是',go_ip)
                                if ip == go_ip[0]:
                                    print('########测试通过,当前ip是',go_ip)
                                    self.useableProxy.add(ip)
                                    return self.useableProxy
                            self.useableProxy.add(ip)
                            print('访问失败',res.status)
                            return self.useableProxy
                    except asyncio.TimeoutError:
                        print('asyncio.timeout异常')
                    except Exception as e:
                        print('未知异常',e)

    # @pysnooper.snoop()
    async def _get_proxy_queue(self):
        '''
        获取待检测ip，放入异步队列asyncio.Queue
        :return:
        '''
        print('开始获取ip队列，从数据库中取数据')
        queue = asyncio.Queue()
        count = 0
        pr = Proxy()
        # while count < 30:
        html = pr.getHTML()
        print('下载的页面',len(html))
        pr.parse(html)
        print('爬取到的ip数据',pr.data)
        for i in pr.data:
            ip = [i[0],i[1]]
            print('取到一个ip，', ip)
            await queue.put(ip)
        self.proxy_queue = queue
        return queue

    # @pysnooper.snoop()
    async def start(self):
        '''
        获取待检测代理队列
        '''
        print('start方法开始执行，准备获得代理ip的队列。将get_proxy_queue方法await上')
        proxy_queue = await self._get_proxy_queue()
        print('创建500个请求任务，即validator')
        to_validate = [self._validator(proxy_queue) for _ in range(self.coro_count)]
        # to_validate.append(self.)
        print('协程await验证方法的完成')
        await asyncio.wait(to_validate)

    @pysnooper.snoop()
    def proxy_validator_run(self):
        print('注册事件循环')
        loop = asyncio.get_event_loop()
        try:
            print('将start方法加入到循环上去，作为一个任务')
            loop.run_until_complete(self.start())
        except Exception as e:
            print(e)

if __name__ == '__main__':
    validator = ProxtValidator()
    ips = validator.proxy_validator_run()
    print('最终得到的可用ip：',ips)