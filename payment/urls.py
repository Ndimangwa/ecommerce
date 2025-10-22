from django.urls import path
from . import views

app_name='payment'

urlpatterns = [
    path('payment_success/', views.payment_success, name='payment_success'),
    path('checkout/', views.checkout, name='checkout'),
    path('billing_info/', views.billing_info, name='billing_info'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('shipped_dash/', views.shipped_dash, name='shipped_dash'),
    path('not_shipped_dash/', views.not_shipped_dash, name='not_shipped_dash'),
    path('orders/<int:pk>/', views.orders, name='orders'),
    path('update_shipping_status/', views.update_shipping_status, name='update_shipping_status'),
]
