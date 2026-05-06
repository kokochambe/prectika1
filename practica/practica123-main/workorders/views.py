from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import TaskNotification, WorkOrder
from accounts.models import User
from equipment.models import Equipment
from .forms import AssignTaskForm, CreateWorkOrderForm


@login_required
def create_work_order(request):
    """Создание наряда-заказа (для клиента)"""
    if request.method == 'POST':
        form = CreateWorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.created_by = request.user
            work_order.status = 'new'
            work_order.save()
            
            messages.success(request, f'✅ Заявка #{work_order.id} успешно создана!')
            return redirect('accounts:dashboard')
    else:
        form = CreateWorkOrderForm()
    
    return render(request, 'workorders/create.html', {'form': form})


@login_required
def admin_assign_task(request):
    """Администратор назначает задачу технику"""
    if not request.user.is_admin:
        messages.error(request, 'Доступ запрещён')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AssignTaskForm(request.POST)
        if form.is_valid():
            worker = form.cleaned_data['worker']
            message_text = form.cleaned_data['message']
            
            # Создаём наряд-заказ (если нужно) или используем существующий
            # Для простоты создаём новый наряд
            equipment = Equipment.objects.first()  # В реальном проекте нужно выбирать оборудование
            if equipment:
                work_order = WorkOrder.objects.create(
                    equipment=equipment,
                    order_type='emergency',
                    priority=3,
                    status='new',
                    assigned_user=worker,
                    created_by=request.user,
                    description=message_text
                )
                
                # Создаём уведомление
                notification = TaskNotification.objects.create(
                    worker=worker,
                    work_order=work_order,
                    message=message_text,
                    status='pending',
                    created_by=request.user
                )
                
                messages.success(request, f'✅ Задание назначено пользователю {worker.username}')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Нет доступного оборудования для создания задания')
    else:
        form = AssignTaskForm()
    
    technicians = User.objects.filter(role='technician', is_active=True)
    return render(request, 'workorders/admin_assign.html', {'form': form, 'technicians': technicians})


@login_required
def accept_notification(request, notification_id):
    """Принять уведомление в работу"""
    if request.method == 'POST':
        notification = get_object_or_404(TaskNotification, id=notification_id, worker=request.user)
        if notification.status == 'pending':
            notification.status = 'accepted'
            notification.save()
            
            # Обновляем статус наряда
            if notification.work_order.status == 'new':
                notification.work_order.status = 'assigned'
                notification.work_order.save()
            
            messages.success(request, f'✅ Задание принято в работу: {notification.work_order}')
        else:
            messages.warning(request, 'Это задание уже обрабатывается')
    
    return redirect('accounts:dashboard')


@login_required
def start_notification(request, notification_id):
    """Начать выполнение работы"""
    if request.method == 'POST':
        notification = get_object_or_404(TaskNotification, id=notification_id, worker=request.user)
        if notification.status in ['accepted', 'in_progress']:
            notification.status = 'in_progress'
            notification.save()
            
            # Обновляем статус наряда
            if notification.work_order.status in ['new', 'assigned']:
                notification.work_order.status = 'in_progress'
                notification.work_order.started_at = timezone.now()
                notification.work_order.save()
            
            messages.success(request, f'🔧 Работа началась: {notification.work_order}')
        else:
            messages.warning(request, 'Невозможно начать это задание')
    
    return redirect('accounts:dashboard')


@login_required
def complete_notification(request, notification_id):
    """Завершить работу"""
    if request.method == 'POST':
        notification = get_object_or_404(TaskNotification, id=notification_id, worker=request.user)
        if notification.status == 'in_progress':
            notification.status = 'done'
            notification.save()
            
            # Обновляем статус наряда
            notification.work_order.status = 'completed'
            notification.work_order.completed_at = timezone.now()
            notification.work_order.save()
            
            messages.success(request, f'✅ Работа завершена: {notification.work_order}')
        else:
            messages.warning(request, 'Сначала необходимо начать работу')
    
    return redirect('accounts:dashboard')
