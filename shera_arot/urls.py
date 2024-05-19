from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from api.views import *

router = DefaultRouter()

router.register('customers', CustomerModelViewSet, basename='customer')
router.register('inventory', InventoryModelViewSet, basename='inventory')
router.register('orders', OrderModelViewSet, basename='orders')
router.register('orders_crud', OrderModelViewSetCRUD, basename='orders_crud')
router.register('remarks', RemarksViewSet, basename='remarks')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/<str:phone_number>/<str:password>/', login_with_phone_number),
    path('place_order/', place_order),
    path('shipments/', shipments),
    path('sales/', get_sales),
    path('accounts/', accounts),
    path('income_statement/', income_statement),
    path('save_income/', save_income),
    path('delete_income/<int:id>/', delete_income),
    path('save_expense/', save_expense),
    path('delete_expense/<int:id>/', delete_expense),
    path('cancel_order/<int:id>/', cancel_order),
    path('done_order/<int:id>/', done_order),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
