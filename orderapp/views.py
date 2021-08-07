from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse


def order_list(request, order_num, city_code):
    print(order_num, city_code)
    return render(request, 'list_order.html', locals())


def cancel_order(request, order_num):
    # order_num订单编号是UUID类型
    return render(request, 'list_order.html', locals())


def search(request, phone):
    return HttpResponse('hi,phone: %s ' % phone)


def query(request: HttpRequest):
    print(type(request.GET), request.GET)
    # 查询参数中code
    print(request.GET.code)
    # (1:按城市和订单号num查询，2:按手机号phone查询)
    # url = reverse('order:search', args=('15981394125', ))
    # return redirect(url)
    # url = reverse('order:list', args=('XA', 1009))
    url = reverse('order:list', kwargs=dict(city_code='BeiJing', order_num=1009))
    # return redirect(url)
    return HttpResponseRedirect(url)
    # return HttpResponse('Hi, Query %s' % url)
