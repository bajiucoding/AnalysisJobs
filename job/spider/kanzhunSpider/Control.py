# coding=utf-8
'''
*************************
file:       AnalysisJobs Control
author:     gongyi
date:       2019/7/16 16:53
****************************
change activity:
            2019/7/16 16:53
'''
# 看准网爬虫调度
from job.spider.HTMLDownload import HTMLDownload
from job.spider.URLManager import URLManager
# from job.spider.log import logger
from .HTMLAnalysis import CompanyHTMLAnalysis, InterviewHTMLAnalysis, ReviewHTMLAnalysis, SalaryHTMLAnalysis, InterviewDetailHTMLAnalysis, ReviewDetailHTMLAnalysis
from db import DataClass
import time,logging
import random

logger = logging.getLogger('django_console')


class Control():

    def __init__(self, company):
        # 初始化
        self.manager = URLManager('kanzhun')
        self.HTMLDownload = HTMLDownload()
        self.company = CompanyHTMLAnalysis()
        self.interview = InterviewHTMLAnalysis()
        self.interviewDetail = InterviewDetailHTMLAnalysis()
        self.review = ReviewHTMLAnalysis()
        self.reviewDetail = ReviewDetailHTMLAnalysis()
        self.salary = SalaryHTMLAnalysis()
        self.connM = DataClass.DataClass('kanzhunDB', company).connM

    def spider(self, root_url):
        '''
        ,company,job,city
        爬虫核心调度程序。根据传入company、职位、城市爬取对应内容
        :param job:
        :param city:
        :return:
        '''
        logger.info('看准网爬虫程序开始运行')
        self.manager.add_new_url(root_url)

        while self.manager.has_new_url():
            # 当有待爬取url存在时，就继续爬取
            logger.info('有待爬取url，开始爬取')
            time.sleep(random.randint(5, 10))

            new_url = self.manager.get_new_url()
            logger.info('开始爬取' + new_url + '的内容')
            html = self.HTMLDownload.download(new_url)

            new_urls = set()
            # 判断html，选择合适的解析类
            if 'companyl' in new_url:
                #公司列表页面 [title,review,salary,interview,photo]
                new_urls, data = self.company.parse(new_url, html)

                if not data:
                    self.connM.update({'title': 'company'},
                                      {'$set': {'company': None,
                                                'revieWNum': None,
                                                'salaryNum': None,
                                                'interviewNum': None,
                                                'photoNum': None}},
                                      True)
                else:
                    self.connM.update({'title': 'company'},
                                      {'$set': {'company': data[0],
                                                'revieWNum': data[1],
                                                'salaryNum': data[2],
                                                'interviewNum': data[3],
                                                'photoNum': data[4]}},
                                      True)

            elif 'gsr' in new_url:
                # 公司点评界面，[title,score,tags]
                new_urls, data = self.review.parse(new_url, html)
                # self.manager.add_new_urls(new_urls)
                if data:
                    self.connM.update({'title': 'company'}, {
                                  '$set': {'companyScore': data[1], 'companyTags': data[2]}}, True)
                else:
                    self.connM.update({'title': 'company'}, {
                        '$set': {'companyScore': None, 'companyTags': None}}, True)
            elif 'pl' in new_url:
                # 公司评价详情界面 [title, employee, commit_time,
                # job,[question_title,question_content],[...]]]
                logger.info('******************开始插入评价详情数据了****************8')
                new_urls, data = self.reviewDetail.parse(new_url, html)
                # self.manager.add_new_urls(new_urls)
                logger.info(data)
                if data:
                    self.connM.update({'title': 'review'}, {
                                  '$set': {data[3]: [data[1], data[2], data[4]]}}, True)
                else:
                    self.connM.update({'title': 'review'}, {
                        '$set': {None: [None, None, None]}}, True)

            elif 'gsx' in new_url:
                # 爬取工资界面，并未返回数据
                pass
                # new_urls, data = self.salary.parse(new_url, html)
                # self.manager.add_new_urls(new_urls)

            elif 'gsmsh' in new_url:
                # 面试经验详情界面 [title, job, interview_time, city, [interview_title, interview_content],[question_title,question_answer]]

                new_urls, data = self.interviewDetail.parse(new_url, html)
                logger.info('开始插入面试详情数据了***************************8')
                logger.info(data)
                if data:
                    self.connM.update({'title': 'interview'}, {
                                  '$set': {data[1]: [data[2], data[3], data[4], data[5]]}}, True)
                else:
                    self.connM.update({'title': 'interview'}, {
                        '$set': {None: [None, None, None, None]}}, True)
            elif 'gso' in new_url:
                # 主页
                pass

            elif 'gsp' in new_url:
                # 照片页面
                pass

            else:
                #面经列表界面 [title,interview_degree]
                new_urls, data = self.interview.parse(new_url, html)
                # self.manager.add_new_urls(new_urls)
                if len(data) == 2:
                    self.connM.update({'title': 'company'},
                                  {'$set': {'interviewDegree': data[1]}}, True)
                else:
                    self.connM.update({'title': 'company'},
                                      {'$set': {'interviewDegree': None}}, True)
            self.manager.add_new_urls(new_urls)
            logger.info('已经爬取了' + str(self.manager.old_urls_size()) + '个链接')

    def main(self,company):
        logger.info('看准网爬虫启动')
        url = 'https://www.kanzhun.com/companyl/search/?q='+company+'&stype=1'
        self.spider(url)


# if __name__ == '__main__':
#     control = Control('康博嘉')
#     control.main()
