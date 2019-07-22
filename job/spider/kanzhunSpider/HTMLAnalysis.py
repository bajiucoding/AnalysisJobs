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
# from job.spider.log import logger

# logger = logger('KanZhunHTMLAnalysis')
logger = logging.getLogger('django_console')

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

class CompanyHTMLAnalysis(HTMLAnalysis):
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
            return None
        logger.info('开始解析搜索得出的公司列表页面')
        soup = BeautifulSoup(html,'html.parser')
        if soup.find('p','f_16 mb15'):
            #说明看准网没有这家公司的信息
            logger.info('看准网没有这家公司的信息')
            return None
        new_url = self.getNewUrl(url,soup)
        new_data = self.getNewData(url,soup)
        logger.info('解析公司列表页面html成功')
        return new_url,new_data

    def getNewUrl(self,url,soup):
        '''
        职位页面获取新url。直接返回列表中的第一家公司
        :param url:
        :param soup:
        :return: 详情url
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        new_urls = set()
        logger.info('开始从公司列表页面解析新的url，即公司详情')
        #获取公司详情页面的href
        href = soup.find('a',ka='com1-title')['href']
        new_urls.add(urljoin(url,href))
        #获取公司点评界面url
        href = soup.find('a',ka='com1-review')['href']
        new_urls.add(urljoin(url,href))
        #公司工资界面
        href = soup.find('a', ka='com1-salary')['href']
        new_urls.add(urljoin(url, href))
        #公司面试界面
        href = soup.find('a', ka='com1-interview')['href']
        new_urls.add(urljoin(url, href))
        #照片
        href = soup.find('a', ka='com1-photo')['href']
        new_urls.add(urljoin(url, href))
        logger.info('从'+url+'界面抓取url成功')
        return new_urls


    def getNewData(self,url,soup):
        '''
        职位页面获取职位相关数据
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        title = soup.find('a',ka='com1-title').string
        review = re.findall(r'\d+',soup.find('a', ka='com1-review').string)[0]  #评价条数
        salary = re.findall(r'\d+',soup.find('a',ka='com1-salary').string)[0]    #平均工资
        interview = re.findall(r'\d+',soup.find('a',ka='com1-interview').string)[0]  #面试经验条数
        photo = re.findall(r'\d+',soup.find('a',ka='com1-photo').string)[0]  #照片条数
        result = [title,review,salary,interview,photo]
        logger.info('获取公司列表界面'+url+'数据完毕，即将返回数据，list类型')
        return result

class ReviewHTMLAnalysis(HTMLAnalysis):
    '''
    公司评价详情界面HTML解析。形如gsr
    '''

    def parse(self,url,html):
        if not url or not html:
            logger.info('传入参数不完整')
            return None
        logger.info('开始解析公司评价详情页面')
        soup = BeautifulSoup(html,'html.parser')
        new_url = self.getNewUrl(url,soup)
        new_data = self.getNewData(url,soup)
        logger.info('解析公司评价详情页面html成功')
        return new_url,new_data

    def getNewUrl(self,url,soup):
        '''
        查看前端界面可以看到跳转到具体评价详情的界面。只抓取前10条评价
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        new_urls = set()
        h3 = soup.find_all('h3','question_title')
        for h3 in h3:
            href = h3.find('a')['href']
            new_urls.add(urljoin(url,href))
        return new_urls

    def getNewData(self,url,soup):
        '''
        解析公司评价首页内容。包括公司名字和公司评分，公司评价标签
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        if not url or not soup:
            logger.info('参数错误')
            return None
        logger.info('开始获取公司详情数据'+url)
        title = soup.find('div','com_logo f_left').find('img')['title']    #公司名称
        score = soup.find('div','score_num').string                        #公司平均得分
        try:
            companytag = soup.find('dl','condition_item show-all').find_all('a')   #公司标签
        except Exception as e:
            companytag = None
        tags = []
        if tags:
            for tag in companytag:
                tags.append(tag.string.replace('\n','').replace('\t',''))
        result = [title,score,tags]
        return result

class ReviewDetailHTMLAnalysis(HTMLAnalysis):
    '''
    公司评价详情界面HTML解析。形如gsr
    '''

    def parse(self,url,html):
        if not url or not html:
            logger.info('传入参数不完整')
            return None
        logger.info('开始解析公司评价详情页面')
        soup = BeautifulSoup(html,'html.parser')
        if soup.find('p','grey_99 f_14 mt5'):
            logger.info('这家公司没有点评')
            return None
        new_url = self.getNewUrl(url,soup)
        new_data = self.getNewData(url,soup)
        logger.info('解析公司评价详情页面html成功')
        return new_url,new_data

    def getNewUrl(self,url,soup):
        '''
        查看前端界面可以看到跳转到具体评价详情的界面。只抓取前10条评价
        :param url:
        :param soup:
        :return:
        '''
        pass

    def getNewData(self,url,soup):
        '''
        解析公司评价详情内容。包括公司名字和评价详情，评价时间，星数，问题和对应答案
        [title, employee, commit_time, job, [question_title,question_content],[...]]]
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('参数错误')
            return None

        logger.info('开始获取公司评价详情数据'+url)
        title = soup.find('div','com_logo f_left').find('img')['title']    #公司名称

        employee_info = soup.find('p', 'grey_99 f_12 dd_bot').contents  # 包括评价人和评价时间
        employee = employee_info[0]    #评价人
        commit_time = employee_info[2].string  # 评价时间

        commit_info = soup.find('section', 'review_detail_content')  # 评价全部内容

        # 匹配去除字符串
        st = '【'+title + '】' + '怎么样？'
        job = commit_info.find('span', 'desc').string.replace(st, '')

        question_titles = commit_info.find_all('div', 'question_title')
        question_contents = commit_info.find_all('div', 'question_content')
        questions = []
        for i in range(len(question_titles)):
            questions.append(
                [question_titles[i].contents[1], question_contents[i].get_text().replace(' ', '').replace('\n\t', '')])

        result = [title, employee, commit_time, job, questions]
        return result

class SalaryHTMLAnalysis(HTMLAnalysis):
    #爬取工资界面

    def parse(self, url, html):
        pass

    def getNewUrl(self, url, soup):
        pass

    def getNewData(self, url, soup):
        pass

class InterviewHTMLAnalysis(HTMLAnalysis):
    #爬取面试界面
    def parse(self, url, html):
        '''
        重写虚类的parse方法，解析html
        :param url: 当前页面的url
        :param html: 当前页面得到的text即html文件
        :return:
        '''
        if not url or not html:
            logger.info('传入参数不完整')
            return None
        logger.info('开始解析公司面试经验页面')
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find('p','grey_99 f_14 mt5'):
            logger.info('这家公司现在没有面试经验，后边不用解析了')
            return None
        new_url = self.getNewUrl(url, soup)
        new_data = self.getNewData(url, soup)
        logger.info('解析公司面试经验页面html成功')
        return new_url, new_data

    def getNewUrl(self, url, soup):
        '''
        职位页面获取新url。这里不返回url
        :param url:
        :param soup:
        :return: 详情url
        '''
        # if soup.find('p','grey_99 f_14 mt5'):
        #     return None
        new_urls = set()
        hrefs = soup.find_all('h3','question_title')
        for href in hrefs:
            new_urls.add(urljoin(url,href.find('a')['href']))
        return new_urls

    def getNewData(self, url, soup):
        '''
        爬取面试经验文本。前十条
        [公司，面试难度]
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        # if soup.find('p','grey_99 f_14 mt5'):
        #     logging.info('无面经分享')
        #     return None
        title = soup.find('div','com_nav').find('a',ka='head-bread2').string
        try:
            interview_degree = soup.find('div','mt10 clearfix').find('em').string  #面试难度
        except Exception as e:
            interview_degree = 0
        result = [title,interview_degree]
        logger.info('获取公司面经界面' + url + '数据完毕，即将返回数据，list类型')
        return result

class InterviewDetailHTMLAnalysis(HTMLAnalysis):
    #爬取面试详情界面
    def parse(self, url, html):
        '''
        重写虚类的parse方法，解析html
        :param url: 当前页面的url
        :param html: 当前页面得到的text即html文件
        :return:
        '''
        if not url or not html:
            logger.info('传入参数不完整')
            return None
        logger.info('开始解析公司面试经验详情页面')
        soup = BeautifulSoup(html, 'html.parser')
        new_url = self.getNewUrl(url, soup)
        new_data = self.getNewData(url, soup)
        logger.info('解析公司面试经验详情页面html成功')
        return new_url, new_data

    def getNewUrl(self, url, soup):
        '''
        职位页面获取新url。这里不返回url
        :param url:
        :param soup:
        :return: 详情url
        '''
        return None

    def getNewData(self, url, soup):
        '''
        爬取面试经验文本。前十条
        [[公司，面试难度，职位，地点，面经标题，面经内容,],]
        :param url:
        :param soup:
        :return:
        '''
        if not url or not soup:
            logger.info('获取数据参数有误')
            return None
        title = soup.find('div','com_logo f_left').find('img')['title']

        interview_info = soup.find('section','interview_detail_content')   #包含面经全部内容的标签

        jobs = interview_info.find('p', 'f_12 dd_bot').contents  # 面试职位和时间
        job = jobs[0].replace('的面试经验', '').replace('\r\n\t', '').strip()
        interview_time = jobs[1].string  # 内部time标签

        city = interview_info.find('p', 'interview_address').string.replace('面试地点：','')  # 面试地点
        #面试经验的题目和内容
        interview_titles = interview_info.find('h1').contents
        interview_title = interview_titles[1].string  # 面试经验题目,a标签里

        interview_content = interview_info.find('div', 'question_content').get_text().replace(' ', '').replace('\n','')  # 面经内容，string
        #面试官问的问题，如果有
        question =interview_info.find('div','interview_qa')
        if question:
            #有的面经界面没有面试官问题，就判断一下。有的时候再取值
            question_title = question.find('p','question_title').contents[1]
            question_answer = question.find('p','question_content').contents[1]
        else:
            question_title = '无问题'
            question_answer = '无答案'

        result = [title, job, interview_time, city, [interview_title, interview_content],[question_title,question_answer]]
        logger.info('获取公司面经界面' + url + '数据完毕，即将返回数据，list类型')
        return result
