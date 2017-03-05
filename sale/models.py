from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import Client, Product, Category
from django.contrib.auth.models import User
# from managers import SaleManager


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField()
    shops = ArrayField(models.IntegerField(),null=True)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    user = models.ForeignKey(User)

    # objects = SaleManager()

    class Meta:
        unique_together = ('client', 'name', 'user')


class Sale_products(models.Model):
    sale = models.ForeignKey(Sale)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.PROTECT)
    class Meta:
        unique_together = ('sale', 'product')
