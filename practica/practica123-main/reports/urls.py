from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('export/equipment/', views.export_equipment_csv, name='export_equipment'),
    path('export/parts/', views.export_parts_csv, name='export_parts'),
    path('export/workorders/', views.export_workorders_csv, name='export_workorders'),
]
