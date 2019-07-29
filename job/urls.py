# coding=utf-8
'''
*************************
file:       AnalysisJobs urls
author:     gongyi
date:       2019/7/13 16:16
****************************
change activity:
            2019/7/13 16:16
'''
from django.conf.urls import url
from .views import getCompany,index,index_data,analysis

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'jobs',index_data,name='index_data'),
    url(r'analysis',analysis,name='analysis'),
    url(r'company',getCompany,name='company')
    # url(r'jobs/(?P<page>\d+)', show, name='show_page'),
]
