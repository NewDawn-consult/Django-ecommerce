from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_pk>/', views.order_confirmation, name='order_confirmation'),
    path('detail/<int:order_pk>/', views.order_detail, name='order_detail'),
    path('invoice/<int:order_pk>/', views.order_invoice, name='order_invoice'),
    path('', views.order_list, name='order_list'),
]
