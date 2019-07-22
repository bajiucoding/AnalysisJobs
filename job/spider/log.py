#coding=utf-8
'''
*************************
file:       AnalysisJobs log
author:     gongyi
date:       2019/7/14 17:24
****************************
change activity:
            2019/7/14 17:24
'''
import logging
from django.conf import settings
def logger(log_type):
    '''
    日志初始配置函数
    :param log_type:
    :return:
    '''

    logLevel = logging.INFO
    # 创建日志
    my_logger = logging.getLogger(log_type)
    my_logger.setLevel(logLevel)

    # 创建日志输出
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)

    #创建文件句柄，设置级别
    log_file = 'log/debug.log'
    fh  = logging.FileHandler(log_file)
    fh.setLevel(logLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)


    my_logger.addHandler(fh)
    return my_logger
