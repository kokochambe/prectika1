from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import TaskNotification, WorkOrder


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
