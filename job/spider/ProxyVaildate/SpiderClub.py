#coding=utf-8
'''
*************************
file:       AnalysisJobs SpiderClub
author:     gongyi
date:       2019/7/19 16:35
****************************
change activity:
            2019/7/19 16:35
'''
from haipproxy.client.py_cli import ProxyFetcher
args = dict(host='127.0.0.1', port=6379, password='123456', db=0)
# ＃　这里`zhihu`的意思是，去和`zhihu`相关的代理ip校验队列中获取ip
# ＃　这么做的原因是同一个代理IP对不同网站代理效果不同
fetcher = ProxyFetcher('http', strategy='greedy', redis_args=args)
# 获取一个可用代理
print(fetcher.get_proxy())
# 获取可用代理列表
print(fetcher.get_proxies()) # or print(fetcher.pool)