#encoding=utf-8
from django.test import TestCase

# Create your tests here.
from db import DataClass

db_kanzhun = DataClass.DataClass('kanzhunDB')
company = '康博嘉'

from db.redisPool import getRedis
db = getRedis()
# tags = db.smembers('boss_old_urls')
# print(type(tags),tags)
# for i in tags:
#     print(i)

db_boss = DataClass.DataClass('bossDB','bossDB')
data_boss = list(db_boss.connM.find())
# print(data_boss.count())
# for i in data_boss:
#     # print(i['content'][10])
#     print('***********************************')
#     i['match'] = 1.1
#     print(i)
# li = list(data_boss)
print('列表：&&&&&&&&&&&&&7',data_boss)
# dblist = db_kanzhun.connM1.collection_names()
# data_kanzhun = db_kanzhun.connM1[company].find({'title':'company'})
# d1 =  db_kanzhun.connM1[company].find_one()
# print(d1)
# print('###############################################')
# print(data_kanzhun[0]['companyScore'])
# for i in data_kanzhun:
#     print(i)





