from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('login/', views.AdminLoginView.as_view(), name='login'),

    path('logout/', views.admin_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/status/', views.order_update_status, name='order_update_status'),
    path('customers/', views.customer_list, name='customer_list'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('reports/', views.reports, name='reports'),
    path('subscribers/', views.subscriber_list, name='subscriber_list'),
]
