#coding=utf-8
'''
*************************
file:       AnalysisJobs log_choose
author:     gongyi
date:       2019/7/24 17:32
****************************
change activity:
            2019/7/24 17:32
'''
import logging

def log(func):
    '''
    装饰器，判断传入函数参数中的url决定采用哪种log配置
    :param func:
    :return:
    '''
    def wrapper(*args,**kwargs):
        url = args[0]
        if 'zhibin' in url:
            logger = logging.getLogger('boss')
        else:
            logger = logging.getLogger('kanzhun')
    return wrapper