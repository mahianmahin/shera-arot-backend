from datetime import date, datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import *


class CustomerModelViewSet(viewsets.ModelViewSet):
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class InventoryModelViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

class OrderModelViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        today_date = timezone.now().date()

        delivered_orders = Order.objects.filter(delivered=True, cancelled=False)
        not_delivered_orders = Order.objects.filter(delivered=False, cancelled=False)
        missed_delivery_orders = Order.objects.filter(delivery_date__lt=today_date, delivered=False, cancelled=False)
        cancelled_orders = Order.objects.filter(cancelled=True)

        delivered_orders_data = OrderSerializer(delivered_orders, many=True).data
        not_delivered_orders_data = OrderSerializer(not_delivered_orders, many=True).data
        missed_delivery_orders_data = OrderSerializer(missed_delivery_orders, many=True).data
        cancelled_orders_data = OrderSerializer(cancelled_orders, many=True).data

        response_data = {
            'delivered_orders': delivered_orders_data,
            'not_delivered_orders': not_delivered_orders_data,
            'missed_delivery_orders': missed_delivery_orders_data,
            'cancelled_orders': cancelled_orders_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class OrderModelViewSetCRUD(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shipments(request):
    today_date = date.today()

    orders_today = Order.objects.filter(delivery_date=today_date, delivered=False, cancelled=False)
    serializer = OrderSerializer(orders_today, many=True)

    return Response({
        'status': status.HTTP_200_OK,
        'data': serializer.data,
    }) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_order(request, id):
    order_ins = Order.objects.get(id=id)
    order_ins.cancelled = True

    ordered_product = Inventory.objects.get(id=int(order_ins.order_product_id))
    ordered_product.amount = str(int(ordered_product.amount) + int(order_ins.amount))

    customer_ins = Customers.objects.get(phone=order_ins.customer_phone)
    customer_ins.next_order = "-"

    ordered_product.save()
    order_ins.save()
    customer_ins.save()


    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Order cancelled successfully!'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def done_order(request, id):
    today_date = date.today()

    order_ins = Order.objects.get(id=id)
    order_ins.delivered = True
    order_ins.delivered_date = today_date

    ordered_product = Inventory.objects.get(id=int(order_ins.order_product_id))

    customer_ins = Customers.objects.get(phone=order_ins.customer_phone)
    customer_ins.next_order = "-"
    customer_ins.previous_order = today_date

    ordered_product.save()
    order_ins.save()
    customer_ins.save()


    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Order done successfully!'
    })


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def place_order(request):
    if request.method == 'POST':
        ordered_product = Inventory.objects.get(id=int(request.data.get('order_product')))
        ordered_product.amount = str(int(ordered_product.amount) - int(request.data.get('amount')))
        ordered_product.save()

        ordered_customer = Customers.objects.get(id=request.data.get('customer_id'))
        ordered_customer.next_order = request.data.get('delivery_date')
        ordered_customer.save()

        order_ins = Order(
            order_product = ordered_product.name,
            order_product_id = ordered_product.id,
            amount = request.data.get('amount'),
            price = str(int(ordered_product.price) * int(request.data.get('amount'))),
            customer_name = request.data.get('customer_name'),
            customer_phone = request.data.get('customer_phone'),
            customer_address = request.data.get('customer_address'),
            delivery_date = request.data.get('delivery_date'),
        )

        order_ins.save()

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Order Placed Successfully'
        })

@api_view(['GET'])
def login_with_phone_number(request, phone_number, password):
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            if user:
                username = user.user.username
                user_auth = authenticate(username=username, password=password)
                if user_auth:
                    refresh = RefreshToken.for_user(user_auth)
                    is_admin = user.user.is_superuser
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'admin': is_admin,
                        'success': True
                    })
                else:
                    return Response({
                        'message': 'Invalid credentials!',
                        'success': False
                    })
            else:
                return Response({
                    'message': 'User not found',
                    'success': False
                })
        except:
            return Response({
                'message': 'User not found!',
                'success': False
            })

@api_view(['POST'])
def get_sales(request):
    if request.user.is_superuser:
        first_day_of_month = request.data.get('first_date')
        last_day_of_month = request.data.get('last_date')
        
        orders = Order.objects.filter(delivered=True, delivered_date__gte=first_day_of_month, delivered_date__lte=last_day_of_month, cancelled=False)
        
        order_serializer = OrderSerializer(orders, many=True)

        total_price = sum(int(item.price) for item in orders)

        return Response({
            'success': True,
            'data': order_serializer.data,
            'total_price': total_price
        })
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to see this page!'
        })

def month_in_words(start_date, end_date):
    # Parse the input dates
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    # Extract month and year
    month = start_datetime.strftime('%B')
    year = start_datetime.strftime('%Y')

    # Check if the month is the same for both dates
    if start_datetime.month == end_datetime.month:
        return f"For the month of {month} {year}"
    else:
        return f"For the period from {start_datetime.strftime('%B')} {year} to {end_datetime.strftime('%B')} {year}"        

@api_view(['POST'])
def income_statement(request):
    if request.user.is_superuser:
        first_day_of_month = request.data.get('first_date')
        last_day_of_month = request.data.get('last_date')

        sales = Order.objects.filter(delivered=True, delivered_date__gte=first_day_of_month, delivered_date__lte=last_day_of_month, cancelled=False)
        sales_serializer = OrderSerializer(sales, many=True)
        total_sales = sum(int(item.price) for item in sales)

        expenses = Expense.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month)
        exp_serializer = ExpenseSerializer(expenses, many=True)
        total_expense_amount = sum(int(item.amount) for item in expenses)

        incomes = Income.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month)
        inc_serializer = IncomeSerializer(incomes, many=True)
        total_income_amount = sum(int(item.amount) for item in incomes)

        marged_income = sales_serializer.data + inc_serializer.data

        total_expense = sum(int(item.amount) for item in expenses)
        total_income = sum(int(item.amount) for item in incomes) + sum(int(item.price) for item in sales)
        balance = total_income - total_expense

        statement_date = ''

        try:
            statement_date = month_in_words(first_day_of_month, last_day_of_month)
        except:
            pass

        return Response({
            'success': True,
            'sales': total_sales,
            'income': inc_serializer.data,
            'income_amount': total_income_amount,
            'expense': exp_serializer.data,
            'expense_amoumt': total_expense_amount,
            'balance': balance,
            'statement_date': statement_date
        })

    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to see this page!'
        })

@api_view(['POST'])
def accounts(request):
    if request.user.is_superuser:
        first_day_of_month = request.data.get('first_date')
        last_day_of_month = request.data.get('last_date')
        
        sales = Order.objects.filter(delivered=True, delivered_date__gte=first_day_of_month, delivered_date__lte=last_day_of_month, cancelled=False)
        sales_serializer = OrderSerializer(sales, many=True)

        expenses = Expense.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month)
        exp_serializer = ExpenseSerializer(expenses, many=True)

        incomes = Income.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month)
        inc_serializer = IncomeSerializer(incomes, many=True)

        marged_income = sales_serializer.data + inc_serializer.data

        total_expense = sum(int(item.amount) for item in expenses)
        total_income = sum(int(item.amount) for item in incomes) + sum(int(item.price) for item in sales)
        balance = total_income - total_expense

        return Response({
            'success': True,
            'expenses': exp_serializer.data,
            'income': marged_income,
            'total_expense': total_expense,
            'total_income': total_income,
            'balance': balance
        })
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to see this page!'
        })

@api_view(['POST'])
def save_income(request):
    if request.user.is_superuser:
        income_ins = Income(
            name=request.data.get('name'),
            amount=request.data.get('amount'),
            date=request.data.get('date')
        )

        income_ins.save()

        return Response({
            'success': True,
            'message': 'Data saved successfully!'
        })
    
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to perform this opration!'
        })

@api_view(['GET'])
def delete_income(request, id):
    if request.user.is_superuser:
        income_ins = Income.objects.get(id=id)
        income_ins.delete()

        return Response({
            'success': True,
            'message': 'Income deleted successfully!'
        })
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to perform this opration!'
        })

@api_view(['POST'])
def save_expense(request):
    if request.user.is_superuser:
        expense_ins = Expense(
            name=request.data.get('name'),
            amount=request.data.get('amount'),
            date=request.data.get('date')
        )

        expense_ins.save()

        return Response({
            'success': True,
            'message': 'Data saved successfully!'
        })
    
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to perform this opration!'
        })
    
@api_view(['GET'])
def delete_expense(request, id):
    if request.user.is_superuser:
        expense_ins = Expense.objects.get(id=id)
        expense_ins.delete()

        return Response({
            'success': True,
            'message': 'Expense deleted successfully!'
        })
    else:
        return Response({
            'success': False,
            'message': 'You are not authorized to perform this opration!'
        })

class RemarksViewSet(viewsets.ModelViewSet):
    queryset = Remarks.objects.all()
    serializer_class = RemarksSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]