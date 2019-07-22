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
from .views import show,getTags,getCompany

urlpatterns = [
    url(r'^$', show, name='show'),
    url(r'getTags',getTags,name='getTags'),
    url(r'company/(?P<jobId>\d+)/(?P<company>\.+))',getCompany,name='company')
    # url(r'jobs/(?P<page>\d+)', show, name='show_page'),
]
