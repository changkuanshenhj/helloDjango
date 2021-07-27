import uuid

from django.db import models

# Create your models here.


class UserEntity(models.Model):  # 客户的用户表
    # 默认情况下会自动创建id主键
    name = models.CharField(max_length=20, verbose_name='账号')  # 配置后台显示的名字
    age = models.IntegerField(default=0, verbose_name='年龄')
    phone = models.CharField(max_length=11, verbose_name='手机号',
                             null=True,  # 数据表的字段可以是null值
                             blank=True)  # 表示此项在站点的表单字段值可以不填写（为空）

    def __str__(self):
        return self.name

    class Meta:
        # 设置表名，指定当前模型类映射成哪一个表
        db_table = 'app_user'
        verbose_name = '客户管理'
        # 设置复数的表示方式
        verbose_name_plural = verbose_name


# 水果分类模型
class CateTypeEntity(models.Model):
    name = models.CharField(max_length=20, verbose_name='分类名')

    order_num = models.IntegerField(verbose_name='排序')

    def __str__(self):
        # 相当于是对得到表中的哪一条数据，本来是一个object对象--->显示为当前设置的内容
        return self.name

    class Meta:
        app_label = 'mainapp'  # 指定应用的名称
        db_table = 't_category'
        ordering = ['order_num']  # 升序
        # ordering = ['-order_num'] 表示降序
        verbose_name = '水果分类'
        verbose_name_plural = verbose_name


class FruitEntity(models.Model):
    name = models.CharField(max_length=20,
                            verbose_name='水果名')
    price = models.FloatField(verbose_name='价格')
    source = models.CharField(max_length=30, verbose_name='源产地')
    category = models.ForeignKey(CateTypeEntity,
                                 on_delete=models.CASCADE)  # 是否可以进行级联删除

    def __str__(self):
        return self.name+"-"+self.source

    class Meta:
        db_table = 't_fruit'
        verbose_name = '水果表'
        verbose_name_plural = verbose_name


class StoreEntity(models.Model):
    # 默认情况下，模型自动创建主键id-字段----隐式
    # 但也可以显式的方式声明主键（primary key）
    id = models.UUIDField(primary_key=True, verbose_name='店号')

    name = models.CharField(max_length=50, verbose_name='店名')

    # 表中对应的字段是type_
    store_type = models.IntegerField(choices=((0, '自营'), (1, '第三方')), verbose_name='类型', db_column='type_')

    address = models.CharField(max_length=100, verbose_name='地址')

    # 支持城市搜索，所有要创建city索引"db_index"
    city = models.CharField(max_length=50, verbose_name='城市', db_index=True)

    logo = models.ImageField(verbose_name='LOGO',
                             upload_to='store',
                             width_field='logo_width',
                             height_field='logo_height',
                             blank=True,
                             null=True)

    logo_width = models.IntegerField(verbose_name='LOGO宽', null=True)

    logo_height = models.IntegerField(verbose_name='LOGO高', null=True)

    summary = models.TextField(verbose_name='商店介绍', blank=True, null=True)

    opened = models.BooleanField(verbose_name='是否开业', default=False)

    create_time = models.DateTimeField(verbose_name='成立时间', auto_now_add=True, null=True)

    last_time = models.DateTimeField(verbose_name='最后变更时间', auto_now=True, null=True)

    # 站点显示对象的字符串信息
    def __str__(self):
        return self.name+'-'+self.city

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # 调用模型保存方法时被调用(提前赋值)
        if not self.id:  # 判断是否为新增的
            self.id = uuid.uuid4().hex
        super().save()

    @property  # 装饰器
    def id_(self):
        # return str(self.id).replace('-', '')
        return self.id.hex

    class Meta:  # 元数据
        db_table = 't_store'
        unique_together = (('name', 'city'), )
        verbose_name = '水果店'
        verbose_name_plural = verbose_name
