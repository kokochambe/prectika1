from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('dashboard/', views.sales_dashboard, name='dashboard'),
    path('create/', views.create_sale, name='create_sale'),
    path('export/sales/', views.export_sales_csv, name='export_sales'),
]
