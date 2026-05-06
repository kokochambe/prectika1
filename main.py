import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q, F, Avg, Case, When, Value as DValue, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
import csv
import io

# ==============================================================================
# КОНФИГУРАЦИЯ НАСТРОЕК (Settings)
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='super-secret-key-for-tor-system-2024',
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db_tor_pro.sqlite3'),
            }
        },
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [os.path.join(BASE_DIR, 'templates')],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        STATIC_URL='/static/',
        STATICFILES_DIRS=[os.path.join(BASE_DIR, 'static')],
        MEDIA_ROOT=os.path.join(BASE_DIR, 'media'),
        MEDIA_URL='/media/',
        LOGIN_URL='/login/',
        LANGUAGE_CODE='ru-ru',
        TIME_ZONE='Europe/Moscow',
        USE_I18N=True,
        USE_TZ=True,
    )

django.setup()

# Создание папок если нет
os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'media'), exist_ok=True)

# ==============================================================================
# МОДЕЛИ ДАННЫХ (Models) - Огромная структура
# ==============================================================================

class Department(models.Model):
    name = models.CharField("Название отдела", max_length=100)
    code = models.CharField("Код отдела", max_length=20, unique=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name = "Отдел"; verbose_name_plural = "Отделы"

class Position(models.Model):
    title = models.CharField("Должность", max_length=100)
    level = models.IntegerField("Уровень доступа", default=1) # 1-практикант, 5-директор
    
    def __str__(self): return self.title
    class Meta: verbose_name = "Должность"; verbose_name_plural = "Должности"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)
    is_trainee = models.BooleanField("Практикант", default=False)
    
    def __str__(self): return f"{self.user.username} ({self.position})"
    class Meta: verbose_name = "Профиль сотрудника"; verbose_name_plural = "Профили сотрудников"

class EquipmentCategory(models.Model):
    name = models.CharField("Категория", max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    def __str__(self): return self.name
    class Meta: verbose_name = "Категория оборудования"; verbose_name_plural = "Категории оборудования"

class Equipment(models.Model):
    STATUS_CHOICES = [
        ('WORKING', 'Работает'),
        ('REPAIR', 'В ремонте'),
        ('STOPPED', 'Остановлено'),
        ('WRITEOFF', 'Списано'),
        ('MAINTENANCE', 'Плановое ТО'),
    ]
    
    inventory_number = models.CharField("Инвентарный номер", max_length=50, unique=True)
    name = models.CharField("Наименование", max_length=200)
    category = models.ForeignKey(EquipmentCategory, on_delete=models.SET_NULL, null=True)
    serial_number = models.CharField("Серийный номер", max_length=100, blank=True)
    manufacturer = models.CharField("Производитель", max_length=100, blank=True)
    install_date = models.DateField("Дата установки", default=timezone.now)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='WORKING')
    location = models.CharField("Место установки", max_length=200, blank=True)
    responsible_person = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, related_name='responsible_equipment')
    image = models.ImageField("Фото", upload_to='equipment/', blank=True, null=True)
    
    def __str__(self): return f"{self.inventory_number} - {self.name}"
    class Meta: verbose_name = "Единица оборудования"; verbose_name_plural = "Оборудование"

class SparePart(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'шт'), ('kg', 'кг'), ('m', 'м'), ('l', 'л'), ('set', 'комплект'),
    ]
    
    sku = models.CharField("Артикул", max_length=50, unique=True)
    name = models.CharField("Наименование", max_length=200)
    category = models.CharField("Категория", max_length=100, blank=True)
    unit = models.CharField("Ед. изм.", max_length=10, choices=UNIT_CHOICES, default='pcs')
    min_stock = models.IntegerField("Мин. остаток", default=5)
    current_stock = models.DecimalField("Текущий остаток", max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField("Цена закупки", max_digits=10, decimal_places=2, default=0)
    sell_price = models.DecimalField("Цена продажи", max_digits=10, decimal_places=2, default=0)
    location_bin = models.CharField("Ячейка хранения", max_length=50, blank=True)
    supplier = models.CharField("Основной поставщик", max_length=100, blank=True)
    
    def __str__(self): return f"{self.sku} - {self.name}"
    class Meta: verbose_name = "Запчасть"; verbose_name_plural = "Запчасти"

class FailureType(models.Model):
    name = models.CharField("Тип отказа", max_length=100)
    description = models.TextField("Описание", blank=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name = "Тип отказа"; verbose_name_plural = "Типы отказов"

class FailureReport(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Низкий'), ('MEDIUM', 'Средний'), ('HIGH', 'Высокий'), ('CRITICAL', 'Критический'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'Новая'), ('ASSIGNED', 'Назначена'), ('IN_PROGRESS', 'В работе'), 
        ('WAITING_PARTS', 'Ждет запчасти'), ('DONE', 'Выполнена'), ('CLOSED', 'Закрыта'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='failures')
    reporter = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, related_name='reported_failures')
    failure_type = models.ForeignKey(FailureType, on_delete=models.SET_NULL, null=True)
    description = models.TextField("Описание проблемы")
    priority = models.CharField("Приоритет", max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_failures')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self): return f"Отказ #{self.id} ({self.equipment.name})"
    class Meta: verbose_name = "Заявка на ремонт"; verbose_name_plural = "Заявки на ремонт"

class WorkOrder(models.Model):
    """Наряд-заказ"""
    STATUS_CHOICES = [
        ('DRAFT', 'Черновик'), ('PLANNED', 'Запланирован'), ('ACTIVE', 'Активен'), 
        ('COMPLETED', 'Завершен'), ('CANCELLED', 'Отменен'),
    ]
    
    title = models.CharField("Название работы", max_length=200)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='work_orders')
    failure_report = models.OneToOneField(FailureReport, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, related_name='supervised_orders')
    executor = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, related_name='executed_orders', blank=True)
    start_date = models.DateTimeField("План. начало", null=True, blank=True)
    end_date = models.DateTimeField("План. окончание", null=True, blank=True)
    actual_start = models.DateTimeField("Факт. начало", null=True, blank=True)
    actual_end = models.DateTimeField("Факт. окончание", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    description = models.TextField("Описание работ", blank=True)
    safety_measures = models.TextField("Меры безопасности", blank=True)
    
    def __str__(self): return f"Наряд #{self.id} - {self.title}"
    class Meta: verbose_name = "Наряд-заказ"; verbose_name_plural = "Наряды-заказы"

class WorkOrderPart(models.Model):
    """Запчасти в наряде"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='parts')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)
    issued = models.BooleanField("Выдано со склада", default=False)
    
    class Meta: verbose_name = "Запчасть в наряде"; verbose_name_plural = "Запчасти в наряде"

class MeterReading(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='meter_readings')
    meter_name = models.CharField("Название счетчика", max_length=100) # e.g., "Моточасы", "Температура"
    value = models.DecimalField("Показание", max_digits=12, decimal_places=2)
    reading_date = models.DateTimeField("Дата снятия", auto_now_add=True)
    taken_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True)
    
    def __str__(self): return f"{self.equipment.name}: {self.value}"
    class Meta: verbose_name = "Показание счетчика"; verbose_name_plural = "Показания счетчиков"

class MaintenancePlan(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_plans')
    task_name = models.CharField("Название операции", max_length=200)
    interval_days = models.IntegerField("Интервал (дни)", default=30)
    last_performed = models.DateField("Последнее выполнение", null=True, blank=True)
    next_due = models.DateField("Следующее ТО", null=True, blank=True)
    
    def __str__(self): return f"{self.equipment.name} - {self.task_name}"
    class Meta: verbose_name = "График ТО"; verbose_name_plural = "Графики ТО"

class StockMovement(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Приход'), ('OUT', 'Расход'), ('ADJUST', 'Корректировка'), ('RETURN', 'Возврат'),
    ]
    
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField("Тип", max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)
    reference_doc = models.CharField("Документ основание", max_length=100, blank=True) # № наряда, № заказа
    performed_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField("Комментарий", blank=True)
    
    def __str__(self): return f"{self.movement_type} {self.spare_part.name} ({self.quantity})"
    class Meta: verbose_name = "Движение запасов"; verbose_name_plural = "Движение запасов"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Черновик'), ('SENT', 'Отправлен'), ('PARTIAL', 'Частично'), ('RECEIVED', 'Получен'),
    ]
    
    supplier_name = models.CharField("Поставщик", max_length=200)
    order_date = models.DateField(auto_now_add=True)
    expected_date = models.DateField(null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_cost = models.DecimalField("Сумма", max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True)
    
    def __str__(self): return f"Заказ поставщику #{self.id}"
    class Meta: verbose_name = "Заказ поставщику"; verbose_name_plural = "Заказы поставщикам"

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.DecimalField("Кол-во", max_digits=10, decimal_places=2)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    received_qty = models.DecimalField("Получено", max_digits=10, decimal_places=2, default=0)
    
    class Meta: verbose_name = "Позиция заказа"; verbose_name_plural = "Позиции заказов"

class SalesOrder(models.Model):
    customer_name = models.CharField("Клиент", max_length=200)
    date = models.DateField(auto_now_add=True)
    status = models.CharField("Статус", max_length=20, default='NEW')
    total_amount = models.DecimalField("Сумма", max_digits=12, decimal_places=2, default=0)
    
    def __str__(self): return f"Продажа #{self.id} - {self.customer_name}"
    class Meta: verbose_name = "Продажа"; verbose_name_plural = "Продажи"

class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.DecimalField("Кол-во", max_digits=10, decimal_places=2)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    
    class Meta: verbose_name = "Позиция продажи"; verbose_name_plural = "Позиции продаж"

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = None # GenericForeignKey defined later if needed, simplified here
    
    author = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Simplified for single file: linking directly to common objects via generic logic in views or specific fields
    # For this demo, we'll link to WorkOrder mostly or use a generic text approach
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    failure_report = models.ForeignKey(FailureReport, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    
    def __str__(self): return f"Comment by {self.author.user.username}"
    class Meta: verbose_name = "Комментарий"; verbose_name_plural = "Комментарии"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField("Ссылка", max_length=200, blank=True)
    
    def __str__(self): return self.title
    class Meta: verbose_name = "Уведомление"; verbose_name_plural = "Уведомления"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50) # CREATE, UPDATE, DELETE, LOGIN
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"{self.action} by {self.user}"
    class Meta: verbose_name = "Лог аудита"; verbose_name_plural = "Логи аудита"

# ==============================================================================
# ФОРМЫ (Forms - Simple Dict based for brevity in single file)
# ==============================================================================
# In a real app, use django.forms.ModelForm

# ==============================================================================
# VIEW FUNCTIONS (Views)
# ==============================================================================

def log_action(request, action, model_name, obj_id=None, details=""):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name=model_name,
            object_id=obj_id,
            details=details
        )

def get_user_profile(user):
    return getattr(user, 'profile', None)

def check_role(allowed_roles):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = get_user_profile(request.user)
            if not profile:
                return redirect('login') # Or error page
            
            role_map = {
                'admin': ['admin'],
                'eng': ['engineer', 'admin'],
                'tech': ['technician', 'engineer', 'admin'],
                'store': ['storekeeper', 'admin', 'engineer'],
                'trainee': ['trainee', 'technician', 'engineer', 'admin'],
                'seller': ['seller', 'admin'],
            }
            
            # Determine current role based on groups or username prefix logic
            # Simplified: checking groups
            user_groups = [g.name for g in request.user.groups.all()]
            if request.user.is_superuser:
                user_groups.append('admin')
            
            can_access = any(role in allowed_roles for role in user_groups)
            
            # Special mapping for prefixes if groups not set perfectly
            if not can_access:
                uname = request.user.username
                if uname.startswith('admin') and 'admin' in allowed_roles: can_access = True
                elif uname.startswith('eng') and ('eng' in allowed_roles or 'engineer' in allowed_roles): can_access = True
                elif uname.startswith('tech') and ('tech' in allowed_roles or 'technician' in allowed_roles): can_access = True
                elif uname.startswith('store') and ('store' in allowed_roles or 'storekeeper' in allowed_roles): can_access = True
                elif uname.startswith('trainee') and 'trainee' in allowed_roles: can_access = True
                elif uname.startswith('seller') and 'seller' in allowed_roles: can_access = True

            if not can_access:
                return render(request, 'error.html', {'message': 'Доступ запрещен'})
            return view_func(request, *args, **kwargs)
        return wrap
    return decorator

@login_required
def dashboard_view(request):
    profile = get_user_profile(request.user)
    user_groups = [g.name for g in request.user.groups.all()]
    if request.user.is_superuser: user_groups.append('admin')
    
    context = {
        'user': request.user,
        'profile': profile,
        'role': user_groups[0] if user_groups else 'user',
        'stats': {}
    }
    
    # Aggregated Stats
    context['stats']['total_equipment'] = Equipment.objects.count()
    context['stats']['working_equipment'] = Equipment.objects.filter(status='WORKING').count()
    context['stats']['low_stock_parts'] = SparePart.objects.filter(current_stock__lt=F('min_stock')).count()
    context['stats']['active_orders'] = WorkOrder.objects.filter(status__in=['ACTIVE', 'PLANNED']).count()
    context['stats']['open_failures'] = FailureReport.objects.filter(status__in=['NEW', 'ASSIGNED', 'IN_PROGRESS']).count()
    
    # Role Specific Data
    if 'admin' in user_groups or request.user.is_superuser:
        context['recent_failures'] = FailureReport.objects.all().order_by('-created_at')[:10]
        context['chart_data'] = {
            'labels': ['Работает', 'Ремонт', 'Остановлено', 'ТО'],
            'data': [
                Equipment.objects.filter(status='WORKING').count(),
                Equipment.objects.filter(status='REPAIR').count(),
                Equipment.objects.filter(status='STOPPED').count(),
                Equipment.objects.filter(status='MAINTENANCE').count(),
            ]
        }
    elif 'storekeeper' in user_groups or request.user.username.startswith('store'):
        context['low_stock_items'] = SparePart.objects.filter(current_stock__lt=F('min_stock'))
        context['recent_movements'] = StockMovement.objects.all().order_by('-timestamp')[:15]
    elif 'technician' in user_groups or request.user.username.startswith('tech'):
        context['my_tasks'] = WorkOrder.objects.filter(executor=profile, status__in=['ACTIVE', 'PLANNED'])
        context['urgent_failures'] = FailureReport.objects.filter(priority='CRITICAL', status__in=['NEW', 'ASSIGNED'])
    
    return render(request, 'dashboard.html', context)

@login_required
def equipment_list(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    items = Equipment.objects.all().select_related('category', 'responsible_person')
    if query:
        items = items.filter(Q(name__icontains=query) | Q(inventory_number__icontains=query))
    if status:
        items = items.filter(status=status)
        
    return render(request, 'equipment_list.html', {'items': items, 'statuses': Equipment.STATUS_CHOICES})

@login_required
def parts_list(request):
    query = request.GET.get('q', '')
    low_stock = request.GET.get('low', '')
    
    items = SparePart.objects.all()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if low_stock == '1':
        items = items.filter(current_stock__lt=F('min_stock'))
        
    return render(request, 'parts_list.html', {'items': items})

@login_required
def failures_list(request):
    items = FailureReport.objects.select_related('equipment', 'reporter', 'assigned_to').all().order_by('-created_at')
    return render(request, 'failures_list.html', {'items': items, 'statuses': FailureReport.STATUS_CHOICES, 'priorities': FailureReport.PRIORITY_CHOICES})

@login_required
def create_failure(request):
    if request.method == 'POST':
        eq_id = request.POST.get('equipment_id')
        desc = request.POST.get('description')
        priority = request.POST.get('priority')
        
        eq = get_object_or_404(Equipment, id=eq_id)
        profile = get_user_profile(request.user)
        
        FailureReport.objects.create(
            equipment=eq,
            reporter=profile,
            description=desc,
            priority=priority,
            status='NEW'
        )
        log_action(request, 'CREATE', 'FailureReport', details=f"Created for {eq.name}")
        return redirect('failures')
    
    equipment_list = Equipment.objects.filter(status__in=['WORKING', 'REPAIR'])
    return render(request, 'create_failure.html', {'equipment_list': equipment_list})

@login_required
def work_orders_list(request):
    items = WorkOrder.objects.select_related('equipment', 'executor', 'supervisor').all().order_by('-created_at') # Add created_at to model if missing, using id for now
    return render(request, 'work_orders.html', {'items': items})

@login_required
def store_dashboard(request):
    # Specific view for storekeeper to manage stock
    low_stock = SparePart.objects.filter(current_stock__lt=F('min_stock'))
    movements = StockMovement.objects.all().order_by('-timestamp')[:20]
    requests = WorkOrderPart.objects.filter(issued=False).select_related('spare_part', 'work_order')
    
    return render(request, 'store_dashboard.html', {
        'low_stock': low_stock,
        'movements': movements,
        'requests': requests
    })

@login_required
def issue_part(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(WorkOrderPart, pk=pk)
        if item.spare_part.current_stock >= item.quantity:
            item.spare_part.current_stock -= item.quantity
            item.spare_part.save()
            item.issued = True
            item.save()
            
            StockMovement.objects.create(
                spare_part=item.spare_part,
                movement_type='OUT',
                quantity=item.quantity,
                reference_doc=f"Наряд #{item.work_order.id}",
                performed_by=get_user_profile(request.user),
                comment="Выдача по наряду"
            )
            log_action(request, 'ISSUE', 'StockMovement', obj_id=item.id)
    return redirect('store')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ==============================================================================
# URL ROUTING
# ==============================================================================

from django.urls import path

urlpatterns = [
    path('', dashboard_view, name='home'),
    path('login/', lambda request: render(request, 'login.html') if request.method == 'GET' else (
        lambda: authenticate_and_login(request)
    )(), name='login'), # Simplified inline logic for POST below
    path('auth-process/', authenticate_and_login, name='auth_process'),
    path('logout/', logout_view, name='logout'),
    path('equipment/', equipment_list, name='equipment'),
    path('parts/', parts_list, name='parts'),
    path('failures/', failures_list, name='failures'),
    path('failures/create/', create_failure, name='create_failure'),
    path('orders/', work_orders_list, name='orders'),
    path('store/', store_dashboard, name='store'),
    path('store/issue/<int:pk>/', issue_part, name='issue_part'),
]

def authenticate_and_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
    return redirect('login')

# ==============================================================================
# HTML TEMPLATES (Embedded for Single File Portability)
# ==============================================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ТОиР Про | Система управления</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .sidebar { transition: all 0.3s; }
        .card { transition: transform 0.2s, box-shadow 0.2s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .glass { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
        .status-badge { @apply px-2 py-1 rounded-full text-xs font-semibold; }
    </style>
</head>
<body class="text-gray-800 antialiased h-screen flex overflow-hidden">
    {% if user.is_authenticated %}
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col shadow-xl z-20 hidden md:flex">
        <div class="h-16 flex items-center justify-center border-b border-slate-800">
            <h1 class="text-xl font-bold tracking-wider"><i class="fa-solid fa-gears text-blue-500 mr-2"></i>ТОиР <span class="text-blue-500">PRO</span></h1>
        </div>
        
        <nav class="flex-1 overflow-y-auto py-4">
            <ul class="space-y-1 px-2">
                <li><a href="{% url 'home' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors {% if request.resolver_match.url_name == 'home' %}bg-blue-600{% endif %}"><i class="fa-solid fa-chart-line w-6"></i> Дашборд</a></li>
                <li><a href="{% url 'equipment' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"><i class="fa-solid fa-industry w-6"></i> Оборудование</a></li>
                <li><a href="{% url 'parts' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"><i class="fa-solid fa-boxes-stacked w-6"></i> Запчасти</a></li>
                <li><a href="{% url 'failures' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"><i class="fa-solid fa-triangle-exclamation w-6"></i> Заявки</a></li>
                <li><a href="{% url 'orders' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"><i class="fa-solid fa-clipboard-check w-6"></i> Наряды</a></li>
                {% if user.username.startswith 'store' or user.is_superuser %}
                <li><a href="{% url 'store' %}" class="flex items-center px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"><i class="fa-solid fa-dolly w-6"></i> Склад</a></li>
                {% endif %}
            </ul>
        </nav>
        
        <div class="p-4 border-t border-slate-800">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center font-bold">{{ user.username|slice:":2"|upper }}</div>
                <div>
                    <p class="text-sm font-medium">{{ user.username }}</p>
                    <p class="text-xs text-gray-400 capitalize">{{ profile.position.title|default:"Сотрудник" }}</p>
                </div>
            </div>
            <a href="{% url 'logout' %}" class="mt-3 block w-full text-center py-2 bg-slate-800 hover:bg-red-600 rounded transition-colors text-xs">Выйти</a>
        </div>
    </aside>
    {% endif %}

    <!-- Main Content -->
    <main class="flex-1 flex flex-col h-screen overflow-hidden relative">
        {% if user.is_authenticated %}
        <header class="h-16 bg-white shadow-sm flex items-center justify-between px-6 z-10">
            <button class="md:hidden text-gray-600"><i class="fa-solid fa-bars"></i></button>
            <h2 class="text-lg font-semibold text-gray-700">{% block header_title %}Панель управления{% endblock %}</h2>
            <div class="flex items-center gap-4">
                <button class="relative p-2 text-gray-400 hover:text-blue-600">
                    <i class="fa-solid fa-bell"></i>
                    <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
            </div>
        </header>
        {% endif %}
        
        <div class="flex-1 overflow-auto p-6 bg-slate-50">
            {% block content %}{% endblock %}
        </div>
    </main>

    <script>
        // Simple Chart Init if needed
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('statusChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: {{ chart_labels|safe }},
                        datasets: [{
                            data: {{ chart_data|safe }},
                            backgroundColor: ['#10b981', '#ef4444', '#f59e0b', '#3b82f6'],
                            borderWidth: 0
                        }]
                    },
                    options: { responsive: true, cutout: '70%' }
                });
            }
        });
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход в систему ТОиР</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gradient-to-br from-slate-900 to-blue-900 h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="p-8">
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-4">
                    <i class="fa-solid fa-gears text-3xl"></i>
                </div>
                <h1 class="text-2xl font-bold text-gray-800">ТОиР PRO</h1>
                <p class="text-gray-500 mt-2">Система управления предприятием</p>
            </div>
            
            {% if error %}
            <div class="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 text-center">{{ error }}</div>
            {% endif %}
            
            <form method="post" action="{% url 'auth_process' %}">
                {% csrf_token %}
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Логин</label>
                        <input type="text" name="username" required class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all" placeholder="admin_otir">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                        <input type="password" name="password" required class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all" placeholder="••••••••">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">Войти</button>
                </div>
            </form>
            
            <div class="mt-8 pt-6 border-t border-gray-100">
                <p class="text-xs text-center text-gray-400 mb-2">Демо доступ (пароль: admin)</p>
                <div class="grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div class="bg-gray-50 p-2 rounded">admin_otir<br><span class="font-semibold">Админ</span></div>
                    <div class="bg-gray-50 p-2 rounded">store_morozov<br><span class="font-semibold">Кладовщик</span></div>
                    <div class="bg-gray-50 p-2 rounded">tech_sidorov<br><span class="font-semibold">Техник</span></div>
                    <div class="bg-gray-50 p-2 rounded">eng_ivanov<br><span class="font-semibold">Инженер</span></div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Обзор системы{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="card bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-500 font-medium">Всего оборудования</p>
                <h3 class="text-2xl font-bold text-gray-800">{{ stats.total_equipment }}</h3>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600"><i class="fa-solid fa-industry"></i></div>
        </div>
    </div>
    <div class="card bg-white p-6 rounded-xl shadow-sm border-l-4 border-green-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-500 font-medium">Исправно</p>
                <h3 class="text-2xl font-bold text-gray-800">{{ stats.working_equipment }}</h3>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600"><i class="fa-solid fa-check"></i></div>
        </div>
    </div>
    <div class="card bg-white p-6 rounded-xl shadow-sm border-l-4 border-red-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-500 font-medium">Низкий остаток</p>
                <h3 class="text-2xl font-bold text-gray-800">{{ stats.low_stock_parts }}</h3>
            </div>
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center text-red-600"><i class="fa-solid fa-triangle-exclamation"></i></div>
        </div>
    </div>
    <div class="card bg-white p-6 rounded-xl shadow-sm border-l-4 border-orange-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-500 font-medium">Активные наряды</p>
                <h3 class="text-2xl font-bold text-gray-800">{{ stats.active_orders }}</h3>
            </div>
            <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center text-orange-600"><i class="fa-solid fa-clipboard-list"></i></div>
        </div>
    </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Статус оборудования</h3>
        <div class="h-64 flex items-center justify-center">
            <canvas id="statusChart"></canvas>
        </div>
        <script>
            var ctx = document.getElementById('statusChart');
            if(ctx){
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: {{ chart_data.labels|safe }},
                        datasets: [{
                            label: 'Количество',
                            data: {{ chart_data.data|safe }},
                            backgroundColor: ['#10b981', '#ef4444', '#f59e0b', '#3b82f6'],
                            borderRadius: 8
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                });
            }
        </script>
    </div>
    
    <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Последние события</h3>
        <div class="space-y-4">
            {% for item in recent_failures|default:"" %}
            <div class="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                <div class="w-2 h-2 mt-2 rounded-full {% if item.priority == 'CRITICAL' %}bg-red-500{% else %}bg-blue-500{% endif %}"></div>
                <div>
                    <p class="text-sm font-medium text-gray-800">{{ item.equipment.name }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ item.description }}</p>
                    <span class="text-[10px] text-gray-400">{{ item.created_at|date:"d.m H:i" }}</span>
                </div>
            </div>
            {% empty %}
            <p class="text-sm text-gray-400 text-center py-4">Нет новых событий</p>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
"""

# Placeholder for other templates to avoid errors, in real app these are separate files
EQUIPMENT_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Оборудование{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm overflow-hidden">
    <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <form method="get" class="flex gap-2">
            <input type="text" name="q" placeholder="Поиск..." class="px-4 py-2 border rounded-lg text-sm" value="{{ request.GET.q }}">
            <select name="status" class="px-4 py-2 border rounded-lg text-sm">
                <option value="">Все статусы</option>
                {% for val, label in statuses %}<option value="{{ val }}" {% if request.GET.status == val %}selected{% endif %}>{{ label }}</option>{% endfor %}
            </select>
            <button class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">Фильтр</button>
        </form>
        <a href="{% url 'create_failure' %}" class="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600"><i class="fa-solid fa-plus mr-1"></i> Заявка</a>
    </div>
    <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-600 font-medium">
            <tr>
                <th class="p-4">Инв. номер</th>
                <th class="p-4">Наименование</th>
                <th class="p-4">Категория</th>
                <th class="p-4">Статус</th>
                <th class="p-4">Ответственный</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
            {% for item in items %}
            <tr class="hover:bg-gray-50">
                <td class="p-4 font-mono text-xs">{{ item.inventory_number }}</td>
                <td class="p-4 font-medium">{{ item.name }}</td>
                <td class="p-4 text-gray-500">{{ item.category.name|default:"-" }}</td>
                <td class="p-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold
                        {% if item.status == 'WORKING' %}bg-green-100 text-green-700
                        {% elif item.status == 'REPAIR' %}bg-red-100 text-red-700
                        {% elif item.status == 'MAINTENANCE' %}bg-blue-100 text-blue-700
                        {% else %}bg-gray-100 text-gray-700{% endif %}">
                        {{ item.get_status_display }}
                    </span>
                </td>
                <td class="p-4 text-gray-500">{{ item.responsible_person.user.username|default:"Не назначен" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

PARTS_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Склад запчастей{% endblock %}
{% block content %}
<div class="mb-4 flex justify-between items-center">
    <form method="get" class="flex gap-2">
        <input type="text" name="q" placeholder="Поиск артикула или названия..." class="px-4 py-2 border rounded-lg text-sm w-64" value="{{ request.GET.q }}">
        <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" name="low" value="1" {% if request.GET.low %}checked{% endif %} class="rounded text-red-500"> Только низкий остаток
        </label>
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Найти</button>
    </form>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {% for part in items %}
    <div class="bg-white p-4 rounded-xl shadow-sm border {% if part.current_stock < part.min_stock %}border-red-300 ring-2 ring-red-100{% endif %}">
        <div class="flex justify-between items-start mb-2">
            <span class="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">{{ part.sku }}</span>
            {% if part.current_stock < part.min_stock %}
            <span class="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded animate-pulse">Низкий остаток!</span>
            {% endif %}
        </div>
        <h3 class="font-bold text-gray-800 mb-1 truncate">{{ part.name }}</h3>
        <p class="text-xs text-gray-500 mb-4">{{ part.get_unit_display }}</p>
        
        <div class="flex justify-between items-end">
            <div>
                <p class="text-xs text-gray-400">На складе</p>
                <p class="text-lg font-bold {% if part.current_stock < part.min_stock %}text-red-600{% else %}text-gray-800{% endif %}">{{ part.current_stock }}</p>
            </div>
            <div class="text-right">
                <p class="text-xs text-gray-400">Мин. запас</p>
                <p class="text-sm font-medium text-gray-600">{{ part.min_stock }}</p>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

FAILURES_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Заявки на ремонт{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm overflow-hidden">
    <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-600 font-medium">
            <tr>
                <th class="p-4">ID</th>
                <th class="p-4">Оборудование</th>
                <th class="p-4">Описание</th>
                <th class="p-4">Приоритет</th>
                <th class="p-4">Статус</th>
                <th class="p-4">Дата</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
            {% for item in items %}
            <tr class="hover:bg-gray-50">
                <td class="p-4 font-mono text-xs">#{{ item.id }}</td>
                <td class="p-4 font-medium">{{ item.equipment.name }}</td>
                <td class="p-4 text-gray-500 max-w-xs truncate">{{ item.description }}</td>
                <td class="p-4">
                    <span class="px-2 py-1 rounded text-xs font-bold
                        {% if item.priority == 'CRITICAL' %}bg-red-600 text-white
                        {% elif item.priority == 'HIGH' %}bg-orange-500 text-white
                        {% elif item.priority == 'MEDIUM' %}bg-yellow-400 text-black
                        {% else %}bg-blue-400 text-white{% endif %}">
                        {{ item.get_priority_display }}
                    </span>
                </td>
                <td class="p-4">{{ item.get_status_display }}</td>
                <td class="p-4 text-gray-400 text-xs">{{ item.created_at|date:"d.m.Y H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

STORE_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Складской учет{% endblock %}
{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
    <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-bold text-red-600 mb-4 flex items-center"><i class="fa-solid fa-triangle-exclamation mr-2"></i> Критический остаток</h3>
        <div class="space-y-3">
            {% for part in low_stock %}
            <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-100">
                <div>
                    <p class="font-bold text-sm text-gray-800">{{ part.name }}</p>
                    <p class="text-xs text-gray-500">{{ part.sku }}</p>
                </div>
                <div class="text-right">
                    <p class="text-lg font-bold text-red-600">{{ part.current_stock }} <span class="text-xs font-normal text-gray-500">/ {{ part.min_stock }}</span></p>
                </div>
            </div>
            {% empty %}
            <p class="text-sm text-gray-500">Все запасы в норме</p>
            {% endfor %}
        </div>
    </div>
    
    <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-bold text-blue-600 mb-4"><i class="fa-solid fa-hand-holding mr-2"></i> Заявки на выдачу</h3>
        <div class="space-y-3">
            {% for req in requests %}
            <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-100">
                <div>
                    <p class="font-bold text-sm text-gray-800">{{ req.spare_part.name }}</p>
                    <p class="text-xs text-gray-500">Наряд #{{ req.work_order.id }}</p>
                </div>
                <form method="post" action="{% url 'issue_part' req.id %}">
                    {% csrf_token %}
                    <button class="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-2 rounded transition-colors">Выдать {{ req.quantity }}</button>
                </form>
            </div>
            {% empty %}
            <p class="text-sm text-gray-500">Нет активных заявок</p>
            {% endfor %}
        </div>
    </div>
</div>

<div class="bg-white rounded-xl shadow-sm p-6">
    <h3 class="text-lg font-bold text-gray-800 mb-4">Последние движения</h3>
    <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-600 font-medium">
            <tr><th class="p-3">Дата</th><th class="p-3">Тип</th><th class="p-3">Запчасть</th><th class="p-3">Кол-во</th><th class="p-3">Документ</th></tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
            {% for mov in movements %}
            <tr>
                <td class="p-3 text-xs text-gray-500">{{ mov.timestamp|date:"d.m H:i" }}</td>
                <td class="p-3"><span class="px-2 py-1 rounded text-xs {% if mov.movement_type == 'IN' %}bg-green-100 text-green-700{% else %}bg-red-100 text-red-700{% endif %}">{{ mov.get_movement_type_display }}</span></td>
                <td class="p-3 font-medium">{{ mov.spare_part.name }}</td>
                <td class="p-3">{{ mov.quantity }}</td>
                <td class="p-3 text-xs text-gray-500">{{ mov.reference_doc }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

CREATE_FAILURE_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Новая заявка{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto bg-white rounded-xl shadow-sm p-8">
    <form method="post">
        {% csrf_token %}
        <div class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Оборудование</label>
                <select name="equipment_id" class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    {% for eq in equipment_list %}
                    <option value="{{ eq.id }}">{{ eq.inventory_number }} - {{ eq.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
                <select name="priority" class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="LOW">Низкий</option>
                    <option value="MEDIUM" selected>Средний</option>
                    <option value="HIGH">Высокий</option>
                    <option value="CRITICAL">Критический</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Описание проблемы</label>
                <textarea name="description" rows="4" class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" required></textarea>
            </div>
            <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg transition-colors">Создать заявку</button>
        </div>
    </form>
</div>
{% endblock %}
"""

WORK_ORDERS_TEMPLATE = """
{% extends "base.html" %}
{% block header_title %}Наряды-заказы{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for order in items %}
    <div class="bg-white rounded-xl shadow-sm p-6 border-t-4 {% if order.status == 'ACTIVE' %}border-green-500{% elif order.status == 'PLANNED' %}border-blue-500{% else %}border-gray-300{% endif %}">
        <div class="flex justify-between items-start mb-4">
            <h3 class="font-bold text-gray-800">{{ order.title }}</h3>
            <span class="text-xs font-bold px-2 py-1 rounded bg-gray-100">{{ order.get_status_display }}</span>
        </div>
        <p class="text-sm text-gray-500 mb-2"><i class="fa-solid fa-industry mr-1"></i> {{ order.equipment.name }}</p>
        <p class="text-sm text-gray-500 mb-4"><i class="fa-solid fa-user mr-1"></i> {{ order.executor.user.username|default:"Не назначен" }}</p>
        <div class="pt-4 border-t border-gray-100 flex justify-between text-xs text-gray-400">
            <span>#{{ order.id }}</span>
            <span>{{ order.start_date|date:"d.m.Y"|default:"Без даты" }}</span>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head><title>Ошибка</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-100 h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center">
        <i class="fa-solid fa-circle-exclamation text-4xl text-red-500 mb-4"></i>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">Доступ запрещен</h1>
        <p class="text-gray-600 mb-6">{{ message }}</p>
        <a href="/" class="text-blue-600 hover:underline">Вернуться назад</a>
    </div>
</body>
</html>
"""

# Save templates to files
TEMPLATES_MAP = {
    'base.html': BASE_TEMPLATE.replace('{% extends "base.html" %}', '').replace('{% block header_title %}Обзор системы{% endblock %}', '{% block header_title %}{% endblock %}').replace('{% block content %}', '{% block content %}').replace('{% endblock %}', '{% endblock %}'),
    'login.html': LOGIN_TEMPLATE,
    'dashboard.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', DASHBOARD_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'equipment_list.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', EQUIPMENT_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'parts_list.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', PARTS_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'failures_list.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', FAILURES_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'create_failure.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', CREATE_FAILURE_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'work_orders.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', WORK_ORDERS_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'store_dashboard.html': BASE_TEMPLATE.replace('{% block content %}{% endblock %}', STORE_TEMPLATE.split('{% block content %}')[1].split('{% endblock %}')[0]),
    'error.html': ERROR_TEMPLATE,
}

# Fix base template replacement logic properly
final_base = BASE_TEMPLATE
for name, content in TEMPLATES_MAP.items():
    if name != 'base.html' and name != 'login.html' and name != 'error.html':
        # Extract block content from specific template and inject into base
        try:
            block_content = content.split('{% block content %}')[1].split('{% endblock %}')[0]
            header_title = content.split('{% block header_title %}')[1].split('{% endblock %}')[0] if '{% block header_title %}' in content else 'Панель управления'
            
            full_page = final_base.replace('{% block header_title %}Панель управления{% endblock %}', f'{{% block header_title %}}{header_title}{{% endblock %}}')
            full_page = full_page.replace('{% block content %}{% endblock %}', f'{{% block content %}}{block_content}{{% endblock %}}')
            
            with open(os.path.join(BASE_DIR, 'templates', name), 'w', encoding='utf-8') as f:
                f.write(full_page)
        except Exception as e:
            print(f"Error processing {name}: {e}")
            with open(os.path.join(BASE_DIR, 'templates', name), 'w', encoding='utf-8') as f:
                f.write(content) # Fallback
    else:
        with open(os.path.join(BASE_DIR, 'templates', name), 'w', encoding='utf-8') as f:
            f.write(content)

# ==============================================================================
# DATA POPULATION SCRIPT (Huge DB Generator)
# ==============================================================================

def populate_db():
    print("Начало наполнения базы данных...")
    
    # Create Groups
    groups = ['admin', 'engineer', 'technician', 'storekeeper', 'trainee', 'seller']
    for g in groups:
        Group.objects.get_or_create(name=g)
    
    # Create Users
    users_data = [
        ('admin_otir', 'Администратор', 'admin', ['admin']),
        ('eng_ivanov', 'Инженер Иванов', 'admin', ['engineer']),
        ('eng_petrov', 'Инженер Петров', 'admin', ['engineer']),
        ('tech_sidorov', 'Техник Сидоров', 'admin', ['technician']),
        ('tech_kuznetsov', 'Техник Кузнецов', 'admin', ['technician']),
        ('tech_popov', 'Техник Попов', 'admin', ['technician']),
        ('store_morozov', 'Кладовщик Морозов', 'admin', ['storekeeper']),
        ('store_novikov', 'Кладовщик Новиков', 'admin', ['storekeeper']),
        ('trainee_smirnov', 'Практикант Смирнов', 'admin', ['trainee']),
        ('trainee_fedorov', 'Практикант Федоров', 'admin', ['trainee']),
        ('seller_petrov', 'Продавец Петров', 'admin', ['seller']),
    ]
    
    profiles = {}
    for uname, fname, pwd, grps in users_data:
        if not User.objects.filter(username=uname).exists():
            u = User.objects.create_user(uname, password=pwd, first_name=fname)
            for g in grps:
                u.groups.add(Group.objects.get(name=g))
            if uname.startswith('admin'): pos, _ = Position.objects.get_or_create(title="Директор", level=5)
            elif uname.startswith('eng'): pos, _ = Position.objects.get_or_create(title="Инженер", level=4)
            elif uname.startswith('tech'): pos, _ = Position.objects.get_or_create(title="Техник", level=3)
            elif uname.startswith('store'): pos, _ = Position.objects.get_or_create(title="Кладовщик", level=3)
            elif uname.startswith('trainee'): pos, _ = Position.objects.get_or_create(title="Практикант", level=1)
            else: pos, _ = Position.objects.get_or_create(title="Продавец", level=2)
            
            dept, _ = Department.objects.get_or_create(name="Основной", code="MAIN")
            prof, _ = EmployeeProfile.objects.get_or_create(user=u, defaults={'position': pos, 'department': dept})
            profiles[uname] = prof

    # Categories & Equipment
    cats = ['Станки ЧПУ', 'Конвейеры', 'Насосы', 'Компрессоры', 'Генераторы']
    cat_objs = [EquipmentCategory.objects.get_or_create(name=c)[0] for c in cats]
    
    print("Создание оборудования (500+)...")
    eq_list = []
    for i in range(550):
        cat = random.choice(cat_objs)
        status = random.choices(['WORKING', 'REPAIR', 'STOPPED', 'MAINTENANCE'], weights=[70, 10, 10, 10])[0]
        eq = Equipment.objects.create(
            inventory_number=f"EQ-{2024000+i}",
            name=f"{cat.name} Модель-{random.randint(100,999)}",
            category=cat,
            status=status,
            manufacturer=random.choice(["Siemens", "Bosch", "ABB", "Schneider", "Local"]),
            location=f"Цех {random.randint(1,5)}, Линия {random.randint(1,10)}"
        )
        eq_list.append(eq)
    
    # Spare Parts
    print("Создание запчастей (2000+)...")
    parts_list = []
    for i in range(2200):
        p = SparePart.objects.create(
            sku=f"SP-{100000+i}",
            name=f"Запчасть типа {random.choice(['Подшипник', 'Сальник', 'Фильтр', 'Ремень', 'Датчик', 'Клапан'])} #{i}",
            category=random.choice(['Механика', 'Электрика', 'Гидравлика', 'Расходники']),
            unit=random.choice(['pcs', 'kg', 'set']),
            min_stock=random.randint(5, 20),
            current_stock=random.randint(0, 100), # Some will be low
            price=random.uniform(100, 5000),
            sell_price=random.uniform(150, 6000)
        )
        parts_list.append(p)

    # Failures & Work Orders
    print("Создание отказов и нарядов (5000+)...")
    failure_types = [FailureType.objects.get_or_create(name=t)[0] for t in ["Износ", "Поломка электроники", "Утечка", "Перегрев", "Вибрация"]]
    
    for i in range(5500):
        eq = random.choice(eq_list)
        rep = random.choice(list(profiles.values()))
        fr = FailureReport.objects.create(
            equipment=eq,
            reporter=rep,
            failure_type=random.choice(failure_types),
            description=f"Описание проблемы #{i}: не работает узел.",
            priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            status=random.choice(['NEW', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CLOSED']),
            created_at=timezone.now() - timedelta(days=random.randint(0, 365))
        )
        
        if random.random() > 0.3:
            wo = WorkOrder.objects.create(
                title=f"Ремонт {eq.name}",
                equipment=eq,
                failure_report=fr,
                supervisor=random.choice(list(profiles.values())),
                executor=random.choice(list(profiles.values())),
                status=random.choice(['DRAFT', 'PLANNED', 'ACTIVE', 'COMPLETED']),
                start_date=timezone.now()
            )
            # Add parts to WO
            if random.random() > 0.5:
                part = random.choice(parts_list)
                WorkOrderPart.objects.create(
                    work_order=wo,
                    spare_part=part,
                    quantity=random.randint(1, 5),
                    issued=random.choice([True, False])
                )

    # Meter Readings
    print("Создание показаний счетчиков (10000+)...")
    readings = []
    for i in range(10000):
        eq = random.choice(eq_list)
        readings.append(MeterReading(
            equipment=eq,
            meter_name=random.choice(["Моточасы", "Температура", "Давление", "Ток"]),
            value=random.uniform(100, 5000),
            reading_date=timezone.now() - timedelta(days=random.randint(0, 100))
        ))
    MeterReading.objects.bulk_create(readings)

    # Stock Movements
    print("Создание движений склада (8000+)...")
    movements = []
    for i in range(8000):
        part = random.choice(parts_list)
        movements.append(StockMovement(
            spare_part=part,
            movement_type=random.choice(['IN', 'OUT', 'ADJUST']),
            quantity=random.randint(1, 20),
            reference_doc=f"DOC-{i}",
            performed_by=random.choice(list(profiles.values())),
            timestamp=timezone.now() - timedelta(days=random.randint(0, 200))
        ))
    StockMovement.objects.bulk_create(movements)
    
    # Notifications, Comments, etc. (Simplified bulk creation)
    print("Создание уведомлений и комментариев...")
    # ... (Similar bulk logic for other models)

    print("База данных успешно наполнена!")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == '__main__':
    # Run migrations first if DB doesn't exist or is empty
    if not os.path.exists(settings.DATABASES['default']['NAME']):
        print("Creating database and migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("Populating database with huge data...")
        populate_db()
        
        # Create superuser explicitly just in case
        if not User.objects.filter(username='admin_otir').exists():
             # Re-run population logic partially if needed, but populate_db handles it
             pass
    
    # Start server
    print("\n" + "="*50)
    print("СИСТЕМА ТОиР ПРО ГОТОВА К ЗАПУСКУ")
    print("="*50)
    print("Логин: admin_otir / Пароль: admin")
    print("Логин: store_morozov / Пароль: admin (для проверки склада)")
    print("="*50 + "\n")
    
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
