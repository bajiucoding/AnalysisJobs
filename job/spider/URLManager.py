# coding=utf-8
'''
*************************
file:       AnalysisJobs URLManager
author:     gongyi
date:       2019/7/13 20:15
****************************
change activity:
            2019/7/13 20:15
'''
import hashlib
from db import redisPool
from job.spider.log import logger
import logging

# logger = logger('URLManager')

logger = logging.getLogger('django_console')
class URLManager():
    # url管理类。url集合存储在redis中

    def __init__(self,site):
        '''
        初始化
        '''
        self.conn = redisPool.getRedis()  # 初始化一个redis的连接
        # self.new_url = self.conn.sadd()
        self.new_url = site+'_new_urls'
        self.old_url = site+'_old_urls'

    def old_urls_size(self):
        '''
        获取已爬取链接的数量
        :return:
        '''
        return self.conn.scard(self.old_url)

    def add_new_url(self,url):
        '''
        向待爬取链接集合中增加新的待爬取链接
        :param url: 单个链接
        :return:
        '''
        logger.info('开始向['+self.new_url+']中添加待爬取url')
        if not url:
            return None
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        url_md5 = m.hexdigest()
        if not self.conn.sismember(self.new_url,url) and not self.conn.sismember(self.old_url,url_md5):
            self.conn.sadd(self.new_url,url)

    def add_new_urls(self, urls):
        '''
        向待爬取链接集合中增加新的待爬取链接集合
        :param urls: 待爬取链接。集合
        :return:
        '''
        logger.info('开始向[' + self.new_url + ']中添加待爬取url')
        if not urls:
            return None
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        '''
        是否还有待爬取的链接
        :return:Boolean
        '''
        return self.conn.scard(self.new_url) != 0

    def get_new_url(self):
        '''
        获取即将要爬取的新链接
        :return:
        '''
        logger.info('开始从[' + self.new_url + ']中获取待爬取url')
        new_url = self.conn.spop(self.new_url)
        logger.info('还有'+str(self.conn.scard(self.new_url))+'条链接待爬取')
        #引入hashlib库，将url进行md5转化，并只取中间128位，减少数据长度，节省内存。
        m = hashlib.md5()
        m.update(new_url.encode())
        logger.info('开始向[' + self.old_url + ']中添加已爬取url')
        self.conn.sadd(self.old_url,m.hexdigest()[8:-8])
        return new_url


