#coding=utf-8
'''
*************************
file:       AnalysisJobs Control
author:     gongyi
date:       2019/7/14 17:44
****************************
change activity:
            2019/7/14 17:44
'''
from job.spider.URLManager import URLManager
from job.spider.HTMLDownload import HTMLDownload
from job.spider.bossSpider.HTMLAnalysis import DetailHTMLAnalysis,JobHTMLAnalysis
from db import DataClass
import logging
import time,random

logger = logging.getLogger('boss')
class Control():
    #爬虫调度管理
    def __init__(self):
        self.manager = URLManager('boss')
        self.download = HTMLDownload()
        self.job_analysis = JobHTMLAnalysis()
        self.detail_analysis = DetailHTMLAnalysis()
        self.db = DataClass.DataClass('bossDB','bossDB')
        # self.query = 'python'
        self.page = 1

    def spider(self,root_url):
        '''
        爬虫调度方法
        :param root_url:
        :return:
        '''
        self.manager.add_new_url(root_url)
        logger.info('添加根url成功'+root_url)

        # if self.manager.old_urls_size() > 3:
        #     return None
        #开始爬取
        while self.manager.has_new_url():
            logger.info('有待爬取url，开始爬取')
            time.sleep(random.randint(5,10))
            new_url = self.manager.get_new_url()
            logger.info('即将开始下载['+str(new_url)+']的内容')
            html = self.download.download(new_url)
            if 'job_detail' not in new_url:
                #判断是否是职位详情界面
                new_urls,data = self.job_analysis.parse(new_url,html)
                if data:
                    for k,v in data.items():
                        self.db.connM.update({'jobId':k},{'$set':{'job':v[0],'city':v[-1],'content':v}},True)
            else:
                #是职位详情界面 [jobId,year,detail]
                new_urls,data = self.detail_analysis.parse(new_url,html)
                logger.info(str(data))
                if data:
                    self.db.connM.update({'jobId':data[0]},{'$addToSet':{'content':{'$each':[data[1],data[2]]}}},True)
            self.manager.add_new_urls(new_urls)
            logger.info('html解析完毕，开始存入数据')
            logger.info('已经爬取了'+str(self.manager.old_urls_size())+'个链接')
            # return data

    def main(self,job,city):
        '''
        爬虫启动入口
        :return:
        '''
        logger.info('爬虫启动')
        #爬取十页
        while self.page < 11:
            root_url = 'https://www.zhipin.com/{}/?query={}&page={}&ka=page-{}'.format(city,job, self.page,self.page)
            self.spider(root_url)
            self.page += 1

if __name__ == '__main__':
    spider = Control()
    print('开始')
    spider.main('python','深圳')