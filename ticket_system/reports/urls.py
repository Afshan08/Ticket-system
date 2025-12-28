from django.urls import path
from . import views

urlpatterns = [
    path('production/', views.production_report_view, name='production_report'),
    path('dashboard/', views.production_dashboard_view, name='production_dashboard'),
    path('progress/', views.job_progress_view, name='job_progress_report'),
    path('pending/', views.pending_orders_view, name='pending_orders_report'),
    path('job/<str:job_no>/', views.job_detail_view, name='job_order_report'),
    path('process/<str:process_type>/', views.process_output_view, name='process_output_report'),
]