from django.db import models
from django.conf import settings


class SparePart(models.Model):
    """Справочник запчастей и материалов"""
    
    CATEGORY_CHOICES = [
        ('bearings', 'Подшипники'),
        ('seals', 'Уплотнения'),
        ('filters', 'Фильтры'),
        ('belts', 'Ремни'),
        ('electrical', 'Электрика'),
        ('hydraulic', 'Гидравлика'),
        ('pneumatic', 'Пневматика'),
        ('fasteners', 'Крепёж'),
        ('lubricants', 'Смазочные материалы'),
        ('tools', 'Инструмент'),
        ('other', 'Другое'),
    ]
    
    UNIT_CHOICES = [
        ('pcs', 'шт'),
        ('kg', 'кг'),
        ('l', 'л'),
        ('m', 'м'),
        ('set', 'комплект'),
        ('box', 'коробка'),
    ]
    
    sku = models.CharField(max_length=30, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=200, verbose_name='Наименование')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', verbose_name='Категория')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена за ед.')
    min_stock = models.PositiveIntegerField(default=5, verbose_name='Мин. остаток')
    current_stock = models.PositiveIntegerField(default=0, verbose_name='Текущий остаток')
    reserved_stock = models.PositiveIntegerField(default=0, verbose_name='Зарезервировано')
    warehouse_location = models.CharField(max_length=30, blank=True, null=True, verbose_name='Место на складе')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    supplier = models.CharField(max_length=200, blank=True, null=True, verbose_name='Поставщик')
    manufacturer = models.CharField(max_length=200, blank=True, null=True, verbose_name='Производитель')
    lead_time_days = models.PositiveIntegerField(default=7, verbose_name='Срок поставки (дней)')
    reorder_quantity = models.PositiveIntegerField(default=10, verbose_name='Количество для заказа')
    last_purchase_date = models.DateField(null=True, blank=True, verbose_name='Дата последней закупки')
    last_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена последней закупки')
    compatible_equipment = models.ManyToManyField('equipment.Equipment', blank=True, related_name='compatible_parts', verbose_name='Совместимое оборудование')
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name='Штрих-код')
    photo = models.ImageField(upload_to='spare_parts/%Y/%m/%d/', blank=True, null=True, verbose_name='Фото')
    datasheet = models.FileField(upload_to='spare_parts_docs/%Y/%m/%d/', blank=True, null=True, verbose_name='Спецификация')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Запчасть'
        verbose_name_plural = 'Запчасти'
        ordering = ['sku']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['current_stock']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock
    
    @property
    def available_stock(self):
        return self.current_stock - self.reserved_stock
    
    @property
    def total_value(self):
        return self.current_stock * self.unit_price


class PartRequest(models.Model):
    """Заявка на выдачу запчастей"""
    
    STATUS_CHOICES = [
        ('requested', 'Запрошено'),
        ('approved', 'Утверждено'),
        ('issued', 'Выдано'),
        ('rejected', 'Отклонено'),
        ('partially_issued', 'Частично выдано'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Срочно'),
        (2, 'Высокий'),
        (3, 'Обычный'),
        (4, 'Низкий'),
    ]
    
    work_order = models.ForeignKey('workorders.WorkOrder', on_delete=models.CASCADE, related_name='part_requests', verbose_name='Наряд-заказ')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='requests', verbose_name='Запчасть')
    quantity_requested = models.PositiveIntegerField(verbose_name='Запрошено')
    quantity_issued = models.PositiveIntegerField(default=0, verbose_name='Выдано')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested', verbose_name='Статус')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3, verbose_name='Приоритет')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requested_parts', verbose_name='Запросил')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_parts', verbose_name='Утвердил')
    fulfilled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfilled_parts', verbose_name='Выдал')
    fulfilled_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выдачи')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='Причина отказа')
    notes = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заявка на запчасти'
        verbose_name_plural = 'Заявки на запчасти'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Заявка #{self.id} для наряда #{self.work_order.id}"


class InventoryTransaction(models.Model):
    """Журнал движения запасных частей"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('receipt', 'Приход'),
        ('issue', 'Расход'),
        ('adjustment', 'Корректировка'),
        ('return', 'Возврат'),
        ('write_off', 'Списание'),
        ('transfer', 'Перемещение'),
    ]
    
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='transactions', verbose_name='Запчасть')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='Тип операции')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена за ед.')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Общая сумма')
    stock_before = models.PositiveIntegerField(verbose_name='Остаток до')
    stock_after = models.PositiveIntegerField(verbose_name='Остаток после')
    reference_document = models.CharField(max_length=100, blank=True, null=True, verbose_name='Документ основание')
    related_request = models.ForeignKey(PartRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Заявка')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Выполнил')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Операция с запчастями'
        verbose_name_plural = 'Операции с запчастями'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['spare_part', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} #{self.id} - {self.spare_part.name}"


class Supplier(models.Model):
    """Поставщики запчастей"""
    
    name = models.CharField(max_length=200, verbose_name='Название')
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name='Контактное лицо')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    address = models.TextField(blank=True, null=True, verbose_name='Адрес')
    website = models.URLField(blank=True, null=True, verbose_name='Сайт')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3, verbose_name='Рейтинг')
    payment_terms = models.CharField(max_length=200, blank=True, null=True, verbose_name='Условия оплаты')
    delivery_time_days = models.PositiveIntegerField(default=7, verbose_name='Срок поставки (дней)')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Заказ на поставку запчастей"""
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('sent', 'Отправлен'),
        ('confirmed', 'Подтверждён'),
        ('partial', 'Частично получен'),
        ('received', 'Получен'),
        ('cancelled', 'Отменён'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders', verbose_name='Поставщик')
    order_number = models.CharField(max_length=50, unique=True, verbose_name='Номер заказа')
    order_date = models.DateField(verbose_name='Дата заказа')
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name='Ожидаемая дата доставки')
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name='Фактическая дата доставки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая сумма')
    notes = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заказ на поставку'
        verbose_name_plural = 'Заказы на поставку'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Заказ #{self.order_number} от {self.order_date}"


class PurchaseOrderItem(models.Model):
    """Позиции заказа на поставку"""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, verbose_name='Запчасть')
    quantity_ordered = models.PositiveIntegerField(verbose_name='Заказано')
    quantity_received = models.PositiveIntegerField(default=0, verbose_name='Получено')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за ед.')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Общая стоимость')
    received_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата получения')
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
    
    def __str__(self):
        return f"{self.spare_part.name} x{self.quantity_ordered}"
