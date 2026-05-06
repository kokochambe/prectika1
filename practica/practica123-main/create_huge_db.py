"""
Скрипт для генерации огромной базы данных для системы ТОиР
Генерирует:
- 500 единиц оборудования
- 1000 запчастей
- 2000 нарядов-заказов
- 5000 отказов оборудования
- 10000 показаний счётчиков
- 3000 заявок на запчасти
- 500 продаж
- и многое другое
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maint_system.settings')
django.setup()

from accounts.models import User
from equipment.models import Equipment, MaintenanceSchedule, EquipmentFailure, EquipmentMeterReading, EquipmentDocument, EquipmentChangeLog
from workorders.models import WorkOrder, TaskNotification, WorkReport, WorkOrderComment, WorkOrderStatusHistory, WorkAttachment, WorkLog, WorkOrderRating, WorkTemplate
from inventory.models import SparePart, PartRequest, InventoryTransaction, Supplier, PurchaseOrder, PurchaseOrderItem
from sales.models import Sale

# Константы для генерации
NUM_EQUIPMENT = 500
NUM_SPARE_PARTS = 1000
NUM_WORK_ORDERS = 2000
NUM_FAILURES = 5000
NUM_METER_READINGS = 10000
NUM_PART_REQUESTS = 3000
NUM_MAINTENANCE_SCHEDULES = 600
NUM_DOCUMENTS = 800
NUM_CHANGE_LOGS = 1500
NUM_NOTIFICATIONS = 4000
NUM_WORK_REPORTS = 1800
NUM_COMMENTS = 2500
NUM_STATUS_HISTORY = 3500
NUM_ATTACHMENTS = 1200
NUM_WORK_LOGS = 5000
NUM_RATINGS = 800
NUM_TEMPLATES = 50
NUM_SUPPLIERS = 30
NUM_PURCHASE_ORDERS = 200
NUM_TRANSACTIONS = 8000
NUM_SALES = 500

# Данные для генерации
EQUIPMENT_TYPES = [
    'Насосы', 'Компрессоры', 'Электропривод', 'Механика', 
    'Вентиляция', 'Транспорт', 'Металлообработка', 'Энергетика', 
    'Электрика', 'Автоматика'
]

WORKSHOPS = [
    'Цех №1', 'Цех №2', 'Цех №3', 'Участок А', 'Участок Б', 
    'Участок В', 'Лаборатория', 'Склад', 'Гараж'
]

MANUFACTURERS = [
    'Siemens', 'ABB', 'Schneider Electric', 'Bosch Rexroth', 
    'Parker Hannifin', 'SKF', 'Festo', 'Omron', 'Danfoss', 
    'KSB', 'Grundfos', 'Atlas Copco', 'Kaeser', 'Ingersoll Rand',
    'General Electric', 'WEG', 'Lenze', 'SEW-Eurodrive'
]

FAILURE_TYPES = ['mechanical', 'electrical', 'hydraulic', 'pneumatic', 'software', 'operator_error', 'wear_out', 'other']
SEVERITY_LEVELS = [1, 2, 3, 4]
READING_TYPES = ['hours', 'cycles', 'kilometers', 'units', 'pressure', 'temperature', 'vibration', 'other']
DOCUMENT_TYPES = ['manual', 'passport', 'certificate', 'diagram', 'specification', 'protocol', 'act', 'other']
CHANGE_TYPES = ['status', 'location', 'assignment', 'modification', 'repair', 'inspection', 'other']
ORDER_TYPES = ['planned', 'emergency', 'modernization', 'inspection']
LOG_TYPES = ['start', 'pause', 'resume', 'complete', 'note', 'issue']
PART_CATEGORIES = ['bearings', 'seals', 'filters', 'belts', 'electrical', 'hydraulic', 'pneumatic', 'fasteners', 'lubricants', 'tools', 'other']
TRANSACTION_TYPES = ['receipt', 'issue', 'adjustment', 'return', 'write_off', 'transfer']
SALE_TYPES = ['equipment', 'spare_part', 'service']

def get_random_date(start_date, end_date):
    """Генерация случайной даты в диапазоне"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def get_random_datetime(start_date, end_date):
    """Генерация случайной даты и времени в диапазоне"""
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

def batch_create(model_class, objects, batch_size=500):
    """Пакетное создание объектов"""
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        model_class.objects.bulk_create(batch)
        print(f"  Создано {min(i + batch_size, len(objects))} из {len(objects)}")

print("=" * 60)
print("Генерация огромной базы данных для системы ТОиР")
print("=" * 60)

# Получаем пользователей
users = list(User.objects.all())
if not users:
    print("Ошибка: Нет пользователей в базе данных!")
    print("Запустите сначала create_users.py")
    sys.exit(1)

print(f"\nНайдено пользователей: {len(users)}")

# Распределяем пользователей по ролям
admins = [u for u in users if u.role == 'admin']
engineers = [u for u in users if u.role == 'engineer']
technicians = [u for u in users if u.role == 'technician']
storekeepers = [u for u in users if u.role == 'storekeeper']
trainees = [u for u in users if u.role == 'trainee']
sellers = [u for u in users if u.role == 'seller']

print(f"  Администраторы: {len(admins)}")
print(f"  Инженеры: {len(engineers)}")
print(f"  Техники: {len(technicians)}")
print(f"  Кладовщики: {len(storekeepers)}")
print(f"  Практиканты: {len(trainees)}")
print(f"  Продавцы: {len(sellers)}")

# Генерация поставщиков
print("\n[1/16] Генерация поставщиков...")
suppliers = []
for i in range(NUM_SUPPLIERS):
    supplier = Supplier(
        name=f"Поставщик {i+1} - {random.choice(['ООО', 'АО', 'ИП'])} '{random.choice(['Техно', 'Пром', 'Индустр', 'Сервис', 'Трейд'])}{random.randint(100, 999)}'",
        contact_person=f"{random.choice(['Иван', 'Петр', 'Алексей', 'Дмитрий', 'Сергей', 'Андрей', 'Николай', 'Владимир'])} {random.choice(['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Попов'])}",
        email=f"info@supplier{i+1}.ru",
        phone=f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
        address=f"г. Москва, ул. {random.choice(['Ленина', 'Кирова', 'Гагарина', 'Пушкина'])}, д. {random.randint(1, 100)}",
        website=f"https://www.supplier{i+1}.ru",
        rating=random.randint(3, 5),
        payment_terms=random.choice(['Предоплата 100%', 'Предоплата 50%', 'Отсрочка 30 дней', 'По факту']),
        delivery_time_days=random.randint(3, 30),
    )
    suppliers.append(supplier)

Supplier.objects.bulk_create(suppliers)
suppliers = list(Supplier.objects.all())
print(f"  ✓ Создано {len(suppliers)} поставщиков")

# Генерация оборудования
print("\n[2/16] Генерация оборудования...")
equipment_list = []
for i in range(NUM_EQUIPMENT):
    inv_number = f"EQ-{random.randint(10000, 99999)}"
    equip_type = random.choice(EQUIPMENT_TYPES)
    manufacturer = random.choice(MANUFACTURERS)
    
    install_date = get_random_date(datetime(2015, 1, 1).date(), datetime(2024, 12, 1).date())
    warranty_years = random.randint(1, 5)
    warranty_until = install_date + timedelta(days=warranty_years*365)
    
    status = random.choices(
        ['active', 'maintenance', 'out_of_service', 'decommissioned'],
        weights=[70, 15, 10, 5]
    )[0]
    
    criticality = random.choices([1, 2, 3, 4], weights=[10, 20, 50, 20])[0]
    
    purchase_price = Decimal(random.randint(50000, 5000000))
    
    equipment = Equipment(
        inv_number=inv_number,
        name=f"{equip_type} {manufacturer} модель {random.choice(['X', 'Y', 'Z', 'A', 'B'])}-{random.randint(100, 999)}",
        type=equip_type,
        workshop=random.choice(WORKSHOPS),
        status=status,
        install_date=install_date,
        warranty_until=warranty_until if random.random() > 0.3 else None,
        last_maintenance=get_random_date(install_date, datetime.now().date()) if random.random() > 0.2 else None,
        manufacturer=manufacturer,
        model=f"{random.choice(['Pro', 'Plus', 'Max', 'Ultra', 'Standard'])} {random.randint(100, 999)}",
        serial_number=f"SN-{random.randint(100000, 999999)}",
        criticality=criticality,
        purchase_price=purchase_price,
        replacement_value=purchase_price * Decimal(random.uniform(1.2, 2.0)),
        expected_lifetime_years=random.randint(10, 25),
        location_details=f"Здание {random.randint(1, 10)}, этаж {random.randint(1, 3)}, секция {random.choice(['A', 'B', 'C', 'D'])}",
        technical_specs=f"Мощность: {random.randint(1, 100)} кВт, Производительность: {random.randint(100, 1000)} ед/час",
        qr_code=f"QR-{inv_number}",
        barcode=f"BC-{random.randint(1000000, 9999999)}",
        responsible_person=random.choice(users) if random.random() > 0.3 else None,
        notes=f"Оборудование установлено в {install_date.year} году. {'Требует особого внимания.' if criticality == 1 else ''}" if random.random() > 0.5 else None,
    )
    equipment_list.append(equipment)

Equipment.objects.bulk_create(equipment_list)
equipment_list = list(Equipment.objects.all())
print(f"  ✓ Создано {len(equipment_list)} единиц оборудования")

# Генерация запчастей
print("\n[3/16] Генерация запчастей...")
spare_parts = []
for i in range(NUM_SPARE_PARTS):
    sku = f"SP-{random.randint(100000, 999999)}"
    category = random.choice(PART_CATEGORIES)
    unit = random.choice(['pcs', 'kg', 'l', 'm', 'set', 'box'])
    
    part = SparePart(
        sku=sku,
        name=f"{category.title()} {random.choice(['Тип', 'Модель', 'Вид'])} {random.randint(100, 999)}",
        category=category,
        unit_price=Decimal(random.uniform(10, 50000)),
        min_stock=random.randint(5, 50),
        current_stock=random.randint(0, 500),
        reserved_stock=random.randint(0, 50),
        warehouse_location=f"Стеллаж {random.randint(1, 20)}, полка {random.choice(['A', 'B', 'C', 'D'])}, ячейка {random.randint(1, 100)}",
        supplier=random.choice(suppliers).name if random.random() > 0.2 else None,
        manufacturer=random.choice(MANUFACTURERS) if random.random() > 0.3 else None,
        lead_time_days=random.randint(1, 60),
        reorder_quantity=random.randint(10, 100),
        last_purchase_date=get_random_date(datetime(2023, 1, 1).date(), datetime(2024, 12, 1).date()) if random.random() > 0.3 else None,
        last_purchase_price=Decimal(random.uniform(10, 50000)) if random.random() > 0.3 else None,
        barcode=f"BC-SP-{random.randint(1000000, 9999999)}",
        notes=f"Запчасть категории {category}. " + ("Совместима с несколькими типами оборудования." if random.random() > 0.5 else ""),
        is_active=random.random() > 0.1,
    )
    spare_parts.append(part)

SparePart.objects.bulk_create(spare_parts)
spare_parts = list(SparePart.objects.all())
print(f"  ✓ Создано {len(spare_parts)} запчастей")

# Связываем запчасти с оборудованием
print("  Создание связей запчасти-оборудование...")
for part in spare_parts[:300]:  # Первые 300 запчастей связываем с оборудованием
    compatible = random.sample(equipment_list, k=min(random.randint(1, 10), len(equipment_list)))
    part.compatible_equipment.set(compatible)

# Генерация графиков ТО
print("\n[4/16] Генерация графиков технического обслуживания...")
schedules = []
for equip in equipment_list[:NUM_MAINTENANCE_SCHEDULES]:
    frequency = random.choice(['daily', 'weekly', 'monthly', 'quarterly', 'semi_annual', 'annual', 'custom'])
    frequency_days = {
        'daily': 1, 'weekly': 7, 'monthly': 30, 'quarterly': 90,
        'semi_annual': 180, 'annual': 365, 'custom': random.randint(100, 500)
    }[frequency]
    
    last_completed = get_random_date(datetime(2023, 1, 1).date(), datetime.now().date())
    next_due = last_completed + timedelta(days=frequency_days)
    
    schedule = MaintenanceSchedule(
        equipment=equip,
        frequency_days=frequency_days,
        frequency_type=frequency,
        next_due=next_due,
        last_completed=last_completed if random.random() > 0.2 else None,
        checklist="Проверка масла, натяжение, очистка фильтров, смазка, замер вибрации, визуальный осмотр",
        is_active=random.random() > 0.1,
        estimated_duration_hours=Decimal(random.uniform(0.5, 8.0)),
        required_specialists=random.choice(['Механик', 'Электрик', 'Универсал', 'Бригада']),
        required_parts=f"Масло {random.randint(1, 5)}л, Фильтры {random.randint(1, 3)}шт, Смазка {random.randint(1, 2)}кг",
        safety_requirements="Отключить питание, установить знаки безопасности, использовать СИЗ",
        cost_estimate=Decimal(random.randint(1000, 50000)),
        created_by=random.choice(engineers) if engineers else random.choice(users),
    )
    schedules.append(schedule)

MaintenanceSchedule.objects.bulk_create(schedules)
print(f"  ✓ Создано {len(schedules)} графиков ТО")

# Генерация отказов оборудования
print("\n[5/16] Генерация отказов оборудования...")
failures = []
for i in range(NUM_FAILURES):
    equip = random.choice(equipment_list)
    failure_date = get_random_datetime(
        datetime(2020, 1, 1),
        datetime.now()
    )
    
    severity = random.choice(SEVERITY_LEVELS)
    failure_type = random.choice(FAILURE_TYPES)
    
    resolved = random.random() > 0.15
    resolved_date = failure_date + timedelta(hours=random.randint(1, 72)) if resolved else None
    
    failure = EquipmentFailure(
        equipment=equip,
        failure_date=failure_date,
        failure_type=failure_type,
        severity=severity,
        description=f"Отказ типа {failure_type}. Оборудование перестало функционировать нормально.",
        root_cause=f"Причина: {random.choice(['Износ деталей', 'Перегрузка', 'Неправильная эксплуатация', 'Производственный дефект', 'Внешнее воздействие'])}",
        corrective_action=f"Выполнены работы по устранению: {random.choice(['Замена деталей', 'Регулировка', 'Ремонт', 'Настройка'])}",
        downtime_hours=Decimal(random.uniform(0.5, 48.0)),
        repair_cost=Decimal(random.randint(500, 200000)),
        reported_by=random.choice(users),
        resolved_by=random.choice(technicians) if technicians and resolved else None,
        resolved_at=resolved_date,
        photos=f'["photo_{i}_1.jpg", "photo_{i}_2.jpg"]' if random.random() > 0.5 else None,
    )
    failures.append(failure)

EquipmentFailure.objects.bulk_create(failures)
print(f"  ✓ Создано {len(failures)} отказов")

# Генерация показаний счётчиков
print("\n[6/16] Генерация показаний счётчиков...")
meter_readings = []
for i in range(NUM_METER_READINGS):
    equip = random.choice(equipment_list)
    reading_type = random.choice(READING_TYPES)
    
    units = {
        'hours': 'ч', 'cycles': 'циклов', 'kilometers': 'км', 'units': 'ед',
        'pressure': 'бар', 'temperature': '°C', 'vibration': 'мм/с', 'other': 'ед'
    }
    
    base_value = random.randint(100, 100000)
    
    reading = EquipmentMeterReading(
        equipment=equip,
        reading_type=reading_type,
        value=Decimal(base_value + random.randint(-1000, 10000)),
        unit=units[reading_type],
        reading_date=get_random_datetime(datetime(2020, 1, 1), datetime.now()),
        taken_by=random.choice(users),
        notes=f"Показания сняты при плановой проверке" if random.random() > 0.7 else None,
    )
    meter_readings.append(reading)

EquipmentMeterReading.objects.bulk_create(meter_readings)
print(f"  ✓ Создано {len(meter_readings)} показаний счётчиков")

# Генерация документов оборудования
print("\n[7/16] Генерация документов оборудования...")
documents = []
for i in range(NUM_DOCUMENTS):
    equip = random.choice(equipment_list)
    doc_type = random.choice(DOCUMENT_TYPES)
    
    document = EquipmentDocument(
        equipment=equip,
        document_type=doc_type,
        title=f"{doc_type.title()} для оборудования {equip.inv_number}",
        file=f"docs/{doc_type}_{i}.pdf",
        file_size=random.randint(10000, 10000000),
        uploaded_by=random.choice(users),
        version=f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
        is_current=random.random() > 0.2,
        notes=f"Документ загружен для оборудования {equip.name}",
    )
    documents.append(document)

EquipmentDocument.objects.bulk_create(documents)
print(f"  ✓ Создано {len(documents)} документов")

# Генерация журнала изменений оборудования
print("\n[8/16] Генерация журнала изменений...")
change_logs = []
for i in range(NUM_CHANGE_LOGS):
    equip = random.choice(equipment_list)
    change_type = random.choice(CHANGE_TYPES)
    
    log = EquipmentChangeLog(
        equipment=equip,
        change_type=change_type,
        old_value=f"Старое значение {random.randint(1, 100)}",
        new_value=f"Новое значение {random.randint(1, 100)}",
        description=f"Изменение типа {change_type} для оборудования {equip.inv_number}",
        changed_by=random.choice(users),
    )
    change_logs.append(log)

EquipmentChangeLog.objects.bulk_create(change_logs)
print(f"  ✓ Создано {len(change_logs)} записей журнала изменений")

# Генерация нарядов-заказов
print("\n[9/16] Генерация нарядов-заказов...")
work_orders = []
for i in range(NUM_WORK_ORDERS):
    equip = random.choice(equipment_list)
    order_type = random.choice(ORDER_TYPES)
    priority = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 40, 20, 10])[0]
    status = random.choices(
        ['new', 'assigned', 'in_progress', 'pending_parts', 'completed', 'rejected'],
        weights=[10, 15, 20, 10, 40, 5]
    )[0]
    
    created_at = get_random_datetime(datetime(2023, 1, 1), datetime.now())
    started_at = created_at + timedelta(hours=random.randint(1, 48)) if status != 'new' else None
    completed_at = started_at + timedelta(hours=random.randint(1, 72)) if status == 'completed' else None
    
    wo = WorkOrder(
        equipment=equip,
        order_type=order_type,
        priority=priority,
        status=status,
        assigned_user=random.choice(technicians) if status in ['assigned', 'in_progress', 'completed'] else None,
        created_by=random.choice(engineers + admins),
        description=f"Работы по техническому обслуживанию/ремонту оборудования {equip.inv_number}. Требуется выполнение регламентных работ.",
        created_at=created_at,
        started_at=started_at,
        completed_at=completed_at,
        estimated_hours=Decimal(random.uniform(1, 40)),
        actual_hours=Decimal(random.uniform(1, 50)) if completed_at else None,
        cost_estimate=Decimal(random.randint(1000, 100000)),
        actual_cost=Decimal(random.randint(1000, 150000)) if completed_at else None,
        location=equip.location_details,
        safety_measures="Отключить питание, установить знаки безопасности, использовать СИЗ",
        completion_notes="Работы выполнены в полном объеме. Оборудование протестировано." if status == 'completed' else None,
    )
    work_orders.append(wo)

WorkOrder.objects.bulk_create(work_orders)
work_orders = list(WorkOrder.objects.all())
print(f"  ✓ Создано {len(work_orders)} нарядов-заказов")

# Генерация уведомлений о задачах
print("\n[10/16] Генерация уведомлений...")
notifications = []
for i in range(NUM_NOTIFICATIONS):
    worker = random.choice(technicians + trainees)
    wo = random.choice(work_orders)
    
    notification = TaskNotification(
        worker=worker,
        work_order=wo,
        message=f"Вам назначена задача по наряду #{wo.id}. Оборудование: {wo.equipment.inv_number}",
        notification_type=random.choice(['task', 'message', 'alert', 'reminder']),
        status=random.choice(['pending', 'read', 'accepted', 'in_progress', 'done']),
        created_by=random.choice(engineers + admins),
        is_read=random.random() > 0.3,
        read_at=get_random_datetime(datetime(2023, 1, 1), datetime.now()) if random.random() > 0.3 else None,
    )
    notifications.append(notification)

TaskNotification.objects.bulk_create(notifications)
print(f"  ✓ Создано {len(notifications)} уведомлений")

# Генерация отчётов о работах
print("\n[11/16] Генерация отчётов о работах...")
reports = []
completed_wos = [wo for wo in work_orders if wo.status == 'completed']
for wo in completed_wos[:NUM_WORK_REPORTS]:
    report = WorkReport(
        work_order=wo,
        report_date=wo.completed_at.date() if wo.completed_at else datetime.now().date(),
        hours_spent=wo.actual_hours if wo.actual_hours else Decimal(random.uniform(1, 20)),
        description="Работы выполнены согласно регламенту. Все операции завершены успешно.",
        technician_signature=f"{wo.assigned_user.username}" if wo.assigned_user else "Неизвестный",
        quality_rating=random.choice([3, 4, 4, 5, 5]),
        parts_used=f"Запчасти: {random.choice(['Подшипник', 'Фильтр', 'Ремень', 'Уплотнение'])} x{random.randint(1, 5)}",
        issues_found=random.choice(["Замечаний нет", "Обнаружен износ деталей", "Требуется повторная проверка"]),
        recommendations=random.choice(["Продолжить эксплуатацию", "Запланировать замену", "Провести дополнительное ТО"]),
        photos=f'["report_photo_1.jpg", "report_photo_2.jpg"]' if random.random() > 0.5 else None,
    )
    reports.append(report)

WorkReport.objects.bulk_create(reports)
print(f"  ✓ Создано {len(reports)} отчётов")

# Генерация комментариев к нарядам
print("\n[12/16] Генерация комментариев...")
comments = []
for i in range(NUM_COMMENTS):
    wo = random.choice(work_orders)
    
    comment = WorkOrderComment(
        work_order=wo,
        author=random.choice(users),
        text=f"Комментарий к наряду #{wo.id}. " + random.choice([
            "Работы начаты вовремя.",
            "Требуется дополнительная координация.",
            "Все идёт по плану.",
            "Есть небольшие задержки.",
            "Необходимы дополнительные запчасти."
        ]),
        parent_comment=None,
        is_edited=random.random() > 0.9,
    )
    comments.append(comment)

WorkOrderComment.objects.bulk_create(comments)
print(f"  ✓ Создано {len(comments)} комментариев")

# Генерация истории статусов
print("\n[13/16] Генерация истории статусов...")
status_history = []
for wo in work_orders[:NUM_STATUS_HISTORY]:
    statuses = ['new', 'assigned', 'in_progress', 'completed']
    for j in range(len(statuses) - 1):
        history = WorkOrderStatusHistory(
            work_order=wo,
            old_status=statuses[j],
            new_status=statuses[j + 1],
            changed_by=random.choice(users),
            comment=f"Статус изменён автоматически или пользователем",
        )
        status_history.append(history)

WorkOrderStatusHistory.objects.bulk_create(status_history)
print(f"  ✓ Создано {len(status_history)} записей истории статусов")

# Генерация журнала работ
print("\n[14/16] Генерация журнала работ...")
work_logs = []
for i in range(NUM_WORK_LOGS):
    wo = random.choice(work_orders)
    log_type = random.choice(LOG_TYPES)
    
    duration = random.randint(10, 480) if log_type in ['start', 'pause'] else None
    
    log = WorkLog(
        work_order=wo,
        technician=random.choice(technicians) if technicians else random.choice(users),
        log_type=log_type,
        description=f"Запись типа {log_type}: {random.choice(['Начало работ', 'Перерыв', 'Возобновление', 'Завершение этапа', 'Заметка', 'Проблема'])}",
        start_time=get_random_datetime(datetime(2023, 1, 1), datetime.now()),
        end_time=None,
        duration_minutes=duration,
    )
    work_logs.append(log)

WorkLog.objects.bulk_create(work_logs)
print(f"  ✓ Создано {len(work_logs)} записей журнала работ")

# Генерация заявок на запчасти
print("\n[15/16] Генерация заявок на запчасти...")
part_requests = []
for i in range(NUM_PART_REQUESTS):
    wo = random.choice(work_orders)
    part = random.choice(spare_parts)
    
    requested_qty = random.randint(1, 20)
    issued_qty = random.randint(0, requested_qty) if random.random() > 0.3 else 0
    
    status = random.choices(
        ['requested', 'approved', 'issued', 'rejected', 'partially_issued'],
        weights=[15, 25, 35, 10, 15]
    )[0]
    
    request = PartRequest(
        work_order=wo,
        spare_part=part,
        quantity_requested=requested_qty,
        quantity_issued=issued_qty,
        status=status,
        priority=random.choice([1, 2, 3, 4]),
        requested_by=random.choice(technicians),
        approved_by=random.choice(engineers + admins) if status in ['approved', 'issued', 'partially_issued'] else None,
        fulfilled_by=random.choice(storekeepers) if status in ['issued', 'partially_issued'] else None,
        fulfilled_at=get_random_datetime(datetime(2023, 1, 1), datetime.now()) if status in ['issued', 'partially_issued'] else None,
        rejection_reason="Нет в наличии" if status == 'rejected' else None,
        notes=f"Заявка на запчасти для наряда #{wo.id}",
    )
    part_requests.append(request)

PartRequest.objects.bulk_create(part_requests)
print(f"  ✓ Создано {len(part_requests)} заявок на запчасти")

# Генерация операций с запчастями
print("\n[16/16] Генерация операций с запчастями...")
transactions = []
for i in range(NUM_TRANSACTIONS):
    part = random.choice(spare_parts)
    trans_type = random.choice(TRANSACTION_TYPES)
    
    qty = random.randint(1, 100)
    stock_before = random.randint(50, 500)
    stock_after = stock_before + qty if trans_type in ['receipt', 'return'] else stock_before - qty
    
    transaction = InventoryTransaction(
        spare_part=part,
        transaction_type=trans_type,
        quantity=Decimal(qty),
        unit_price=part.unit_price,
        total_amount=Decimal(qty) * part.unit_price,
        stock_before=stock_before,
        stock_after=max(0, stock_after),
        reference_document=f"DOC-{random.randint(10000, 99999)}",
        related_request=random.choice(part_requests) if random.random() > 0.5 else None,
        performed_by=random.choice(storekeepers) if storekeepers else random.choice(users),
        notes=f"Операция типа {trans_type} для запчасти {part.sku}",
    )
    transactions.append(transaction)

InventoryTransaction.objects.bulk_create(transactions)
print(f"  ✓ Создано {len(transactions)} операций с запчастями")

# Генерация заказов на поставку
print("\n[Дополнительно] Генерация заказов на поставку...")
purchase_orders = []
for i in range(NUM_PURCHASE_ORDERS):
    supplier = random.choice(suppliers)
    order_date = get_random_date(datetime(2023, 1, 1).date(), datetime.now().date())
    
    po = PurchaseOrder(
        supplier=supplier,
        order_number=f"PO-{random.randint(10000, 99999)}",
        order_date=order_date,
        expected_delivery_date=order_date + timedelta(days=random.randint(7, 30)),
        actual_delivery_date=order_date + timedelta(days=random.randint(7, 30)) if random.random() > 0.3 else None,
        status=random.choice(['draft', 'sent', 'confirmed', 'partial', 'received', 'cancelled']),
        total_amount=Decimal(random.randint(10000, 500000)),
        notes=f"Заказ поставщику {supplier.name}",
        created_by=random.choice(admins + engineers),
    )
    purchase_orders.append(po)

PurchaseOrder.objects.bulk_create(purchase_orders)
purchase_orders = list(PurchaseOrder.objects.all())

# Позиции заказов
po_items = []
for po in purchase_orders[:100]:
    for _ in range(random.randint(3, 10)):
        part = random.choice(spare_parts)
        qty = random.randint(5, 50)
        
        item = PurchaseOrderItem(
            purchase_order=po,
            spare_part=part,
            quantity_ordered=qty,
            quantity_received=qty if random.random() > 0.3 else 0,
            unit_price=part.unit_price,
            total_price=Decimal(qty) * part.unit_price,
            received_at=get_random_datetime(datetime(2023, 1, 1), datetime.now()) if random.random() > 0.3 else None,
        )
        po_items.append(item)

PurchaseOrderItem.objects.bulk_create(po_items)
print(f"  ✓ Создано {len(purchase_orders)} заказов на поставку")
print(f"  ✓ Создано {len(po_items)} позиций заказов")

# Генерация продаж
print("\n[Дополнительно] Генерация продаж...")
sales = []
for i in range(NUM_SALES):
    sale_type = random.choice(SALE_TYPES)
    price = Decimal(random.randint(1000, 100000))
    quantity = random.randint(1, 10)
    
    sale = Sale(
        sale_type=sale_type,
        equipment=random.choice(equipment_list) if sale_type == 'equipment' else None,
        spare_part=random.choice(spare_parts) if sale_type == 'spare_part' else None,
        service_name="Техническое обслуживание" if sale_type == 'service' else None,
        quantity=quantity,
        price=price,
        total_amount=price * quantity,  # Явно устанавливаем total_amount
        seller=random.choice(sellers) if sellers else random.choice(users),
        customer_name=f"Клиент {random.randint(1, 1000)}",
        customer_phone=f"+7 ({random.randint(400, 999)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
        notes=f"Продажа типа {sale_type}",
    )
    sales.append(sale)

Sale.objects.bulk_create(sales)
print(f"  ✓ Создано {len(sales)} продаж")

# Генерация оценок работ
print("\n[Дополнительно] Генерация оценок работ...")
ratings = []
rated_wos = random.sample(work_orders, k=min(NUM_RATINGS, len(work_orders)))
for wo in rated_wos:
    rating = WorkOrderRating(
        work_order=wo,
        rated_by=random.choice(users),
        quality_score=random.randint(3, 5),
        timeliness_score=random.randint(3, 5),
        professionalism_score=random.randint(3, 5),
        comment=random.choice(["Отличная работа!", "Хорошо выполнено", "Есть замечания", "Всё в порядке"]),
    )
    ratings.append(rating)

WorkOrderRating.objects.bulk_create(ratings)
print(f"  ✓ Создано {len(ratings)} оценок")

# Генерация шаблонов работ
print("\n[Дополнительно] Генерация шаблонов работ...")
templates = []
template_names = [
    "Ежедневное ТО насоса", "Еженедельная проверка компрессора", 
    "Месячное ТО электропривода", "Квартальное обслуживание вентиляции",
    "Годовое ТО оборудования", "Аварийный ремонт", "Замена подшипников",
    "Проверка электрики", "Диагностика гидравлики", "Чистка фильтров"
]

for i in range(NUM_TEMPLATES):
    template = WorkTemplate(
        name=template_names[i % len(template_names)] + f" v{i//10}",
        description=f"Шаблон типовых работ для {random.choice(EQUIPMENT_TYPES)}",
        equipment_type=random.choice(EQUIPMENT_TYPES),
        checklist="1. Проверка состояния\n2. Замер параметров\n3. Замена расходников\n4. Тестирование",
        estimated_hours=Decimal(random.uniform(1, 8)),
        required_parts=f"Масло, фильтры, уплотнения",
        safety_requirements="Использовать СИЗ, отключить питание",
        is_active=True,
        created_by=random.choice(engineers),
    )
    templates.append(template)

WorkTemplate.objects.bulk_create(templates)
print(f"  ✓ Создано {len(templates)} шаблонов работ")

# Итоговая статистика
print("\n" + "=" * 60)
print("ГЕНЕРАЦИЯ БАЗЫ ДАННЫХ ЗАВЕРШЕНА!")
print("=" * 60)
print(f"\nИТОГОВАЯ СТАТИСТИКА:")
print(f"  • Оборудование: {Equipment.objects.count()}")
print(f"  • Запчасти: {SparePart.objects.count()}")
print(f"  • Наряды-заказы: {WorkOrder.objects.count()}")
print(f"  • Отказы: {EquipmentFailure.objects.count()}")
print(f"  • Показания счётчиков: {EquipmentMeterReading.objects.count()}")
print(f"  • Графики ТО: {MaintenanceSchedule.objects.count()}")
print(f"  • Документы: {EquipmentDocument.objects.count()}")
print(f"  • Заявки на запчасти: {PartRequest.objects.count()}")
print(f"  • Операции с запчастями: {InventoryTransaction.objects.count()}")
print(f"  • Уведомления: {TaskNotification.objects.count()}")
print(f"  • Отчёты о работах: {WorkReport.objects.count()}")
print(f"  • Комментарии: {WorkOrderComment.objects.count()}")
print(f"  • История статусов: {WorkOrderStatusHistory.objects.count()}")
print(f"  • Журнал работ: {WorkLog.objects.count()}")
print(f"  • Оценки работ: {WorkOrderRating.objects.count()}")
print(f"  • Шаблоны работ: {WorkTemplate.objects.count()}")
print(f"  • Поставщики: {Supplier.objects.count()}")
print(f"  • Заказы на поставку: {PurchaseOrder.objects.count()}")
print(f"  • Позиции заказов: {PurchaseOrderItem.objects.count()}")
print(f"  • Продажи: {Sale.objects.count()}")
print(f"  • Пользователи: {User.objects.count()}")
print("\nБаза данных готова к использованию! 🎉")
