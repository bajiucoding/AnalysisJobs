from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from db import DataClass
import logging
from django_redis import get_redis_connection
from django.core.paginator import Paginator

from .spider.kanzhunSpider.Control import Control as kc
from .spider.bossSpider import Control as bc
# Create your views here.

logger = logging.getLogger('django_console')
db_boss = DataClass.DataClass('bossDB','bossDB')
# db_kanzhun = DataClass.DataClass('kanzhunDB','kanzhunDB')

def show(request):
    #调用爬虫
    # Control.Control().main()
    #从数据库中取出数据
    if request.method == 'GET':
        logger.info('开始了')

        #读取bossDB中的数据
        data_boss = list(db_boss.connM.find())
        # data_boss_job = list(db_boss.connM.find())
        logger.info('从boos中获得的数据'+str(list(data_boss)[0]))

        # company = data_boss['content'][2]

        db_kanzhun = DataClass.DataClass('kanzhunDB')
        for i in data_boss:
            company = i['content'][2]
            if company not in db_kanzhun.connM1.collection_names():
                # 该公司名字对应的数据库不存在，启动爬虫，爬取看准网上该公司相关信息
                logger.info('开始启动看准网爬虫'+company)
                kc(company).main(company)

        # 该公司已经被爬取过了
        # 直接读取看准网数据
            data_kanzhun = db_kanzhun.connM1[company].find({'title': 'company'})
            logger.info('看准网查询该公司信息：'+str(company)+'查出来了'+str(data_kanzhun.count()))
            if data_kanzhun.count() > 0:
                if 'companyScore' not in data_kanzhun[0]:
                    company_socre = 0
                else:
                    company_socre = data_kanzhun[0]['companyScore']
                if 'interviewDegree' in data_kanzhun[0]:
                    interview_degree = data_kanzhun[0]['interviewDegree']
                else:
                    interview_degree = 0

                #对company_score和interview


                # 从缓存中读取能力标签,这一步可以不要。show的时候肯定没有tags。之后加了登录注册可以加上这一步
                conn = get_redis_connection('default')
                logger.info('开始读取能力标签')
                tags = conn.smembers('tags')

                # 遍历工作信息
                jd = i['content'][-1]
                # 利用match方法匹配
                match_score = match(jd, tags)
                logger.info('匹配程度是：'+str(match_score))
                # 将匹配到的结果加入原数据中
                i['match_score'] = match_score

                logger.info('当前公司：' + str(company) + ':' + str(company_socre) + str(interview_degree)+str(match_score))
                recommended = recommend(match_score,interview_degree,company_socre)
                i['recommended'] = recommended
            else:
                i['match_score'] = '看准网无信息'
                i['recommended'] = '看准网无信息'

        # logger.info('view方法'+str(data_boss[0])+str(type(data_boss[0]['content']))+data_boss[0]['content'][0])
        logger.info('开始进行分页'+str(type(data_boss)))
        #将数据放入分页内，生成分页对象
        paginator = Paginator(data_boss,7)
        #设定当前页数
        page = request.GET.get('page')

        if not page:
            page = 1
        if int(page) > paginator.num_pages:
            page = 1
        page = int(page)
        #page页的数据
        page_info = paginator.page(page)
        logger.info('看下有没有分页数据')
        #总页数
        sum_pages = paginator.num_pages
        if sum_pages < 5:
            # 1-num_pages
            pages = range(1, sum_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif sum_pages - page <= 2:
            # num_pages-4,num_pages
            pages = range(sum_pages - 4, sum_pages + 1)
        else:
            # page-2,page+2
            pages = range(page - 2, page + 3)

        context = {
            'pages': pages,  # 分页的总页数
            'page_info': page_info,  # 每页的具体数据
            'data_boss': list(data_boss),  # 职位数据
        }
        return render(request, 'base.html',context)

def analysis(request):
    '''
    ajax后台方法，进行匹配指数计算和推荐指数计算并返回
    :return:
    '''
    db_kanzhun = DataClass.DataClass('kanzhunDB')
    data_boss = list(db_boss.connM.find())
    dic_match = {}
    dic_recommend = {}
    for i in data_boss:
        company = i['content'][2]
        data_kanzhun = db_kanzhun.connM1[company].find({'title': 'company'})
        if data_kanzhun.count() > 0:
            if 'companyScore' not in data_kanzhun[0]:
                company_socre = 0
            else:
                company_socre = data_kanzhun[0]['companyScore']
            if 'interviewDegree' in data_kanzhun[0]:
                interview_degree = data_kanzhun[0]['interviewDegree']
            else:
                interview_degree = 0

            # 对company_score和interview
            # 从缓存中读取能力标签
            conn = get_redis_connection('default')
            logger.info('开始读取能力标签')
            tags = conn.smembers('tags')

            # 遍历工作信息
            jd = i['content'][-1]
            # 利用match方法匹配
            match_score = match(jd, tags)
            logger.info('匹配程度是：' + str(match_score))

            # 将匹配到的结果加入字典
            dic_match['company'] = match_score

            logger.info('当前公司：' + str(company) + ':' + str(company_socre) + str(interview_degree) + str(match_score))
            recommended = recommend(match_score, interview_degree, company_socre)
            dic_recommend['company'] = recommended
        else:
            dic_match['company'] = '看准网无信息'
            dic_recommend['company'] = '看准网无信息'

    context = {
        'match':dic_match,
        'recommend':dic_recommend,
    }
    import json
    return render(request,'base.html',json.dumps(context))

def match(jd,tags):
    '''
    根据关键词匹配简历和公司情况得出匹配程度
    :param jd:招聘要求，字符串
    :param tags:集合，能力标签
    :return:
    '''
    logger.info('开始计算匹配程度')
    N = len(tags)
    if N==0:
        return 0
    count = 0
    for i in tags:
        if i in jd.encode('utf-8'):
            count += 1
    return round(count/N)

def getTags(request):
    '''
    获取能力标签存储缓存。计算匹配程度和推荐指数
    :return:
    '''
    logger.info('getTags方法被调用了'+str(request.method))
    get = request.GET
    tags = get.get('tags')
    logger.info('得到前台传过来的数据'+str(type(tags)))
    conn = get_redis_connection('default')  #按照预先的配置连接redis
    tag = tags.split(',')
    #将解析成列表的标签遍历加入redis的列表中
    for i in tag:
        conn.sadd('tags',i)

    db_kanzhun = DataClass.DataClass('kanzhunDB')
    data_boss = list(db_boss.connM.find())
    dic_match = {}
    dic_recommend = {}
    for i in data_boss:
        company = i['content'][2]
        data_kanzhun = db_kanzhun.connM1[company].find({'title': 'company'})
        if data_kanzhun.count() > 0:
            if 'companyScore' not in data_kanzhun[0]:
                company_socre = 0
            else:
                company_socre = data_kanzhun[0]['companyScore']
            if 'interviewDegree' in data_kanzhun[0]:
                interview_degree = data_kanzhun[0]['interviewDegree']
            else:
                interview_degree = 0

            # 对company_score和interview
            # 从缓存中读取能力标签
            conn = get_redis_connection('default')
            logger.info('开始读取能力标签')
            tags = conn.smembers('tags')

            # 遍历工作信息
            jd = i['content'][-1]
            # 利用match方法匹配
            match_score = match(jd, tags)
            logger.info('匹配程度是：' + str(match_score))

            # 将匹配到的结果加入字典
            dic_match[company] = match_score

            logger.info('当前公司：' + str(company) + ':' + str(company_socre) + str(interview_degree) + str(match_score))
            recommended = recommend(match_score, interview_degree, company_socre)
            dic_recommend[company] = recommended
        else:
            dic_match[company] = '看准网无信息'
            dic_recommend[company] = '看准网无信息'

    context = {
        'match': dic_match,
        'recommend': dic_recommend,
        'status':1,
    }
    import json
    return JsonResponse(context)
    # return render(request, 'base.html', json.dumps(context))

def recommend(match_score,interview_degree,company_socre):
    '''
    计算公司推荐指数
    :param match: 能力匹配程度
    :param interview: 面试难度
    :param review: 公司评分
    :return:
    '''
    recommended = 0.0
    logger.info('开始计算推荐指数')
    # 计算推荐指数。公司评分*0.8 + 面试难度 * 0.1 + 匹配程度 * 0.1
    # 匹配程度无，即未输入能力值标签时，面试难度权重为0.2
    if not company_socre:
        company_socre = 2.5
    if not interview_degree or interview_degree == 'None':
        interview_degree = 2.5
    if not match_score:
        match_score = 0.5
    logger.info('计算推荐指数时：此时' + str(company_socre) + str(interview_degree)+str(match_score))
    recommended = float(company_socre) * 0.8 + float(interview_degree) * 0.1 + float(match_score) * 0.1
    return round(recommended,2)


#展示公司详情
def getCompany(request,jobId,company):
    '''
    展示工作详情、公司评价和面试
    :param request:附带参数公司名字，工作jobId
    :return:公司评价、面试经验，工作jd
    '''
    data_boss = list(db_boss.connM.find({'jobId':jobId}))
    company_interview = DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'interview'})
    company_review = DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'review'})
    context = {
        'job':data_boss,
        'interview':company_interview,
        'review':company_review,
    }
    return render(request,'company.html')