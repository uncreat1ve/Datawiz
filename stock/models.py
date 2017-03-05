from __future__ import unicode_literals
# Create your models here.
from django.db import models
from core.models import Client
from core.models import *
# from api1.models import Product, Shop, Loyalty, Cashier
# Create your models here.
# from managers import Product_InventorymManager
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
# from stock.managers import SupplierCacheManager, PurchaseCacheManager, ReceiveCacheManager, RelocateCacheManager


class Supplier(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=100)
    supplier_code = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    commodity_credit_days = models.IntegerField(default=0, blank=True)
    address = models.TextField(null=True, blank=True)
    # cache = SupplierCacheManager()

    class Meta:
        unique_together = ('client', 'name', 'identifier', 'supplier_code')
        index_together = [['client', 'identifier']]

    def __unicode__(self):
        return '%s, name=%s' % (self.id, self.name)


class Purchase_Product_doc(models.Model):
    identifier = models.CharField(max_length=200)
    doc_number = models.CharField(max_length=200, blank=True, default='')
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)

    items_qty = models.DecimalField(decimal_places=4, max_digits=20)
    receive_date = models.DateField(null=True)
    responsible = models.CharField(max_length=200, blank=True)
    order_date = models.DateTimeField()
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    commodity_credit_days = models.IntegerField(default=0, blank=True)
    # cache = PurchaseCacheManager()
    class Meta:
        unique_together = ('client', 'order_date', 'shop', 'doc_number', 'identifier')

    def __unicode__(self):
        return '%s,responsible= %s qty_products= %s' % (
            self.id, self.responsible, self.qty)


class Purchase_doc_Attached_Product(models.Model):
    document = models.ForeignKey(Purchase_Product_doc, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    qty = models.DecimalField(decimal_places=4, max_digits=15)
    price = models.DecimalField(decimal_places=4, max_digits=15)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)


class Receive_Product_doc(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    identifier = models.CharField(max_length=200)
    doc_number = models.CharField(max_length=100, blank=True, default='')
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    doc_order = models.ForeignKey(Purchase_Product_doc, null=True, on_delete=models.PROTECT)
    date_doc = models.DateTimeField()
    responsible = models.CharField(max_length=200)
    items_qty = models.DecimalField(decimal_places=4, max_digits=20)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)

    # cache = ReceiveCacheManager()
    class Meta:
        unique_together = ('client', 'doc_number', 'shop', 'identifier')

    def __unicode__(self):
        return '%s,responsible= %s qty= %s' % (
            self.id, self.responsible, self.qty)


class Receive_doc_Attached_Product(models.Model):
    document = models.ForeignKey(Receive_Product_doc, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    qty = models.DecimalField(decimal_places=4, max_digits=15)
    price = models.DecimalField(decimal_places=4, max_digits=15)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)


class Relocate_Product_doc(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    identifier = models.CharField(max_length=200)
    date = models.DateTimeField()
    shop_sender = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name='sender_relocate_docs',
                                    null=True, blank=True)
    shop_receiver = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name='receiver_relocate_docs',
                                      null=True, blank=True)
    responsible = models.CharField(max_length=200)
    total_price = models.DecimalField(decimal_places=4, max_digits=20, null=True)

    # cache = RelocateCacheManager()
    class Meta:
        unique_together = (
            'client', 'date', 'identifier', 'shop_sender', 'shop_receiver')

    def __unicode__(self):
        return '%s, product= %s shop_sender= %s shop_receiver= %s' % (
            self.id, self.product, self.shop_sender, self.shop_receiver)


class Relocate_doc_Attached_Product(models.Model):
    document = models.ForeignKey(Relocate_Product_doc, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    qty = models.DecimalField(decimal_places=4, max_digits=15)
    price = models.DecimalField(decimal_places=4, max_digits=15, null=True)
    total_price = models.DecimalField(decimal_places=4, max_digits=20, null=True)


class RefundReceipt(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=200, blank=True)
    identifier = models.CharField(max_length=200)
    date = models.DateTimeField()
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name='refunds')
    loyalty = models.ForeignKey(Loyalty, null=True, on_delete=models.PROTECT, related_name='refunds')
    cashier = models.ForeignKey(Cashier, null=True, on_delete=models.PROTECT, related_name='refunds')
    total_price = models.DecimalField(decimal_places=4, max_digits=20)
    items_qty = models.DecimalField(decimal_places=4, max_digits=20)
    closed = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'client', 'date', 'order_id', 'shop'
        )

    def __unicode__(self):
        return '%s, shop= %s' % (self.id, self.shop)


class RefundReceiptProduct(models.Model):
    refund_receipt = models.ForeignKey(RefundReceipt, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    qty = models.DecimalField(decimal_places=4, max_digits=15)
    price = models.DecimalField(decimal_places=4, max_digits=15)
    discount = models.DecimalField(decimal_places=4, max_digits=15, default=0)
    total_price = models.DecimalField(decimal_places=4, max_digits=20)


class Product_Inventory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    dt = models.DateField()
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    week_day = models.IntegerField()
    qty = models.DecimalField(decimal_places=4, max_digits=20)
    original_price = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    stock_total_price = models.DecimalField(decimal_places=4, max_digits=20, default=0)
    # objects = Product_InventorymManager()

    class Meta:
        unique_together = ('client', 'dt', 'shop', 'product')
        index_together = ['client', 'shop', 'dt']

    def __unicode__(self):
        return '%s, shop= %s, product= %s' % (self.id, self.shop, self.product)


class Supplier_products_shop(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('client', 'supplier', 'shop', 'product')
        index_together = [['client', 'shop', 'product']]


#----------Receive_Product_doc----------------
@receiver(post_delete, sender=Receive_Product_doc)
def delete_brands_cache(sender, instance, **kwargs):
    sender.cache.delete(instance)

@receiver(post_save, sender=Receive_Product_doc)
def update_brands_cache(sender, instance, **kwargs):
    sender.cache.update(instance)

#----------Purchase_Product_doc----------------
@receiver(post_delete, sender=Purchase_Product_doc)
def delete_brands_cache(sender, instance, **kwargs):
    sender.cache.delete(instance)

@receiver(post_save, sender=Purchase_Product_doc)
def update_brands_cache(sender, instance, **kwargs):
    sender.cache.update(instance)

#----------Supplier----------------
@receiver(post_delete, sender=Supplier)
def delete_brands_cache(sender, instance, **kwargs):
    sender.cache.delete(instance)

@receiver(post_save, sender=Supplier)
def update_brands_cache(sender, instance, **kwargs):
    sender.cache.update(instance)

#----------Relocate_Product_doc----------------
@receiver(post_delete, sender=Relocate_Product_doc)
def delete_brands_cache(sender, instance, **kwargs):
    sender.cache.delete(instance)

@receiver(post_save, sender=Relocate_Product_doc)
def update_brands_cache(sender, instance, **kwargs):
    sender.cache.update(instance)

