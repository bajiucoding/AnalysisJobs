#coding=utf-8
'''
*************************
file:       AnalysisJobs test
author:     gongyi
date:       2019/7/14 22:23
****************************
change activity:
            2019/7/14 22:23
'''
from job.spider.log import logger
import requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
logger = logger('test_log')


# url = 'https://www.kanzhun.com/pl6177100.html'

def get_data(url,soup):
    if not url or not soup:
        logger.info('参数错误')
        return None
    logger.info('开始获取公司评价详情数据' + url)
    title = soup.find('div', 'com_logo f_left').find('img')['title']  # 公司名称

    employee_info = soup.find('p', 'grey_99 f_12 dd_bot').contents  # 包括评价人和评价时间
    employee = employee_info[0]  # 评价人
    commit_time = employee_info[2].string  # 评价时间

    commit_info = soup.find('section', 'review_detail_content')  # 评价全部内容

    # 匹配去除字符串
    st = '【'+title + '】' + '怎么样？'
    print(st)
    job = commit_info.find('span', 'desc').string.replace(st, '')

    question_titles = commit_info.find_all('div', 'question_title')
    question_contents = commit_info.find_all('div', 'question_content')
    questions = []
    for i in range(len(question_titles)):
        questions.append(
            [question_titles[i].contents[1], question_contents[i].get_text().replace(' ', '').replace('\n\t', '')])

    result = [title, employee, commit_time, job, questions]
    print(result)

url = 'https://www.kanzhun.com/pl6584467.html'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
headers = {'User-Agent':user_agent}
res = requests.get(url,headers=headers,timeout=2)
print('success')
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text,'html.parser')
get_data(url,soup)
