from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Sale
from equipment.models import Equipment
from inventory.models import SparePart
from accounts.models import User
import csv
from django.http import HttpResponse


@login_required
def sales_dashboard(request):
    """Панель продаж для продавца"""
    if not request.user.is_seller:
        messages.error(request, 'Доступно только для продавцов')
        return redirect('accounts:dashboard')
    
    # Статистика
    total_sales = Sale.objects.filter(seller=request.user).count()
    total_revenue = Sale.objects.filter(seller=request.user).aggregate(total=Sum('total_amount'))['total'] or 0
    today_sales = Sale.objects.filter(seller=request.user, created_at__date__gte=timezone.now().date()).count()
    
    # Последние продажи
    recent_sales = Sale.objects.filter(seller=request.user).select_related(
        'equipment', 'spare_part'
    ).order_by('-created_at')[:20]
    
    # Топ товаров
    top_equipment = Equipment.objects.filter(status='active')[:10]
    top_parts = SparePart.objects.filter(current_stock__gt=0).order_by('-current_stock')[:10]
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'today_sales': today_sales,
        'recent_sales': recent_sales,
        'top_equipment': top_equipment,
        'top_parts': top_parts,
    }
    
    return render(request, 'sales/dashboard.html', context)


@login_required
def create_sale(request):
    """Создание новой продажи"""
    if not request.user.is_seller:
        messages.error(request, 'Доступно только для продавцов')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        sale_type = request.POST.get('sale_type')
        quantity = int(request.POST.get('quantity', 1))
        price = float(request.POST.get('price'))
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        notes = request.POST.get('notes')
        
        sale = Sale(
            sale_type=sale_type,
            quantity=quantity,
            price=price,
            seller=request.user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            notes=notes,
        )
        
        if sale_type == 'equipment':
            equipment_id = request.POST.get('equipment_id')
            sale.equipment = Equipment.objects.get(id=equipment_id)
        elif sale_type == 'spare_part':
            part_id = request.POST.get('part_id')
            sale.spare_part = SparePart.objects.get(id=part_id)
        elif sale_type == 'service':
            sale.service_name = request.POST.get('service_name')
        
        sale.save()
        messages.success(request, f'Продажа на сумму {sale.total_amount} руб. успешно создана!')
        return redirect('sales:dashboard')
    
    # Получаем доступные товары
    equipment_list = Equipment.objects.filter(status='active')[:50]
    parts_list = SparePart.objects.filter(current_stock__gt=0)[:50]
    
    context = {
        'equipment_list': equipment_list,
        'parts_list': parts_list,
    }
    
    return render(request, 'sales/create_sale.html', context)


@login_required
def export_sales_csv(request):
    """Экспорт продаж в CSV"""
    if not request.user.is_seller:
        messages.error(request, 'Доступно только для продавцов')
        return redirect('accounts:dashboard')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Тип', 'Товар/Услуга', 'Кол-во', 'Цена', 'Сумма', 'Клиент', 'Дата'])
    
    for sale in Sale.objects.filter(seller=request.user).select_related('equipment', 'spare_part'):
        item_name = ''
        if sale.sale_type == 'equipment' and sale.equipment:
            item_name = sale.equipment.name
        elif sale.sale_type == 'spare_part' and sale.spare_part:
            item_name = sale.spare_part.name
        elif sale.sale_type == 'service':
            item_name = sale.service_name
        
        writer.writerow([
            sale.id,
            sale.get_sale_type_display(),
            item_name,
            sale.quantity,
            sale.price,
            sale.total_amount,
            sale.customer_name or '-',
            sale.created_at.strftime('%d.%m.%Y %H:%M')
        ])
    
    return response
