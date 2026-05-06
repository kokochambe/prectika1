import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maint_system.settings')
django.setup()

from accounts.models import User

# Создаём тестовых пользователей с единым паролем 'admin'
users_data = [
    ('admin_otir', 'admin', 'admin', 'Управление ОТК', '+79001112200'),
    ('eng_ivanov', 'admin', 'engineer', 'Механика', '+79001112201'),
    ('eng_petrov', 'admin', 'engineer', 'Электрика', '+79001112202'),
    ('tech_sidorov', 'admin', 'technician', 'Цех 1', '+79001112203'),
    ('tech_kuznetsov', 'admin', 'technician', 'Цех 2', '+79001112204'),
    ('tech_popov', 'admin', 'technician', 'Цех 1', '+79001112205'),
    ('store_morozov', 'admin', 'storekeeper', 'Склад A', '+79001112212'),
    ('store_novikov', 'admin', 'storekeeper', 'Склад B', '+79001112213'),
    ('trainee_smirnov', 'admin', 'trainee', 'Практика', '+79001112215'),
    ('trainee_fedorov', 'admin', 'trainee', 'Практика', '+79001112216'),
    ('seller_petrov', 'admin', 'seller', 'Отдел продаж', '+79001112220'),
]

for username, password, role, department, phone in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'role': role,
            'department': department,
            'phone': phone,
            'is_active': True,
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f'✅ Создан пользователь: {username} ({role})')
    else:
        # Обновляем пароль для существующих пользователей
        user.set_password(password)
        user.save()
        print(f'🔄 Обновлён пароль для: {username} ({role})')

print('\n🎉 Готово! Все пользователи созданы с паролем: admin')
print('💡 Логин для администратора: admin_otir / admin')
