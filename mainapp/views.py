import os
import random
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Max, Min, Avg, F, Q
from django.template import loader

from helloDjango import settings
from mainapp.models import UserEntity, FruitEntity, StoreEntity


# Create your views here.


def user_list(request):
    datas = [
        {'id': 101, 'name': 'a'},
        {'id': 102, 'name': 'b'},
        {'id': 103, 'name': 'c'},
    ]
    return render(request, 'user/list.html', {'users': datas, 'msg': '优秀学员'})


def user_list2(request):
    users = [
        {'id': 101, 'name': 'a'},
        {'id': 102, 'name': 'b'},
        {'id': 103, 'name': 'c'},
    ]
    msg = '优秀学员'
    return render(request, 'user/list.html', locals())


def user_list3(request):
    users = UserEntity.objects.all()
    msg = '优秀学员'
    error_index = random.randint(0, users.count()-1)
    vip = {
        'name': 'cxk',
        'money': 20000
    }
    names = ['ck', 'cxk', 'shj']
    info = '<h3>用户的个人简要</h3><p>我的家乡在平遥</p>'
    mes = "hhhhhaaaaahhhh"
    now = datetime.now()

    file_dir = os.path.join(settings.BASE_DIR, 'mainapp/')
    files = {file_name: os.stat(file_dir + file_name)
             for file_name in os.listdir(file_dir) if os.path.isfile(file_dir + file_name)}

    price = 19.1356

    img_html = "<img width=200 height=200 src='/media/store/ck.jpg'>"
    # return render(request, 'user/list.html', locals())

    # # 加载模板
    # template = loader.get_template('user/list.html')
    #
    # # 渲染模板
    # html = template.render(context={
    #     'msg': msg,
    #     'users': users
    # })

    # 此处的locals把request也纳入里面了
    html = loader.render_to_string('user/list.html', locals())
    return HttpResponse(html, status=200)  # 增加响应头？？


def add_user(request):
    # 从GET请求中读取数据
    # request.GET.get('name')
    # request.GET 是一个dict字典类型，保存的是查询参数
    name = request.GET.get('name', None)
    age = request.GET.get('age', 0)
    phone = request.GET.get('phone', None)

    # 验证数据是否完整
    if not all((name, age, phone)):
        return HttpResponse('<h3 style="color:red">请求参数不完整</h3>', status=400)
    u1 = UserEntity()
    u1.name = name
    u1.age = age
    u1.phone = phone
    u1.save()
    return redirect('/user/list')


def update_user(request):
    # 查询参数有id, name, phone
    id = request.GET.get('id', None)
    if not id:
        return HttpResponse('id参数必须提供', status=400)
    # 通过模型查询id的用户是否存在(表中的数据（记录）是否存在)
    try:
        # Model类.objects.get()可能会报异常--尝试捕获
        user = UserEntity.objects.get(pk=int(id))
        name = request.GET.get('name', None)
        phone = request.GET.get('phone', None)
        if any((name, phone)):  # name或 phone 任意一个存在即可
            if name:
                user.name = name

            if phone:
                user.phone = phone
            user.save()
            return redirect('/user/list')
    except:
        return HttpResponse('%s 的用户是不存在的' % id, status=404)


def delete_user(request):
    # 查询参数有id
    id = request.GET.get('id')
    # 验证id是否存在
    if id:
        try:
            user = UserEntity.objects.get(pk=int(id))
            user.delete()
            html = """
            <p>
            %s 删除成功！三秒后自动跳转到<a href="/user/list">列表</a>
            </p>
            <script>
                setTimeout(function(){
                    open('/user/list', target='_self')
                }, 3000)
            </script>
            """ % id
            return HttpResponse(html)
        except:
            return HttpResponse('%s 不存在' % id)
    else:
        return HttpResponse('必须提供id参数')


def find_fruit(request):
    # 从查询参数中获取价格区间price1，price2
    price1 = request.GET.get('price1', 0)
    price2 = request.GET.get('price2', 1000)
    # 根据价格区间查询满足条件中所有水果信息(filter和exclude可以连续交替着使用)
    fruits = FruitEntity.objects.filter(price__gte=price1, price__lte=price2)\
        .exclude(price=250)\
        .filter(name__contains='果')\
        .all()

    # 将查询的数据渲染到html模板中
    return render(request, 'fruit/list.html', locals())


def find_store(request):
    # 查询2021年开业的水果店
    # 查询参数：year
    queryset = StoreEntity.objects.filter(create_time__year=2021).oder_by('id', 'city')  # oder_by('-id')
    first_store = queryset.first()  # 模型类的实例对象
    # first()/get()/last()/count()/exists()=>bool/order_by()
    # values()==>①如果api接口，即返回json数据时，用此方法。(②还是QuerySet类对象)③每一条数据就是一个字典对象
    stores = queryset.all()
    return render(request, "store/list.html", locals())


def all_store(request):
    # 返回所有水果店的json数据
    result = {}
    if StoreEntity.objects.exists():
        datas = StoreEntity.objects.values()
        print(type(datas))  # list[{}, {}]？？XXX  | QuerySet对象<{查到的数据1}, {查到的数据2}, {}>

        store_list = []
        for store in datas:
            store_list.append(store)
        result['data'] = store_list
        result['total'] = StoreEntity.objects.count()
    else:
        result['msg'] = '数据是空的'

    return JsonResponse(result)


def count_fruit(request):
    # 返回json数据：统计每种分类的水果数量，最高价格，最低价格和总数据
    result = FruitEntity.objects.aggregate(cnt=Count('name'),
                                           max=Max('price'),
                                           min=Min('price'),
                                           avg=Avg('price'),
                                           sum=Sum('price'))
    # 全场水果打8.8折扣
    FruitEntity.objects.update(price=F('price')*0.88)
    fruits = FruitEntity.objects.values()
    fruits_list = []
    for fruit in fruits:
        fruits_list.append(fruit)

    # 查询价格低于50的，或者高于100的，或者源产地是北京且名字中包含"果"字
    fruits2 = FruitEntity.objects.filter(Q(price__lte=50) |
                                         Q(price_gte=100) |
                                         Q(Q(source='北京') & Q(name__contains="果"))).values()

    return JsonResponse({
        'count': result,
        'fruits': fruits_list,
        'multi_query': [fruit for fruit in fruits2]
    })
