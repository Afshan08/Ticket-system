from django.urls import path
from . import views

urlpatterns = [
    # Area
    path('areas/', views.area_list, name='area_list'),
    path('areas/create/', views.area_create, name='area_create'),
    path('areas/<int:pk>/update/', views.area_update, name='area_update'),

    # Customer
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),

    # Item Category
    path('categories/', views.item_category_list, name='item_category_list'),
    path('categories/create/', views.item_category_create, name='item_category_create'),
    path('categories/<int:pk>/update/', views.item_category_update, name='item_category_update'),

    # Item
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/update/', views.item_update, name='item_update'),

    # Machine
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/create/', views.machine_create, name='machine_create'),
    path('machines/<int:pk>/update/', views.machine_update, name='machine_update'),

    # Operator
    path('operators/', views.operator_list, name='operator_list'),
    path('operators/create/', views.operator_create, name='operator_create'),
    path('operators/<int:pk>/update/', views.operator_update, name='operator_update'),
]
