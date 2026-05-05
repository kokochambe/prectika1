#!/usr/bin/env python
"""
Скрипт для создания тестовых данных
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maint_system.settings')
django.setup()

from accounts.models import User
from equipment.models import Equipment, MaintenanceSchedule
from workorders.models import WorkOrder, WorkReport
from inventory.models import SparePart, PartRequest
from datetime import date, timedelta
import random

def create_test_data():
    print("🗑️  Очистка старых данных...")
    
    # Очистка в правильном порядке (сначала зависимые таблицы)
    PartRequest.objects.all().delete()
    WorkReport.objects.all().delete()
    WorkOrder.objects.all().delete()
    MaintenanceSchedule.objects.all().delete()
    SparePart.objects.all().delete()
    Equipment.objects.all().delete()
    User.objects.all().delete()
    
    print("✅ Очистка завершена")
    
    # Создание пользователей
    print("\n👥 Создание пользователей...")
    users_data = [
        ('admin_otir', 'admin123', 'Алексей', 'Иванов', 'admin', 'Отдел ТОиР'),
        ('eng_ivanov', 'engineer123', 'Дмитрий', 'Сидоров', 'engineer', 'Цех 1'),
        ('tech_sidorov', 'tech123', 'Андрей', 'Морозов', 'technician', 'Цех 1'),
        ('store_morozov', 'store123', 'Игорь', 'Попов', 'storekeeper', 'Склад №1'),
        ('trainee_smirnov', 'trainee123', 'Максим', 'Кузнецов', 'trainee', 'Цех 1'),
        ('seller_petrov', 'seller123', 'Елена', 'Петрова', 'seller', 'Отдел продаж'),
    ]
    
    created_users = {}
    for username, password, first_name, last_name, role, department in users_data:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
            email=f'{username}@company.com'
        )
        created_users[username] = user
        print(f"   ✓ {username} ({first_name} {last_name})")
    
    print(f"\n✅ Создано {len(created_users)} пользователей")
    
    # Создание оборудования
    print("\n⚙️  Создание оборудования...")
    equipment_data = [
        ('EQ-001', 'Станок ЧПУ-1', 'Металлообработка', 'Цех 1', 'active', '2022-03-15'),
        ('EQ-002', 'Пресс гидравлический P-200', 'Механика', 'Цех 2', 'active', '2021-06-20'),
        ('EQ-003', 'Конвейерная линия КЛ-500', 'Транспорт', 'Цех 3', 'maintenance', '2020-09-10'),
        ('EQ-004', 'Робот-манипулятор R-100', 'Автоматика', 'Цех 1', 'active', '2023-01-25'),
        ('EQ-005', 'Генератор дизельный ГД-500', 'Энергетика', 'Энергоцех', 'active', '2019-11-05'),
        ('EQ-006', 'Компрессор воздушный КВ-300', 'Компрессоры', 'Цех 2', 'active', '2022-07-18'),
        ('EQ-007', 'Токарный станок Т-500', 'Металлообработка', 'Цех 1', 'active', '2018-04-22'),
        ('EQ-008', 'Фрезерный станок Ф-300', 'Металлообработка', 'Цех 2', 'out_of_service', '2017-08-30'),
        ('EQ-009', 'Вентилятор промышленный ВП-800', 'Вентиляция', 'Цех 3', 'active', '2021-12-14'),
        ('EQ-010', 'Насос циркуляционный НЦ-150', 'Насосы', 'Энергоцех', 'active', '2023-05-08'),
        ('EQ-011', 'Электропривод ЭП-250', 'Электропривод', 'Цех 1', 'active', '2022-10-03'),
        ('EQ-012', 'Щит управления ЩУ-1', 'Электрика', 'Энергоцех', 'active', '2020-02-28'),
    ]
    
    created_equipment = []
    for inv_number, name, eq_type, workshop, status, install_date in equipment_data:
        eq = Equipment.objects.create(
            inv_number=inv_number,
            name=name,
            type=eq_type,
            workshop=workshop,
            status=status,
            install_date=install_date,
            warranty_until='2025-12-31',
            last_maintenance=(date.today() - timedelta(days=random.randint(10, 60))).isoformat()
        )
        created_equipment.append(eq)
        print(f"   ✓ {inv_number} - {name}")
    
    print(f"\n✅ Создано {len(created_equipment)} единиц оборудования")
    
    # Создание графиков ТО
    print("\n📅 Создание графиков ТО...")
    for i, eq in enumerate(created_equipment[:6]):
        MaintenanceSchedule.objects.create(
            equipment=eq,
            frequency_days=30 if i % 2 == 0 else 90,
            next_due=(date.today() + timedelta(days=random.randint(5, 30))).isoformat(),
            checklist='Проверка масла, натяжение ремней, очистка фильтров, смазка узлов, замер вибрации'
        )
    print(f"✅ Создано {MaintenanceSchedule.objects.count()} графиков ТО")
    
    # Создание запчастей
    print("\n🔧 Создание запчастей...")
    spare_parts_data = [
        ('SP-001', 'Подшипник 205', 'Подшипники', 150.00, 10, 45, 'Стеллаж А-1'),
        ('SP-002', 'Подшипник 305', 'Подшипники', 280.00, 5, 20, 'Стеллаж А-1'),
        ('SP-003', 'Ремень приводной А-50', 'Ремни', 450.00, 8, 25, 'Стеллаж Б-2'),
        ('SP-004', 'Фильтр масляный ФМ-100', 'Фильтры', 320.00, 15, 60, 'Стеллаж В-3'),
        ('SP-005', 'Фильтр воздушный ФВ-200', 'Фильтры', 180.00, 20, 80, 'Стеллаж В-3'),
        ('SP-006', 'Сальник 40х60', 'Уплотнения', 85.00, 30, 150, 'Стеллаж Г-1'),
        ('SP-007', 'Болт М12х80', 'Крепеж', 25.00, 100, 500, 'Стеллаж Д-4'),
        ('SP-008', 'Гайка М12', 'Крепеж', 15.00, 200, 800, 'Стеллаж Д-4'),
        ('SP-009', 'Масло моторное 5W-40', 'ГСМ', 850.00, 10, 35, 'Зона ГСМ'),
        ('SP-010', 'Смазка Литол-24', 'ГСМ', 420.00, 15, 40, 'Зона ГСМ'),
        ('SP-011', 'Электроды сварочные 3мм', 'Расходники', 550.00, 5, 18, 'Стеллаж Е-2'),
        ('SP-012', 'Щетка электродвигателя', 'Электро', 190.00, 12, 30, 'Стеллаж Ж-1'),
    ]
    
    for sku, name, category, price, min_stock, current_stock, location in spare_parts_data:
        SparePart.objects.create(
            sku=sku,
            name=name,
            category=category,
            unit_price=price,
            min_stock=min_stock,
            current_stock=current_stock,
            warehouse_location=location
        )
        print(f"   ✓ {sku} - {name}")
    
    print(f"\n✅ Создано {SparePart.objects.count()} запчастей")
    
    # Создание нарядов-заданий
    print("\n📋 Создание нарядов-заданий...")
    work_orders_data = [
        ('planned', 3, 'in_progress', 'technician1', 'Плановое ТО станка ЧПУ-1', 'Замена масла, проверка натяжения ремней, смазка направляющих'),
        ('emergency', 1, 'new', 'technician2', 'Срочный ремонт конвейера', 'Замена порванного приводного ремня, регулировка натяжения'),
        ('planned', 2, 'assigned', 'technician3', 'ТО робота-манипулятора', 'Диагностика сенсоров, калибровка осей, обновление ПО'),
        ('inspection', 4, 'completed', 'technician4', 'Инспекция генератора', 'Проверка уровня топлива, замена фильтров, тест под нагрузкой'),
        ('modernization', 2, 'pending_parts', 'engineer1', 'Модернизация системы управления', 'Установка нового контроллера, прокладка кабелей'),
        ('planned', 3, 'new', 'technician1', 'ТО компрессора', 'Замена воздушных фильтров, проверка давления, смазка'),
        ('emergency', 1, 'in_progress', 'technician2', 'Ремонт насоса', 'Замена уплотнений, балансировка крыльчатки'),
        ('planned', 4, 'assigned', 'technician3', 'Обслуживание вентилятора', 'Очистка лопастей, проверка подшипников, смазка'),
    ]
    
    for order_type, priority, status, technician, title, description in work_orders_data:
        eq = random.choice(created_equipment)
        WorkOrder.objects.create(
            equipment=eq,
            order_type=order_type,
            priority=priority,
            status=status,
            assigned_user=created_users.get(technician),
            created_by=random.choice([created_users['admin_otir'], created_users['eng_ivanov']]),
            description=description,
            started_at=(date.today() - timedelta(days=random.randint(1, 5))).isoformat() if status in ['in_progress', 'completed'] else None,
            completed_at=(date.today() - timedelta(days=1)).isoformat() if status == 'completed' else None,
        )
        print(f"   ✓ Наряд #{WorkOrder.objects.latest('id').id} - {title}")
    
    print(f"\n✅ Создано {WorkOrder.objects.count()} нарядов-заданий")
    
    # Создание отчетов о работах
    print("\n📝 Создание отчетов о работах...")
    completed_orders = WorkOrder.objects.filter(status='completed')
    for order in completed_orders:
        WorkReport.objects.create(
            work_order=order,
            report_date=date.today().isoformat(),
            hours_spent=round(random.uniform(2.0, 8.0), 1),
            description='Работы выполнены согласно регламенту. Оборудование протестировано и запущено в эксплуатацию.',
            technician_signature=f'{order.assigned_user.first_name} {order.assigned_user.last_name}' if order.assigned_user else ''
        )
    
    # Добавим отчеты для некоторых нарядов в работе
    in_progress_orders = WorkOrder.objects.filter(status='in_progress')[:2]
    for order in in_progress_orders:
        WorkReport.objects.create(
            work_order=order,
            report_date=(date.today() - timedelta(days=1)).isoformat(),
            hours_spent=round(random.uniform(1.0, 4.0), 1),
            description='Работы находятся в стадии выполнения. Основные узлы проверены.',
            technician_signature=f'{order.assigned_user.first_name} {order.assigned_user.last_name}' if order.assigned_user else ''
        )
    
    print(f"✅ Создано {WorkReport.objects.count()} отчетов о работах")
    
    # Создание заявок на запчасти
    print("\n📦 Создание заявок на запчасти...")
    spare_parts = list(SparePart.objects.all())
    work_orders_list = list(WorkOrder.objects.all())
    
    requests_data = [
        (work_orders_list[0], spare_parts[3], 2, 'approved', 'tech_sidorov', 'store_morozov'),
        (work_orders_list[1], spare_parts[2], 1, 'issued', 'tech_sidorov', 'store_morozov'),
        (work_orders_list[2], spare_parts[11], 4, 'requested', 'tech_sidorov', None),
        (work_orders_list[4], spare_parts[0], 6, 'approved', 'eng_ivanov', 'store_morozov'),
        (work_orders_list[6], spare_parts[5], 3, 'issued', 'tech_sidorov', 'store_morozov'),
    ]
    
    for work_order, part, qty, status, requester, fulfiller in requests_data:
        req = PartRequest.objects.create(
            work_order=work_order,
            spare_part=part,
            quantity=qty,
            status=status,
            requested_by=created_users.get(requester),
        )
        if fulfiller and status == 'issued':
            req.fulfilled_by = created_users.get(fulfiller)
            req.fulfilled_at = (date.today() - timedelta(days=1)).isoformat()
            req.save()
        print(f"   ✓ Заявка #{req.id} - {part.name} ({qty} шт.)")
    
    print(f"\n✅ Создано {PartRequest.objects.count()} заявок на запчасти")
    
    # Итоговая статистика
    print("\n" + "="*50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("="*50)
    print(f"👥 Пользователей: {User.objects.count()}")
    print(f"⚙️  Оборудования: {Equipment.objects.count()}")
    print(f"📅 Графиков ТО: {MaintenanceSchedule.objects.count()}")
    print(f"🔧 Запчастей: {SparePart.objects.count()}")
    print(f"📋 Нарядов-заданий: {WorkOrder.objects.count()}")
    print(f"📝 Отчетов о работах: {WorkReport.objects.count()}")
    print(f"📦 Заявок на запчасти: {PartRequest.objects.count()}")
    print("="*50)
    print("\n✅ Все тестовые данные успешно созданы!")
    print("\n🔐 Данные для входа:")
    print("   Логин: admin1, пароль: password123 (Администратор)")
    print("   Логин: engineer1, пароль: password123 (Инженер)")
    print("   Логин: technician1, пароль: password123 (Техник)")
    print("   Логин: storekeeper1, пароль: password123 (Кладовщик)")
    print("   Логин: intern1, пароль: password123 (Практикант)")
    print("="*50)

if __name__ == '__main__':
    create_test_data()
