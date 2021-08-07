from django.urls import path, re_path
from django.conf.urls import url

from orderapp import views

app_name = 'orderapp'

urlpatterns = [
    path('list/<city_code>/<order_num>', views.order_list, name='list'),
    path('cancel/<uuid:order_num>', views.cancel_order, name='cancel'),  # 指定参数类型
    re_path(r'^search/(?P<phone>1[3-57-9][\d]{9})$', views.search, name='search'),
    # url(r'^list2/(?P<city_code>\w+)/(?P<order_num>\d+)$', views.order_list)  # 老版本配置路由
    path('query', views.query)
]
