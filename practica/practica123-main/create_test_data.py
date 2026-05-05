import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'practica.settings')
django.setup()

User = get_user_model()

# Данные для создания пользователей
users_data = [
    # Администраторы
    {'username': 'admin1', 'password': '123', 'role': 'admin', 'first_name': 'Алексей', 'last_name': 'Иванов'},
    {'username': 'admin2', 'password': '123', 'role': 'admin', 'first_name': 'Мария', 'last_name': 'Петрова'},
    
    # Инженеры
    {'username': 'engineer1', 'password': '123', 'role': 'engineer', 'first_name': 'Дмитрий', 'last_name': 'Сидоров'},
    {'username': 'engineer2', 'password': '123', 'role': 'engineer', 'first_name': 'Елена', 'last_name': 'Козлова'},
    {'username': 'engineer3', 'password': '123', 'role': 'engineer', 'first_name': 'Сергей', 'last_name': 'Новиков'},
    
    # Техники
    {'username': 'technician1', 'password': '123', 'role': 'technician', 'first_name': 'Андрей', 'last_name': 'Морозов'},
    {'username': 'technician2', 'password': '123', 'role': 'technician', 'first_name': 'Ольга', 'last_name': 'Волкова'},
    {'username': 'technician3', 'password': '123', 'role': 'technician', 'first_name': 'Павел', 'last_name': 'Лебедев'},
    {'username': 'technician4', 'password': '123', 'role': 'technician', 'first_name': 'Наталья', 'last_name': 'Соколова'},
    
    # Кладовщики
    {'username': 'storekeeper1', 'password': '123', 'role': 'storekeeper', 'first_name': 'Игорь', 'last_name': 'Попов'},
    {'username': 'storekeeper2', 'password': '123', 'role': 'storekeeper', 'first_name': 'Татьяна', 'last_name': 'Васильева'},
    
    # Практиканты
    {'username': 'intern1', 'password': '123', 'role': 'trainee', 'first_name': 'Максим', 'last_name': 'Кузнецов'},
    {'username': 'intern2', 'password': '123', 'role': 'trainee', 'first_name': 'Анна', 'last_name': 'Павлова'},
    {'username': 'intern3', 'password': '123', 'role': 'trainee', 'first_name': 'Кирилл', 'last_name': 'Смирнов'},
]

created_count = 0
for user_data in users_data:
    username = user_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        created_count += 1
        print(f"Создан пользователь: {username} ({user_data['role']})")
    else:
        print(f"Пользователь {username} уже существует")

print(f"\nВсего создано новых пользователей: {created_count}")
print("Тестовые данные готовы!")
