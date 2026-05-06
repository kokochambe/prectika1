from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с ролями для системы ТОиР"""
    
    ROLE_CHOICES = [
        ('admin', 'Начальник ОТК / Администратор'),
        ('engineer', 'Специалист ОТиР'),
        ('technician', 'Рабочий / Слесарь-ремонтник'),
        ('storekeeper', 'Кладовщик'),
        ('trainee', 'Ученик / Практикант'),
        ('seller', 'Продавец'),
        ('client', 'Клиент'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Роль'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Отдел/Цех'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_engineer(self):
        return self.role == 'engineer'
    
    @property
    def is_technician(self):
        return self.role == 'technician'
    
    @property
    def is_storekeeper(self):
        return self.role == 'storekeeper'
    
    @property
    def is_trainee(self):
        return self.role == 'trainee'
    
    @property
    def is_seller(self):
        return self.role == 'seller'
    
    @property
    def is_client(self):
        return self.role == 'client'
