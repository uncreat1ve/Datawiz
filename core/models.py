# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import *
from django.contrib.auth.models import User
from core.managers import *
import logging
import pandas as pd
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField, JSONField

# from core.cache import (CashierCache,ShopCache,ProductCache,LoyaltyCache,ReceiptCache,
#                         ShopGroupCache,TerminalCache,UnitCache, CategoryCache)


log = logging.getLogger(__name__)


class ArrayAgg(Aggregate):

    function = 'array_agg'
    template = '%(function)s(DISTINCT %(expressions)s)'

    def __init__(self, expression, **extra):
        super(ArrayAgg, self).__init__(
            expression,
            output_field=ArrayField(models.IntegerField()),
            **extra
        )


class Region(models.Model):
    name = models.CharField(max_length=200)


class Client(models.Model):
    name = models.CharField(max_length=200, blank=False)
    def_category_level = models.IntegerField(blank=False,
                                             null=False,
                                             default=-1
                                             )
    date_from = models.DateTimeField(null=True)
    date_to = models.DateTimeField(null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    testing = models.BooleanField(null=False, default=True)
    is_predict = models.BooleanField(null=False, default=False)
    WKToken = models.CharField(max_length=60, blank=True, null=True)
    is_workabox = models.BooleanField(null=False, default=False)
    posterToken = models.CharField(max_length=60, blank=True, null=True)
    is_poster = models.BooleanField(null=False, default=False)
    dirty = models.BooleanField(null=False, default=False)
    activated = models.BooleanField(null=False, default=False)
    initialized = models.BooleanField(null=False, default=False)
    ip_client = models.CharField(max_length=15, null=True)
    receipts_qty = models.IntegerField(default=0)
    cartitems_qty = models.IntegerField(default=0)
    status = models.BooleanField(null=False, default=True)

    def __unicode__(self):
        return '%s' % self.name

class ShopGroup(models.Model):

    name = models.CharField(max_length=150)
    identifier = models.CharField(max_length=50, blank=True)
    parent_identifier = models.CharField(max_length=50, blank=True)
    client = models.ForeignKey(
        Client,
        related_name='shop_groups',
        on_delete=models.PROTECT
    )
    path = JSONField(null=True)
    parent = models.ForeignKey("ShopGroup", related_name="children", null=True)
    l = models.IntegerField(null=True)
    r = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)

    # cache = ShopGroupCache()

    def __unicode__(self):
        return '%s' % self.name



class Shop(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, blank=True, default='')
    client = models.ForeignKey(
        Client,
        related_name='shops',
        on_delete=models.PROTECT
    )
    # defvalue = models.BooleanField(null=False, default=False)
    address = models.TextField(null=True)
    open_date = models.DateField(null=True)
    group = models.ManyToManyField("ShopGroup",through='Shop_ShopGroup')

    # path = models.TextField(blank=True, null=True)
    # parent = models.ForeignKey('Shop', null=True)
    # l = models.IntegerField(null=True)
    # r = models.IntegerField(null=True)
    # level = models.IntegerField(null=True)
    markers = JSONField(null=True)
    area = models.FloatField(null=True, blank=True, default=1)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)

    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)

    # cache = ShopCache()

    class Meta:
        unique_together = (('client', 'identifier'),)

    def __unicode__(self):
        return '%s' % self.name

    # def get_children(self):
    #     return Shop.objects.filter(l__gt=self.l, r__lt=self.r, client=self.client)
    #
    # def get_children_ids(self):
    #     shopsValues = Shop.objects.filter(l__gt=self.l, r__lt=self.r, client=self.client).values(
    #         'id')
    #     return [shop['id'] for shop in shopsValues]


class Shop_ShopGroup(models.Model):
    shop = models.ForeignKey(Shop,related_name='shop_shopgroup_shop')
    group = models.ForeignKey(ShopGroup, related_name='shop_shopgroup_group')


class Shop_location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=10, decimal_places=8)
    color = models.CharField(max_length=50)
    chain_shop = models.CharField(max_length=100)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, null=True)
    picture = models.ImageField(upload_to='picture_shop', null=True)

    class Meta:
        unique_together = (('name', 'address', 'chain_shop'),)
        index_together = ['shop']


class Unit(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    packed = models.BooleanField(null=False, default=True)
    identifier = models.CharField(max_length=50,
                                  null=False,
                                  blank=True,
                                  default=''
                                  )
    pack_capacity = models.PositiveSmallIntegerField(null=False, default=1)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)

    # cache = UnitCache()
    class Meta:
        unique_together = (('client', 'identifier'),)
        index_together = ['client']

class Terminal(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, blank=True, default='')
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    shop = models.ForeignKey(
        Shop,
        related_name='terminals',
        on_delete=models.PROTECT
    )
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)
    # cache = TerminalCache()
    class Meta:
        unique_together = (('client', 'shop', 'identifier'),)
        index_together = [['client'],['shop']]


class Cashier(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, blank=True, default='')
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)
    # cache = CashierCache()
    class Meta:
        unique_together = (('client', 'identifier'),)
        index_together = ['client']


class Category_day_sum(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    dt = models.DateTimeField()
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    avg_receipt = models.DecimalField(decimal_places=4, max_digits=20)
    receipts_qty = models.IntegerField()
    stock_qty = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_total_price = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    original_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    margin_price_unit = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    margin_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    week_day = models.IntegerField()

    class Meta:
        unique_together = (('client', 'category', 'dt', 'shop'),)
        index_together = [['client'], ['category'], ['client', 'category', 'dt', 'shop']]

class Category_hour_sum(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    date = models.DateTimeField(null=True)
    dt = models.DateField()
    hour = models.IntegerField()
    week_day = models.IntegerField()
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    receipts_qty = models.DecimalField(decimal_places=4, max_digits=20)
    avg_receipt = models.DecimalField(decimal_places=4, max_digits=20)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        unique_together = (('client', 'category', 'shop', 'date'), ('client', 'category', 'shop', 'dt', 'hour'))
        index_together = [['client', 'category'], ['client', 'category', 'dt', 'shop']]


class Category(models.Model):
    identifier = models.CharField(max_length=100, blank=True, default='')
    parent_identifier = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200)
    path = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('Category', null=True, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    l = models.IntegerField(null=True)
    r = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)

    # objects = CategoryManager()
    # cache = CategoryCache()

    class Meta:
        unique_together = (('client', 'identifier'),)
        index_together = [['client'], ['client', 'l', 'r', 'level'],['parent']]

    def __unicode__(self):
        return '%s' % self.name

    def get_descendant_category(self, level=None):
        descendant = Category.objects.filter(
            client_id=self.client_id,
            l__gt=self.l,
            r__lt=self.r,
            # cartItems_qty__gt = 0,
        )
        if level:
            descendant = descendant.filter(level=level)
        return descendant

    def parent_categories(self):
        category = self
        categories_list = []
        while category is not None:
            categories_list += [category]
            category = category.parent
        categories_list.reverse()

        return categories_list

    def children(self):
        return self.category_set.all()

    def products(self):
        return self.product_set.all()

    def get_products_bellow(self):
        return Product.objects.filter(client_id=self.client_id,
                                      category__l__gte=self.l,
                                      category__r__lte=self.r
                                      )

    @staticmethod
    def getSalesperProduct(shops, item_type, item_id, date_from, date_to):
        """
        Формування даних для виводу обороту та різниці в к-сті проданого товару
        по тижням даних по вказаній категорії/вказаному продукту

        вхідні параметри::
        shops - list|str -список магазинів (list або рядок типу
                'id1,id2,id3,...')
        item_type - str - тип елементу: 'category'|'product'
        item_id - int - id елементу
        date_from - date|datetime - початкова дата останнього періоду
                    (active_range) (див.пояснення в _prepare_performance_date()
        date_to - date|datetime - кінцева дата останнього періоду active_range

        результат:
        словник (dict) виду (дані згруповано по тижням, дата вказує на перший день тижня):
        { "columns_chart_values": [[ date(%Y,%m,%d), delta ], ...]
          "name": category/product name
        }
        """
        if item_type == 'product':
            product = Product.objects.get(id=item_id)
            item_name = product.name
            products = [product]
        else:
            category = Category.objects.get(id=item_id)
            item_name = category.name
            products = category.get_products_bellow()

        dr = Product_day_sum.objects \
            .filter(product__in=products, date__lte=date_to) \
            .values('date', 'qty', 'total_price')
        df = pd.DataFrame().from_records(dr, index='date', coerce_float=True)
        df = df.resample('7d', how='sum')
        df['delta'] = df['qty']  # /df['qty'].mean()-1

        df = df.reset_index().fillna(0)
        df['date'] = df['date'].apply(lambda dt: "%s,%s,%s" % (dt.year, dt.month - 1, dt.day))
        df = df[['date', 'delta', 'total_price']]

        result = {
            'column_chart_values': df.to_dict(orient='split')['data'],
            'name': item_name
        }
        return result


class Product_day_sum(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    dt = models.DateField()
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    avg_receipt = models.DecimalField(decimal_places=4, max_digits=20)
    price = models.DecimalField(decimal_places=4, max_digits=20)
    receipts_qty = models.IntegerField(null=False, default=0)
    week_day = models.IntegerField(null=False, default=0)
    original_price_unit = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    original_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    margin_price_unit = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    margin_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_qty = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_total_price = models.DecimalField(decimal_places=4, max_digits=20, default=0)

    class Meta:
        unique_together = (('client', 'shop', 'dt', 'product'),)
        index_together = [['client', 'shop', 'dt', 'product'], ['product'],
                          ['client', 'shop', 'dt'], ['client']]


class Brand(models.Model):
    identifier = models.CharField(max_length=100)
    client = models.ForeignKey(Client, related_name="brands", on_delete=models.PROTECT)
    name = models.CharField(max_length=200)

    api_updated = models.DateTimeField(null=False,auto_now_add=True)
    api_changed = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = (('client', 'identifier'),)


class BrandSupplier(models.Model):
    client = models.ForeignKey(Client, related_name="brands_supplier", on_delete=models.PROTECT)
    bonus = models.DecimalField(decimal_places=3, max_digits=10, default=0)
    deferment = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand)
    supplier = models.ForeignKey('stock.Supplier', related_name="supplier__brands",)

    api_updated = models.DateTimeField(null=False,auto_now_add=True)
    api_changed = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = (('client', 'brand', 'supplier'),)


class Product(models.Model):
    identifier = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200)
    unit = models.ForeignKey('Unit', null=True, on_delete=models.PROTECT)
    category = models.ForeignKey('Category', null=True, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    article = models.CharField(null=True, max_length=100)
    old_id = models.CharField(max_length=100)
    first_sale = models.DateField(auto_now_add=True, blank=True, null=True)
    photo = models.ImageField(upload_to='photo_products', null=True)
    barcode = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(Brand, related_name="products")
    markers = JSONField(null=True)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)
    # objects = ProductManager()
    # cache = ProductCache()
    class Meta:
        unique_together = (('client', 'old_id'),)
        index_together = [['client', 'category', 'id'], ['client'], ['category']]

    def __unicode__(self):
        return '%s' % self.name


class Product_date_prices(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,related_name='core_product_price')
    identifier = models.CharField(max_length=100, null=True)
    dt = models.DateField()
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT,related_name='core_shop_price')
    original_price = models.DecimalField(decimal_places=4, max_digits=20)
    price = models.DecimalField(decimal_places=4, max_digits=20)
    margin = models.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        unique_together = (('client', 'product', 'shop', 'dt'),)
        index_together = [['client', 'shop', 'dt', 'product'], ['product'],
                          ['client', 'shop', 'dt'], ['client']]

class Loyalty(models.Model):
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.PROTECT)
    identifier = models.CharField(max_length=50, null=False, blank=True, default='')
    cardno = models.CharField(max_length=20, null=True)
    discount = models.DecimalField(decimal_places=2, max_digits=20, null=True, default=0)
    client_name = models.CharField(max_length=200, blank=True, null=False, default='')
    client_birthday = models.DateField(null=True)
    is_male = models.NullBooleanField(null=True)
    turnover = models.DecimalField(decimal_places=2, max_digits=20, null=True, default=0)
    api_updated = models.DateTimeField(null=True)
    api_changed = models.BooleanField(null=False, default=False)
    age = models.IntegerField(null=True)
    first_visit = models.DateTimeField(null=True)
    last_visit = models.DateTimeField(null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    email = models.CharField(max_length=75, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    # cache = LoyaltyCache()
    class Meta:
        unique_together = (('client', 'identifier'),)
        index_together = [['client'],]


class Receipt(models.Model):
    date = models.DateTimeField()
    dt = models.DateField()  # filled automatically from `date` field
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=200)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    cartItems_qty = models.IntegerField()
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    items_qty = models.DecimalField(decimal_places=4, max_digits=20)
    terminal = models.ForeignKey(Terminal, null=True, on_delete=models.PROTECT)
    loyalty = models.ForeignKey(Loyalty, null=True, on_delete=models.PROTECT)
    cashier = models.ForeignKey(Cashier, null=True, on_delete=models.PROTECT)
    products_list = ArrayField(models.IntegerField(),null=True)
    week_day = models.IntegerField()
    hour = models.IntegerField()
    margin_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)

    # objects = ReceiptManager.from_queryset(ReceiptQuerySet)()
    # cache = ReceiptCache()

    class Meta:
        unique_together = (('client', 'shop', 'date', 'terminal', 'order_id'),)
        index_together = [['client'], ['client', 'dt', 'shop'], ['shop'],
                          ['loyalty'], ['client', 'loyalty'],
                          ['client', 'shop', 'dt', 'week_day', 'hour', 'total_price']]

    def get_carts(self):
        return self.cartitem_set.all()

    def __unicode__(self):
        if self.terminal:
            terminal_name = self.terminal.name
        else:
            terminal_name = ''
        return '%s %s [%s] %s:%s' % (
        self.order_id, self.date, self.client.name, self.shop.name, terminal_name)


class Receipt_day_sum(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    dt = models.DateField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    receipts_qty = models.DecimalField(decimal_places=4, max_digits=20)
    avg_receipt = models.DecimalField(decimal_places=4, max_digits=20)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    week_day = models.IntegerField()
    margin_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_qty = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_total_price = models.DecimalField(decimal_places=4, max_digits=20, default=0)

    class Meta:
        unique_together = ['client', 'dt', 'shop']
        index_together = [['client'], ['client', 'dt', 'shop']]


class Receipt_hour_sum(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField()
    dt = models.DateField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    receipts_qty = models.DecimalField(decimal_places=4, max_digits=20)
    avg_receipt = models.DecimalField(decimal_places=4, max_digits=20)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    week_day = models.IntegerField()
    hour = models.IntegerField()

    class Meta:
        unique_together = ['client', 'date', 'shop']
        index_together = [['client'], ['client', 'dt', 'shop']]



class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    base_price = models.DecimalField(decimal_places=4, max_digits=20)
    price = models.DecimalField(decimal_places=4, max_digits=20)
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    receipt = models.ForeignKey(Receipt, related_name='cartitems', on_delete=models.PROTECT)
    loyalty = models.ForeignKey(Loyalty, null=True, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    date = models.DateTimeField()
    dt = models.DateField()  # filled automatically from `date` field
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    original_price = models.DecimalField(decimal_places=4, max_digits=12, default=0)
    order_no = models.CharField(max_length=50)
    week_day = models.IntegerField()
    hour = models.IntegerField()
    margin_price_total = models.DecimalField(decimal_places=4, max_digits=20, default=0)

    # objects = CartItemManager.from_queryset(CartItemQuerySet)()

    class Meta:
        unique_together = (('client', 'receipt', 'order_no'),)
        index_together = [['client'], ['client', 'dt'], ['client', 'receipt'],
                          ['client', 'shop', 'receipt'], ['client', 'dt'],
                          ['receipt']]

    def __unicode__(self):
        return '%s, qty=%s price =%s' % (self.product.name, self.qty, self.price)


class PredictPlan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    dt = models.DateField()
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    receipts_qty = models.IntegerField()
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    turnover_rate = models.DecimalField(decimal_places=4, max_digits=20, null=True)

    class  Meta:
        unique_together = (("client", "shop", "category", "dt"))
        index_together = [["client", "dt"], ["client", "shop", "dt"]]
