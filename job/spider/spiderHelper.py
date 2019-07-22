#coding=utf-8
'''
*************************
file:       AnalysisJobs spiderHelper
author:     gongyi
date:       2019/7/15 19:09
****************************
change activity:
            2019/7/15 19:09
'''
#提供随机IP和随机Agent
import requests,json,re
import sys,os,time,pymysql,random
from bs4 import BeautifulSoup

#数据库设置：
USER = 'root'
PASSWORD = '123'
DATABASE = 'spider'
HOST = '192.168.0.106'
PORT = 3306

user_agent = [
    {'User-Agent':'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'},  #safari5.1–MAC
    {'User-Agent':'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'},        #safari5.1–Windows
    {'User-Agent':'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0'},#IE9.0
    {'User-Agent':'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)'}, #IE8.0
    {'User-Agent':'Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)'}, #IE7.0
    {'User-Agent':'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1'},     #Firefox4.0.1–MAC
    {'User-Agent':'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1'},  #
    {'User-Agent':'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11'},
    {'User-Agent':'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)'},
    {'User-Agent':'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)'},
    {'User-Agent':'Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
]

def get_agent():
    '''
    获取并返回随机agent
    :return:
    '''
    return random.sample(user_agent,1)[0]

class Proxy():
    #代理类.爬取解析获得新的代理ip，返回随机ip
    def __init__(self):
        self.url = 'https://www.xicidaili.com/nn/'+str(random.randint(1,10))
        self.data = []

    def getHTML(self):
        '''
        爬取并解析获得ip
        :return:
        '''
        url = self.url #'https://www.xicidaili.com/nn/1'
        #从user-agent列表中随机选择一个元素作为agent
        headers = get_agent()
        res = requests.get(url,headers=headers,timeout=20)
        res.encoding = 'utf-8'
        return res.text
        # print(res.text)
        # self.parse(res.text)
        # return str(random.sample(self.data,1)[0][0])


    def parse(self,html):
        '''
        根据传入的soup解析html内容，获得想要的返回值
        :param soup:
        :return:
        '''
        # soup = BeautifulSoup(html,'html.parser')
        #解析soup取出数据
        # try:
        re_ip = re.findall(r'<td>\d+\.\d+\.\d+\.\d+</td>',html)
        re_port = re.findall(r'<td>[\d]*</td>',html)
        re_live_time = re.findall(r'<td>\d*[小时分钟天]+</td>',html)
        re_check_time = re.findall(r'<td>\d*-\d*-\d* \d*:\d*</td>',html)
        l = min(len(list(re_ip)),len(re_port),len(re_live_time),len(re_check_time))
        print(len(re_ip),len(re_port),len(re_live_time),len(re_check_time))
        for i in range(l):
            ip = re_ip[i].replace('<td>','').replace('</td>','')
            # print(ip,end=' ')
            port = re_port[i].replace('<td>','').replace('</td>','')
            country = 'China'
            live_time = re_live_time[i].replace('<td>','').replace('</td>','')
            # print(live_time, end=' ')
            check_time = re_check_time[i].replace('<td>','').replace('</td>','')
            # print(check_time)
            proxy_status = 1
            self.data.append([ip,port,country,live_time,check_time,proxy_status])

        print('获取了{}条ip数据'.format(len(self.data)))
        # except Exception as e:
        #     print(e)

    def conn(self):
        '''
        连接mysql数据库
        :return:
        '''
        try:
            # 连接数据库
            conn = pymysql.Connect(host=HOST, user=USER, password=PASSWORD,
                                   database=DATABASE, port=PORT, charset='utf8')
            # 获取游标
            # cursor = conn.cursor()
            print('连接数据库成功')
            return conn
        except Exception as e:
            print('连接数据库出错', e)

    # import pysnooper
    def store(self):
        '''
        类里边存储数据
        :return:
        '''
        '''
            将爬取到的ip存储数据库。这里选择mysql数据库
            :param data:
            :return:
            '''

        sql = "insert into proxy_xici(proxy_ip,proxy_port,proxy_country,proxy_live_time,proxy_check_time,proxy_status) values (%s,%s,%s,%s,%s,%s)"
        conn = self.conn()
        cursor = conn.cursor()
        # 向表中写入数据
        try:
            for i in self.data:
                # print(i)
                cursor.execute(sql, i)
            conn.commit()
            cursor.close()
            conn.close()
            print('写入数据成功',len(self.data))
        except Exception as e:
            print('插入数据失败', e)

    def get(self):
        '''
        从数据库中获取一个ip
        :return:
        '''
        sql = 'select proxy_ip,proxy_port from proxy_xici where proxy_status=1 limit 1'
        sql1 = 'select count(proxy_ip) from proxy_xici where proxy_status=1'
        conn = self.conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        ip = cursor.fetchone()
        cursor.execute(sql1)
        count = cursor.fetchone()[0]
        print(ip,count)
        if count < 10:
            #如果表内可用IP小于10条，立刻重新爬取ip
            html = self.getHTML()
            self.parse(html)
            self.store()
        print('获取数据成功')
        cursor.close()
        conn.close()
        return ip




    def del_ip(self,ip):
        '''
        去除无效IP
        :return:
        '''
        sql = 'update proxy_xici set proxy_status=0 where proxy_ip=%s '
        conn = self.conn()
        cursor = conn.cursor()
        cursor.execute(sql,ip)
        conn.commit()
        cursor.close()
        conn.close()




def store(data):
    '''
    将爬取到的ip存储数据库。这里选择mysql数据库
    :param data:
    :return:
    '''
    try:
        #连接数据库
        conn = pymysql.Connect(host=HOST,user=USER, password=PASSWORD,
                 database=DATABASE, port=PORT,charset='utf8')
        #获取游标
        cursor = conn.cursor()
    except Exception as e:
        print('连接数据库出错',e)

    sql = "insert into proxy_xici('proxy_ip','proxy_port','proxy_country','proxy_live_time','proxy_check_time','proxy_status') values (%s,%s,%s,%s,%s,%s)"

    #向表中写入数据
    try:
        for i in data:
            cursor.execute(sql,i)
    except Exception as e:
        print('插入数据失败',e)




