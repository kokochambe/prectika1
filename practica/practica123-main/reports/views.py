from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from equipment.models import Equipment
from inventory.models import SparePart
from workorders.models import WorkOrder
import csv


@login_required
def export_equipment_csv(request):
    """Экспорт оборудования в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="equipment.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Инв. номер', 'Наименование', 'Тип', 'Цех', 'Статус', 'Дата установки', 'Гарантия до'])
    
    for eq in Equipment.objects.all():
        writer.writerow([
            eq.inv_number,
            eq.name,
            eq.type,
            eq.workshop,
            eq.get_status_display(),
            eq.install_date,
            eq.warranty_until
        ])
    
    return response


@login_required
def export_parts_csv(request):
    """Экспорт запчастей в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="spare_parts.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Артикул', 'Наименование', 'Категория', 'На складе', 'Мин. запас', 'Ед. изм.', 'Цена'])
    
    for part in SparePart.objects.all():
        writer.writerow([
            part.part_number,
            part.name,
            part.category,
            part.current_stock,
            part.min_stock,
            part.unit,
            part.price
        ])
    
    return response


@login_required
def export_workorders_csv(request):
    """Экспорт нарядов-заданий в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="work_orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Оборудование', 'Тип', 'Приоритет', 'Статус', 'Исполнитель', 'Описание', 'Создан'])
    
    for order in WorkOrder.objects.select_related('equipment', 'assigned_user').all():
        writer.writerow([
            order.id,
            order.equipment.inv_number if order.equipment else '',
            order.get_order_type_display(),
            order.priority,
            order.get_status_display(),
            order.assigned_user.username if order.assigned_user else '',
            order.description,
            order.created_at
        ])
    
    return response
