#coding=utf-8
'''
*************************
file:       AnalysisJobs redis-test
author:     gongyi
date:       2019/7/14 15:08
****************************
change activity:
            2019/7/14 15:08
'''
from db.DataClass import DataClass

db = DataClass('bossDB','bossDB')
print('建立与mongo的连接，指定了数据库与数据表')
line = db.connM.update({'jobId':123},{'$set':{'company':'huahua','company_score':222}},True)
print(line)