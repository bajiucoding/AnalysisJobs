from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from django.views.generic import View
from db import DataClass
import logging
from django_redis import get_redis_connection
from django.core.paginator import Paginator
import multiprocessing,threading
from .spider.kanzhunSpider.Control import Control as kanzhunC
from .spider.bossSpider.Control import Control as bc
# Create your views here.

logger = logging.getLogger('django_console')
db_boss = DataClass.DataClass('bossDB','bossDB')
# db_kanzhun = DataClass.DataClass('kanzhunDB','kanzhunDB')

def start_kanzhun(company):
    print('看准网线程********',company)
    kc = kanzhunC(company)
    kc.main(company)

def start_boss(job,city_code):
    bc().main(job, city_code)

def index(request):
    '''
    全部用GET方式
    :param request:
    :return:
    '''
    logger.info('返回首页')
    return render(request, 'jobs2.html')

def index_data(request):
    '''
    点击查找按钮后返回查找的数据
    :param request:
    :return:
    '''
    logger.info('index_data方法，根据city和job查找数据并分页返回')

    # 对city和job的操作
    job = request.GET.get('job')
    city = request.GET.get('city')

    city_code = 'c101280600'  # 现在默认城市为深圳
    #
    #这个设置缓存应该是不用了
    if not all([job,city]):
        logger.info('初次进入，没有城市和职位，用默认值')
        city = request.session.get('job','深圳')
        job = request.session.get('city','python')
    else:
        #如果有这俩值，就设置缓存
        request.session['job'] = job
        request.session['city'] = city
    logger.info('得到的信息：' + str(city) + str(job))


    page = int(request.GET.get('page',1))
    logger.info('对处理好的数据分页并返回,当前页数：'+str(page))
    count = 7
    next = (page-1) * 7    #后一页的数据
    import math
    page_count = math.ceil(len(list(db_boss.connM.find({'job': {'$regex':job,'$options':'i'}, 'city': city})))/count)   #数据库中总页数

    if page_count < 5:
        page_counts = range(1, page_count + 1)
    elif page <= 3:
        page_counts = range(1, 6)
    elif page_count - page <= 2:
        page_counts = range(page_count - 4, page_count + 1)
    else:
        page_counts = range(page - 2, page + 3)
    # city = '深圳'
    # job = 'python'
    # 根据job和city信息取出数据库中的数据
    data_boss = list(db_boss.connM.find({'job': {'$regex':job,'$options':'i'}, 'city': city}).limit(count).skip(next))
    logger.info('获得了' + str(len(data_boss)) + '条数据')



    # if (len(data_boss) == 0):
    #     # 如果没取到数据，启动boss直聘爬虫
    #     logger.info('数据库中没数据，开始boss直聘爬虫进程')
    #     bc().main(job, city_code)
    #     # p = multiprocessing.Process(target=start_boss,args=(job,city_code,))
    #     # p.start()
    #     # t1 = threading.Thread(target=start_boss,args=(job,city_code,))
    #     # t1.start()
    #
    # else:
    #     # 这里应该加上对现有数据准确性的核对
    #     pass

    # 建立对于mongdb中看准网数据的连接
    db_kanzhun = DataClass.DataClass('kanzhunDB')

    # 处理数据，与看准网数据进程匹配。根据是否有能力标签，计算匹配程度
    for i in data_boss:
        # 取出公司信息根据公司名称取出看准网数据，没有就启动爬虫
        company = i['content'][2]



        # if company not in db_kanzhun.connM1.collection_names():
            # 公司名称不存在与看准网数据库的集合名中，说明没数据，启动看准网爬虫
            # logger.info('开始启动看准网爬虫进程，爬取' + company + '的数据')
            # kanzhunC(company).main(company)  # 第一个company是在爬虫内部建立根据公司名命名的collection集合
            # p2 = multiprocessing.Process(target=start_kanzhun,args=(company,))
            # t2 = threading.Thread(target=start_kanzhun,args=(company,))
            # t2.start()



        # context['salary'] = i['content'][1]
        logger.info(company)
        # 这时候，已经有数据了，开始对看准网数据进行梳理
        data_kanzhun = db_kanzhun.connM1[company].find({'title': 'company'})
        logger.info('取出看准网相关数据')

        if data_kanzhun.count() > 0:
            # 数据库里有公司相关的数据
            if 'companyScore' not in data_kanzhun[0]:
                # 没有公司评分
                company_score = None
            else:
                company_score = data_kanzhun[0]['companyScore']

            if 'interviewDegree' not in data_kanzhun[0]:
                interview_degree = None
            else:
                interview_degree = data_kanzhun[0]['interviewDegree']

            # 读取工作jd
            jd = i['content'][-1]

            i['company_score'] = company_score
            i['interview'] = interview_degree

        else:
            # 数据库中有这个公司的数据集合，但是为空。说明该公司在看准网上没数据
            i['company_score'] = '看准网没数据'
            i['interview'] = '看准网没数据'





    context = {
        'data_boss': data_boss,  # 职位数据
        'page':page,              #当前页码
        'page_counts':page_counts,   #分页范围
        'page_count':page_count      #总页数
    }

    return render(request, 'jobs.html', context)

def analysis(request):
    '''
    ajax后台方法，进行匹配指数计算和推荐指数计算并返回
    :return:
    '''
    logger.info('analysis方法开始调用')

    conn = get_redis_connection('default')  # 按照预先的配置连接redis
    tags = request.POST.get('tags')
    logger.info('&&&&&&&&&&&&&&&当前标签非缓存中是：' + str(tags))
    if not tags:
        tags = conn.smembers('tags')
        logger.info('&&&&&&&&&&&&&&&当前标签是：'+str(tags))
    else:
        logger.info('得到前台传过来的数据' + str(type(tags)))
        tag = tags.split(',')
        # 将解析成列表的标签遍历加入redis的列表中
        for i in tag:
            conn.sadd('tags', i)

    db_kanzhun = DataClass.DataClass('kanzhunDB')
    # 对city和job的操作
    job = request.GET.get('job')
    city = request.GET.get('city')
    city_code = 'c101280600'  # 现在默认城市为深圳
    #

    if not all([job, city]):
        logger.info('初次进入，没有城市和职位，读取缓存值')
        job = request.session.get('job', 'python')
        city = request.session.get('city', '深圳')
    else:
        # 如果有这俩值，就设置缓存
        request.session['job'] = job
        request.session['city'] = city
    logger.info('得到的信息：' + str(city) + str(job))

    # city = '深圳'
    # job = 'python'
    # 根据job和city信息取出数据库中的数据
    page = int(request.GET.get('page', 1))
    logger.info('对处理好的数据分页并返回,当前页数：'+str(page))
    count = 7
    next = (page - 1) * 7  # 后一页的数据
    import math
    page_count = math.ceil(
        len(list(db_boss.connM.find({'job': {'$regex': job, '$options': 'i'}, 'city': city}))) / count)  # 数据库中总页数

    if page_count < 5:
        page_counts = range(1, page_count + 1)
    elif page <= 3:
        page_counts = range(1, 6)
    elif page_count - page <= 2:
        page_counts = range(page_count - 4, page_count + 1)
    else:
        page_counts = range(page - 2, page + 3)
    # city = '深圳'
    # job = 'python'
    # 根据job和city信息取出数据库中的数据
    data_boss = list(
        db_boss.connM.find({'job': {'$regex': job, '$options': 'i'}, 'city': city}).limit(count).skip(next))
    logger.info('获得了' + str(len(data_boss)) + '条数据')

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

            # 遍历工作信息
            jd = i['content'][-1]
            # 利用match方法匹配
            match_score = match(jd, tags)
            logger.info('匹配程度是：' + str(match_score))


            logger.info('当前公司：' + str(company) + ':' + str(company_socre) + str(interview_degree) + str(match_score))
            recommended = recommend(match_score, interview_degree, company_socre)

            i['match'] = match_score
            i['recommend'] = recommended
        else:
            i['match'] = '看准网无信息'
            i['recommend'] = '看准网无信息'

    logger.info('analysis开始返回数据')
    context = {
        'page': page,  # 当前页
        'page_count': page_count,  # 总页数
        'page_counts':page_counts,  #分页范围
        'data_boss': data_boss,  # 职位数据
    }

    return render(request,'jobs1.html',context)

def match(jd,tags):
    '''
    根据关键词匹配简历和公司情况得出匹配程度
    :param jd:招聘要求，字符串
    :param tags:集合，能力标签
    :return:
    '''
    logger.info('开始计算匹配程度'+str(tags))
    N = len(tags)
    if N==0:
        return 0
    count = 0
    for i in tags:
        if str(i) in jd:
            count += 1
    return round(count/N)


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
        recommended = float(interview_degree) * 0.1 + float(match_score) * 0.9
    elif not interview_degree or interview_degree == 'None':
        recommended = float(company_socre) * 0.8 + float(match_score) * 0.2
    elif not match_score:
        recommended = float(company_socre) * 0.9 + float(interview_degree) * 0.1
    else:
        recommended = float(company_socre) * 0.8 + float(interview_degree) * 0.1 + float(match_score) * 0.1
    return round(recommended,2)


#展示公司详情
def getCompany(request):
    '''
    展示工作详情、公司评价和面试
    :param request:附带参数公司名字，工作jobId
    :return:公司评价、面试经验，工作jd
    '''
    logger.info('开始展示公司详情')
    jobId = request.GET.get('jobId')
    company = request.GET.get('company')
    logger.info('获得数据'+str(jobId)+company)
    data_boss = list(db_boss.connM.find({'jobId':jobId}))
    company_interview = list(DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'interview'},{'_id':0,'title':0}))
    company_review = list(DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'review'},{'_id':0,'title':0}))
    #读取标签和面试难度、公司评分等数据
    company_tags = list(DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'company'},{'companyTags':1,'_id':0}))[0]
    interview_degree = list(DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'company'},{'_id':0,'interviewDegree':1}))[0]
    companyScore = list(DataClass.DataClass('kanzhunDB').connM1[company].find({'title': 'company'},{'_id':0,'companyScore':1}))[0]
    logger.info('从数据库取出数据'+str(len(data_boss))+'公司评价'+str(len(company_review))+'公司面试经验'+str(len(company_interview)))

    # url = request.get_full_path()
    # if not company_review:
    #     return HttpResponse('暂时无该公司数据')

    # print(data_boss,'\n',company_review[0])
    context = {
        'jobs':data_boss,
        'interviews':company_interview,
        'reviews':company_review,
        'company_tags':company_tags,
        'interview_degree':interview_degree,
        'company_score':companyScore,

    }
    return render(request,'company.html',context)




