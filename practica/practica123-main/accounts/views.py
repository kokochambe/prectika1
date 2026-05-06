from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User
from .forms import RegistrationForm


def home_view(request):
    """Главная страница системы"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'core/home.html')


def quick_login_view(request, role):
    """Быстрый вход без пароля для демонстрации"""
    # Маппинг ролей на тестовых пользователей с новыми логинами
    role_user_map = {
        'admin': 'admin_otir',
        'engineer': 'eng_ivanov',
        'technician': 'tech_sidorov',
        'storekeeper': 'store_morozov',
        'trainee': 'trainee_smirnov',
        'seller': 'seller_petrov',
    }
    
    username = role_user_map.get(role)
    if not username:
        messages.error(request, 'Неверная роль')
        return redirect('accounts:home')
    
    try:
        user = User.objects.get(username=username)
        if user.is_active:
            login(request, user)
            messages.success(request, f'⚡ Быстрый вход как {user.username} ({user.get_role_display()})')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Пользователь не активен')
    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден. Создайте тестовые данные.')
    
    return redirect('accounts:home')


def login_view(request):
    """Представление входа в систему"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    """Представление регистрации нового пользователя"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f'Регистрация успешна! Теперь вы можете войти как {user.username}')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Представление выхода из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('accounts:home')


@login_required
def dashboard_view(request):
    """Главная панель в зависимости от роли пользователя"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    # Получаем статистику в зависимости от роли
    if user.is_admin:
        from equipment.models import Equipment
        from workorders.models import WorkOrder
        from inventory.models import SparePart
        from django.db.models import F, Count, Q, Avg
        from datetime import timedelta
        
        context['total_equipment'] = Equipment.objects.count()
        context['active_equipment'] = Equipment.objects.filter(status='active').count()
        context['total_orders'] = WorkOrder.objects.count()
        context['new_orders'] = WorkOrder.objects.filter(status='new').count()
        context['in_progress_orders'] = WorkOrder.objects.filter(status='in_progress').count()
        context['completed_orders'] = WorkOrder.objects.filter(status='completed').count()
        context['total_parts'] = SparePart.objects.count()
        context['low_stock_parts'] = SparePart.objects.filter(current_stock__lte=F('min_stock')).count()
        context['recent_orders'] = WorkOrder.objects.select_related('equipment', 'assigned_user').order_by('-created_at')[:10]
        context['users_by_role'] = User.objects.values('role').annotate(count=Count('id'))
        
        # Расчет дополнительных метрик для аналитики
        total_completed = WorkOrder.objects.filter(status='completed').count()
        total_all = WorkOrder.objects.count()
        if total_all > 0:
            context['efficiency_rate'] = round((total_completed / total_all) * 100)
        else:
            context['efficiency_rate'] = 0
            
        # Среднее время выполнения (в часах)
        completed_with_time = WorkOrder.objects.filter(
            status='completed',
            started_at__isnull=False,
            completed_at__isnull=False
        )
        if completed_with_time.exists():
            avg_time = 0
            count = 0
            for order in completed_with_time:
                if order.started_at and order.completed_at:
                    delta = order.completed_at - order.started_at
                    avg_time += delta.total_seconds() / 3600
                    count += 1
            if count > 0:
                context['avg_completion_time'] = round(avg_time / count, 1)
            else:
                context['avg_completion_time'] = 0
        else:
            context['avg_completion_time'] = 0
            
        # Загрузка персонала (отношение активных нарядов к количеству техников)
        technicians_count = User.objects.filter(role='technician').count()
        active_orders = WorkOrder.objects.filter(status__in=['new', 'assigned', 'in_progress']).count()
        if technicians_count > 0:
            context['workload_percent'] = min(round((active_orders / technicians_count) * 25), 100)
        else:
            context['workload_percent'] = 0
            
        # Готовность оборудования
        if Equipment.objects.count() > 0:
            context['equipment_uptime'] = round((Equipment.objects.filter(status='active').count() / Equipment.objects.count()) * 100)
        else:
            context['equipment_uptime'] = 0
            
        template = 'dashboards/admin.html'
        
    elif user.is_engineer:
        from equipment.models import Equipment
        from workorders.models import WorkOrder, TaskNotification
        
        context['equipment_count'] = Equipment.objects.filter(workshop=user.department).count() if user.department else Equipment.objects.count()
        context['planned_orders'] = WorkOrder.objects.filter(order_type='planned', status__in=['new', 'assigned']).count()
        context['emergency_orders'] = WorkOrder.objects.filter(order_type='emergency', status__in=['new', 'assigned', 'in_progress']).count()
        context['all_equipment'] = Equipment.objects.all()[:20]
        context['pending_orders'] = WorkOrder.objects.filter(status__in=['new', 'assigned']).select_related('equipment')[:10]
        
        # Обработка POST запросов для инженера
        if request.method == 'POST':
            if 'create_order' in request.POST:
                # Создание нового наряда
                eq_id = request.POST.get('equipment')
                w_type = request.POST.get('work_type')
                desc = request.POST.get('description')
                priority = request.POST.get('priority', 'medium')
                
                if eq_id and w_type:
                    equipment = Equipment.objects.get(id=eq_id)
                    order = WorkOrder.objects.create(
                        equipment=equipment,
                        order_type=w_type,
                        description=desc,
                        priority=priority,
                        status='new',
                        created_by=user
                    )
                    messages.success(request, f'Наряд-заказ #{order.id} успешно создан!')
                    return redirect('accounts:dashboard')
            
            elif 'update_status' in request.POST:
                # Обновление статуса наряда
                order_id = request.POST.get('order_id')
                new_status = request.POST.get('status')
                assignee_id = request.POST.get('assignee')
                
                if order_id:
                    order = WorkOrder.objects.get(id=order_id)
                    old_status = order.status
                    order.status = new_status
                    
                    if assignee_id and assignee_id != '':
                        old_assignee = order.assigned_user
                        order.assigned_user_id = assignee_id
                        
                        # Если назначен новый техник, создаем уведомление
                        if order.assigned_user and order.assigned_user != old_assignee:
                            TaskNotification.objects.create(
                                worker=order.assigned_user,
                                work_order=order,
                                message=f"Вам назначен новый наряд-заказ #{order.id} на {order.equipment.name}. Тип: {order.get_order_type_display()}",
                                status='pending'
                            )
                            messages.success(request, f'Наряд #{order.id} назначен технику {order.assigned_user.username}')
                    
                    order.save()
                    messages.success(request, f'Статус наряда #{order.id} обновлен на "{order.get_status_display()}".')
                    return redirect('accounts:dashboard')
        
        # Данные для форм инженера
        context['create_form_equipment'] = Equipment.objects.all()
        context['technicians'] = User.objects.filter(role='technician')
        
        template = 'dashboards/engineer.html'
        
    elif user.role == 'technician':
        from workorders.models import WorkOrder, TaskNotification
        
        # Мои наряды с разными статусами для отображения workflow
        context['my_orders'] = WorkOrder.objects.filter(assigned_user=user).exclude(status='completed').select_related('equipment')
        context['completed_orders'] = WorkOrder.objects.filter(assigned_user=user, status='completed').count()
        context['all_my_orders'] = WorkOrder.objects.filter(assigned_user=user).select_related('equipment').order_by('-created_at')[:15]
        
        # Новые уведомления от админа
        context['pending_notifications'] = TaskNotification.objects.filter(worker=user, status='pending').select_related('work_order', 'created_by')[:10]
        context['active_notifications'] = TaskNotification.objects.filter(worker=user, status__in=['accepted', 'in_progress']).select_related('work_order', 'created_by')[:10]
        
        # Статистика по статусам нарядов
        context['new_orders_count'] = WorkOrder.objects.filter(assigned_user=user, status='new').count()
        context['in_progress_count'] = WorkOrder.objects.filter(assigned_user=user, status='in_progress').count()
        context['pending_parts_count'] = WorkOrder.objects.filter(assigned_user=user, status='pending_parts').count()
        
        template = 'dashboards/technician.html'
        
    elif user.role == 'storekeeper':
        from inventory.models import SparePart, PartRequest
        from django.db.models import F
        
        context['low_stock_parts'] = SparePart.objects.filter(current_stock__lte=F('min_stock'))
        context['pending_requests'] = PartRequest.objects.filter(status='requested').select_related('spare_part', 'requested_by')[:10]
        context['all_parts'] = SparePart.objects.all()[:20]
        context['recent_requests'] = PartRequest.objects.select_related('spare_part', 'requested_by').order_by('-id')[:10]
        template = 'dashboards/storekeeper.html'
        
    elif user.role == 'trainee':
        from equipment.models import Equipment
        from workorders.models import WorkOrder
        
        context['recent_orders'] = WorkOrder.objects.filter(status='completed').select_related('equipment', 'assigned_user')[:15]
        context['equipment_list'] = Equipment.objects.all()[:20]
        template = 'dashboards/trainee.html'
        
    elif user.role == 'seller':
        from sales.models import Sale
        
        # Перенаправляем продавца на панель продаж
        return redirect('sales:dashboard')
    
    elif user.role == 'client':
        from equipment.models import Equipment
        from workorders.models import WorkOrder
        
        # Панель клиента: просмотр оборудования и история заявок
        context['equipment_list'] = Equipment.objects.filter(status='active')[:20]
        context['my_requests'] = WorkOrder.objects.filter(created_by=user).order_by('-created_at')[:15] if user.is_authenticated else []
        context['active_requests_count'] = WorkOrder.objects.filter(created_by=user, status__in=['new', 'assigned', 'in_progress']).count() if user.is_authenticated else 0
        context['completed_requests_count'] = WorkOrder.objects.filter(created_by=user, status='completed').count() if user.is_authenticated else 0
        
        template = 'dashboards/client.html'
    else:
        template = 'dashboards/admin.html'
    
    return render(request, template, context)
