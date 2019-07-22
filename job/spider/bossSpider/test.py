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
job_info = {}
def getNewData(url,soup):
        '''
        职位页面获取职位相关数据
        :param url:
        :param soup:
        :return:
        '''
        result = []
        jobs = soup.find_all('div','job-primary')
        for job in jobs:
            jobId = job.find('div','info-primary').find('a')['data-jobid']
            result.append(job.find('div','job-title').string)     #获取职位名
            result.append(job.find('span', 'red').string)          #获取工资
            result.append(job.find('div', 'company-text').find('a').string)   #获取公司名称
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
            job_info[jobId] = [i for i in result]
            result.clear()
            print(job_info)

url = 'https://www.zhipin.com/c101280600/?query=python&page=1&ka=page-1'
import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
headers = {'User-Agent':user_agent}
res = requests.get(url,headers=headers)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text,'html.parser')
getNewData(url,soup)