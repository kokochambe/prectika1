from django.db import models
from accounts.models import User
from equipment.models import Equipment
from inventory.models import SparePart


class Sale(models.Model):
    """Модель продажи товаров или услуг"""
    
    SALE_TYPE_CHOICES = [
        ('equipment', 'Оборудование'),
        ('spare_part', 'Запчасть'),
        ('service', 'Услуга'),
    ]
    
    sale_type = models.CharField(
        max_length=20,
        choices=SALE_TYPE_CHOICES,
        verbose_name='Тип продажи'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оборудование'
    )
    spare_part = models.ForeignKey(
        SparePart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Запчасть'
    )
    service_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Название услуги'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Общая сумма'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Продавец'
    )
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Клиент'
    )
    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон клиента'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата продажи'
    )
    
    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.sale_type == 'equipment' and self.equipment:
            return f"Продажа оборудования {self.equipment.inv_number} - {self.total_amount} руб."
        elif self.sale_type == 'spare_part' and self.spare_part:
            return f"Продажа запчасти {self.spare_part.name} x{self.quantity} - {self.total_amount} руб."
        elif self.sale_type == 'service':
            return f"Продажа услуги {self.service_name} - {self.total_amount} руб."
        return f"Продажа #{self.id}"
    
    def save(self, *args, **kwargs):
        # Автоматический расчет общей суммы
        self.total_amount = self.price * self.quantity
        super().save(*args, **kwargs)
