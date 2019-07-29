#coding=utf-8
'''
*************************
file:       AnalysisJobs DataClass
author:     gongyi
date:       2019/7/14 12:23
****************************
change activity:
            2019/7/14 12:23
'''
import redis
from pymongo import MongoClient
from .redisPool import getRedis,getMongo,getMongoNocollection

class DataClass():
    #对数据的操作方法

    #
    def __init__(self,database,*args):
        '''
        初始化redis和mongo的连接
        '''
        #生成redis的新连接
        # self.connR = getRedis()    redis直接用redisPool
        #生成一个mongo的新连接，返回的是一个集合。这里不用
        if args:
            #这个连接时指定数据表
            self.connM = getMongo(database,args[0])

        #不指定数据表先建立连接
        self.connM1 = getMongoNocollection(database)

    # def