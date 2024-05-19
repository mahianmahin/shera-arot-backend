from rest_framework import serializers

from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = "__all__"

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields= "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = "__all__"

class RemarksSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customers.objects.all(),
        source='customer',
        write_only=True
    )

    customer = CustomerSerializer(read_only=True)
    date_time = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)

    class Meta:
        model = Remarks
        fields = "__all__"
        read_only_fields = ["id", "date_time"]