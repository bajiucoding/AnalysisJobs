#coding=utf-8
'''
*************************
file:       AnalysisJobs spider_test
author:     gongyi
date:       2019/7/15 14:48
****************************
change activity:
            2019/7/15 14:48
'''
from Control import Control
from db import DataClass

db = DataClass.DataClass()
db.connR.delete('new_urls','old_urls')
db.connM.remove({})
print('已删除数据')
# spider = Control()
# spider.main()