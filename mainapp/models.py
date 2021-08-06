import uuid

from django.contrib.auth.hashers import make_password
from django.db import models

# Create your models here.


class UserManager(models.Manager):
    def update(self, **kwargs):
        # 重写update方法
        password = kwargs.get('password', None)
        if password and len(password) < 50:
            print('我进update方法了')
            kwargs['password'] = make_password(password)
        super().update(**kwargs)


class UserEntity(models.Model):  # 客户的用户表
    # 默认情况下会自动创建id主键
    name = models.CharField(max_length=20, verbose_name='账号')  # 配置后台显示的名字
    age = models.IntegerField(default=0, verbose_name='年龄')
    phone = models.CharField(max_length=11, verbose_name='手机号',
                             null=True,  # 数据表的字段可以是null值
                             blank=True)  # 表示此项在站点的表单字段值可以不填写（为空）
    password = models.CharField(max_length=100, verbose_name='口令', blank=True, null=True)

    objects = UserManager()   # 重写manager的update方法

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # 通过后台管理进行的用户密码更新都今save这里，而不经update
        if len(self.password) < 50:
            # 明文转密文
            self.password = make_password(self.password)

        super().save()

    def __str__(self):
        return self.name

    class Meta:
        # 设置表名，指定当前模型类映射成哪一个表
        db_table = 'app_user'
        verbose_name = '客户管理'
        # 设置复数的表示方式
        verbose_name_plural = verbose_name


class RealProfile(models.Model):
    # 声明一对一的关联关系（与对应主键自动绑定）
    user = models.OneToOneField(UserEntity,
                                verbose_name='账号',
                                on_delete=models.CASCADE)  # 删除级联操作
    real_name = models.CharField(max_length=20, verbose_name='真实姓名')
    number = models.CharField(max_length=30, verbose_name='证件号')
    real_type = models.IntegerField(verbose_name='证件类型', choices=((0, '身份证'),
                                                                  (1, '护照'),
                                                                  (2, '驾驶证')))
    image1 = models.ImageField(verbose_name='正面照', upload_to='user/real')
    image2 = models.ImageField(verbose_name='反面照', upload_to='user/real')

    class Meta:
        db_table = 't_user_profile'
        verbose_name = verbose_name_plural = '实名认证表'

    def __str__(self):
        return self.real_name


class CartEntity(models.Model):
    class Meta:
        db_table = 't_cart'
        verbose_name = verbose_name_plural = '购物车表'

    user = models.OneToOneField(UserEntity,
                                on_delete=models.CASCADE,
                                verbose_name='账号')
    no = models.CharField(primary_key=True,
                          max_length=10,
                          verbose_name='购物车编号')

    def __str__(self):
        return self.no


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

    # 建立多对一的关联关系
    category = models.ForeignKey(CateTypeEntity,
                                 related_name='fruits',
                                 to_field='id',  # to_field表示是与对方表的谁建立关系
                                 on_delete=models.CASCADE,  # 是否可以进行级联删除
                                 blank=True)
    # 默认情况下，反向引用的名称是当前类的名称（小写）_set
    # 可以通过related_name来指定
    # db_table='t_collect'使用第三张表建立fruit和user的多对多关系
    users = models.ManyToManyField(UserEntity,
                                   db_table='t_collect',
                                   related_name='fruits',
                                   verbose_name='收藏用户列表',
                                   blank=True)
    # 这里使用字符串"TagEntity",是因为TagEntity模型类在当前模型的后面进行定义的
    # 也就是在当前代码的下方
    tags = models.ManyToManyField('TagEntity',
                                  db_table='t_fruit_tags',
                                  related_name='fruits',
                                  verbose_name='所有标签',
                                  blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 't_fruit'
        verbose_name = '水果表'
        verbose_name_plural = verbose_name


class TagEntity(models.Model):
    name = models.CharField(max_length=50,
                            unique=True,
                            verbose_name='标签名')
    order_num = models.IntegerField(default=1,
                                    verbose_name='序号')

    class Meta:
        db_table = 't_tag'
        verbose_name_plural = verbose_name = '标签表'
        ordering = ['-order_num']

    def __str__(self):
        return self.name


# 声明水果商品与购物车的关系表
class FruitCartEntity(models.Model):
    # 自动关联主键
    cart = models.ForeignKey(CartEntity, on_delete=models.CASCADE, verbose_name='购物车')
    fruit = models.ForeignKey(FruitEntity,
                              on_delete=models.CASCADE, verbose_name='水果名')

    cnt = models.IntegerField(verbose_name='数量', default=1)

    class Meta:
        db_table = 't_fruit_cart'
        verbose_name_plural = verbose_name = '购物车详情表'

    @property
    def price1(self):
        return self.fruit.price  # 从获取主的对象属性

    @property
    def price(self):
        # 属性方法在后台显示时没有verbose_name,如何解决？
        return round(self.cnt*self.fruit.price, 2)

    def __str__(self):
        return self.fruit.name + ':' + self.cart.no


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
