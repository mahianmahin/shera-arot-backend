from django.contrib import admin

from api.models import *


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_number']

@admin.register(Customers)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'date', 'previous_order', 'next_order']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_product', 'amount', 'price', 'customer_name', 'customer_phone', 'delivery_date', 'delivered', 'cancelled', 'delivered_date']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'date']

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'date']

@admin.register(AccountsUtility)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ['id', 'type']

@admin.register(Remarks)
class RemarksAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_time', 'detail', 'related_product']