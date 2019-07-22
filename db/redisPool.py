#coding=utf-8
'''
*************************
file:       AnalysisJobs redis-pool
author:     gongyi
date:       2019/7/14 15:44
****************************
change activity:
            2019/7/14 15:44
'''
import redis
from pymongo import MongoClient

# host = '192.168.0.106'
host = '127.0.0.1'
portRedis = 6379
portMongo = 27017
db = 0
pool = redis.ConnectionPool(host=host,port=portRedis,decode_responses=True,password=123456)

def getRedis():
    '''
    获取一个新的redis连接
    :return:
    '''
    conn = redis.Redis(connection_pool=pool)
    return conn

def getMongo(database,collection):
    '''
    获取一个新的mongo连接
    :param database:传入数据库名称
    :param collections:集合名称
    :return:
    '''
    conn = MongoClient(host,portMongo)
    db = conn[database]
    table = db[collection]
    return table

def getMongoNocollection(database):
    '''
    生成一个新的mongo连接，不指定数据表
    :param database:
    :return:
    '''
    conn = MongoClient(host,portMongo)
    db = conn[database]
    return db