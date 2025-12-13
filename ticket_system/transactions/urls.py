from django.urls import path
from . import views

urlpatterns = [
    # Sales Order
    path('sales-orders/', views.sales_order_list, name='sales_order_list'),
    path('sales-orders/create/', views.sales_order_create, name='sales_order_create'),
    path('sales-orders/<int:pk>/update/', views.sales_order_update, name='sales_order_update'),

    # Job Order
    path('job-orders/', views.job_order_list, name='job_order_list'),
    path('job-orders/create/', views.job_order_create, name='job_order_create'),
    
    # Production Transactions
    path('printing/', views.printing_transaction_list, name='printingtransaction_list'),
    path('printing/create/', views.printing_transaction_create, name='printing_transaction_create'),
    path('rewinding/', views.rewinding_transaction_list, name='rewindingtransaction_list'),
    path('rewinding/create/', views.rewinding_transaction_create, name='rewinding_transaction_create'),
    path('slitting/', views.slitting_transaction_list, name='slittingtransaction_list'),
    path('slitting/create/', views.slitting_transaction_create, name='slitting_transaction_create'),
    path('lamination/', views.lamination_transaction_list, name='laminationtransaction_list'),
    path('lamination/create/', views.lamination_transaction_create, name='lamination_transaction_create'),
    path('core/', views.core_transaction_list, name='coretransaction_list'),
    path('core/create/', views.core_transaction_create, name='core_transaction_create'),
    
    # Lookup API Endpoints (JSON)
    path('api/lookup/job-orders/', views.job_order_lookup, name='job_order_lookup'),
    path('api/lookup/customers/', views.customer_lookup, name='customer_lookup'),
    path('api/lookup/machines/', views.machine_lookup, name='machine_lookup'),
    path('api/lookup/operators/', views.operator_lookup, name='operator_lookup'),
]
