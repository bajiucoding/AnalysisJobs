#coding=utf-8
'''
*************************
file:       AnalysisJobs HTMLAnalysis
author:     gongyi
date:       2019/7/14 17:19
****************************
change activity:
            2019/7/14 17:19
'''
from bs4 import BeautifulSoup
from abc import ABCMeta,abstractmethod
from urllib.parse import urljoin
import re
import logging

logger = logging.getLogger('boss')

job_info = {}
class HTMLAnalysis(metaclass=ABCMeta):
    '''
    HTML解析抽象类
    '''

    @abstractmethod
    def parse(self, url, html):
        pass

    @abstractmethod
    def getNewUrl(self, url, soup):
        pass

    @abstractmethod
    def getNewData(self, url, soup):
        pass

class JobHTMLAnalysis(HTMLAnalysis):
    '''
    boss直聘职位列表页面html的解析
    '''

    def parse(self,url,html):
        '''
        重写虚类的parse方法，解析html
        :param url: 当前页面的url
        :param html: 当前页面得到的text即html文件
        :return:
        '''
        if not url or not html:
            logger.info('传入参数不完整')
            return set(),None
        logger.info('开始解析职位列表页面')
        soup = BeautifulSoup(html,'html.parser')
        new_url = self.getNewUrl(url,soup)
        new_data = self.getNewData(url,soup)
        logger.info('解析职位列表页面html成功')
        return new_url,new_data

    def getNewUrl(self,url,soup):
        '''
        职位页面获取新url
        :param url:
        :param soup:
        :return: 详情url
        '''
        logger.info('开始从职位列表页面解析新的url，即职位详情')
        new_urls = set()
        jobs = soup.find_all('div','job-primary')
        for job in jobs:
            href = job.find('div','info-primary').find('a')['href']
            new_url = urljoin(url,href)
            logger.info('解析到新的详情界面url:'+new_url)
            new_urls.add(new_url)
        logger.info('getNewURL方法执行完毕')
        return new_urls

    def getNewData(self,url,soup):
        '''
        职位页面获取职位相关数据
        :param url:
        :param soup:
        :return:
        '''
        logger.info('开始获得职位列表界面的数据')
        result = []
        jobs = soup.find_all('div','job-primary')
        city = soup.find('div','city-sel').find('span','label-text').find('b').string
        for job in jobs:
            jobId = job.find('div','info-primary').find('a')['data-jobid']
            result.append(job.find('div','job-title').string)     #获取职位名
            result.append(job.find('span', 'red').string)          #获取工资
            result.append(job.find('div', 'company-text').find('a').string.replace('.',''))   #获取公司名称
            # 获取公司地址、经验、学历要求。在一个p标签内还有e标签，先找到p标签，再找到其子标签
            response1 = job.find('div', 'info-primary').find('p').contents
            result.append(response1[0])                         #获取工作地点
            result.append(response1[2])                         #获取工作经验要求
            result.append(response1[4])                         #获取学历要求

            # 获取公司行业、规模、融资情况
            response2 = job.find('div', 'company-text').find('p').contents
            result.append(response2[0])                         #获取公司行业
            if len(response2) < 5:
                result.append('无融资信息')                         #公司融资情况
                result.append(response2[2])                             #公司规模
            else:
                result.append(response2[2])
                result.append(response2[4])
            # job_info['jobId'] = jobId
            result.append(city)
            job_info[jobId] = [i for i in result]
            result.clear()
            print(job_info[jobId])
        logger.info('已经获得了职位列表界面的数据')
        return job_info

class DetailHTMLAnalysis(HTMLAnalysis):
    '''
    职位详情界面HTML解析
    '''

    def parse(self,url,html):
        if not url or not html:
            logger.info('传入参数不完整')
            return None,None
        logger.info('开始解析职位详情页面')
        soup = BeautifulSoup(html,'html.parser')
        new_url = self.getNewUrl(url,soup)
        new_data = self.getNewData(url,soup)
        logger.info('解析职位详情页面html成功')
        return new_url,new_data

    def getNewUrl(self,url,soup):
        return set()

    def getNewData(self,url,soup):
        '''
        职位详情页面解析。目前就解析出工作年限和全部的工作要求
        :param url:
        :param soup:
        :return:
        '''
        #工作年限要求
        year = ''
        if not url or not soup:
            logger.info('参数错误')
            return None
        logger.info('开始获取职位详情数据'+url)
        error = soup.find('div','error-content')
        logger.info(error)
        if soup.find('div','error-content'):
            logger.info('工作详情界面不存在')
            return None
        job = soup.find('div','detail-op').find('a')['ka']
        jobId = re.search(r'\d+',job).group(0)

        details = soup.find('div', 'detail-content').find('div', 'text').contents
        logger.info('获取了职位详情数据**'+str(len(details))+'***'+jobId)

        for i in range(len(details)):
            if i % 2 != 0:
                continue
            if '年' in details[i].strip():
                if re.match(r'[1-9]', details[i].strip()) and '经验' in details[i].strip():
                    year = details[i].strip()
        #details是一个列表，里边包含有tag和None，要过滤掉
        detail = ''.join(i.strip() for i in details if type(i) is not 'bs4.element.Tag' and len(i)!=0).replace(' ','')
        logger.info('当前获得的职位信息'+detail)
        # logger.info('当前职位列表信息'+str(job_info[jobId]))
        # logger.info(str(job_info[jobId].append(detail)))
        # job_info[jobId].append(detail)
        info = [jobId,year,detail]
        return info