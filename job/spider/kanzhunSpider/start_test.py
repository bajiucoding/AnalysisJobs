#coding=utf-8
'''
*************************
file:       AnalysisJobs start_test
author:     gongyi
date:       2019/7/17 18:13
****************************
change activity:
            2019/7/17 18:13
'''
#清除数据库现有数据并重新启动爬虫
from db import DataClass
from pymongo import MongoClient

# 删除redis
db = DataClass.DataClass('kanzhunDB','kanzhunDB')
db.connR.delete('kanzhun_new_urls','kanzhun_old_urls')

#删除mongo
conn = MongoClient('192.168.0.106',27017)
connM = conn.kanzhunDB
conn.drop_database('kanzhunDB')
print('已删除数据')