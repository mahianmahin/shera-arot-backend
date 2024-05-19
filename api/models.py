from django.contrib.auth.models import User
from django.db import models


class AccountsUtility(models.Model):
    type = models.CharField(max_length=200, null=True, blank=True)

class CustomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):
        return self.user.username
    
class Customers(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True, unique=True)
    address = models.TextField()
    date = models.DateField(auto_now=True)
    previous_order = models.CharField(max_length=100, null=True, blank=True, default="-")
    next_order = models.CharField(max_length=100, null=True, blank=True, default="-")

    def __str__(self):
        return self.phone

class Inventory(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=20, null=True, blank=True)

class Order(models.Model):
    order_product = models.CharField(max_length=200, null=True, blank=True)
    order_product_id = models.IntegerField()
    amount = models.CharField(max_length=50, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_phone = models.CharField(max_length=100, null=True, blank=True)
    customer_address = models.TextField()
    delivery_date = models.CharField(max_length=50, null=True, blank=True)
    order_placed = models.DateTimeField(auto_now=True)
    delivered = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    delivered_date = models.CharField(max_length=100, null=True, blank=True)

class Expense(models.Model):
    date = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    amount = models.CharField(max_length=200, null=True, blank=True)

class Income(models.Model):
    date = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    amount = models.CharField(max_length=50, null=True, blank=True)

class Remarks(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now=True)
    detail = models.TextField()
    related_product = models.CharField(max_length=200, null=True, blank=True)
