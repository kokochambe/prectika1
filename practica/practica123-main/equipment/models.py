from django.db import models
from django.conf import settings


class Equipment(models.Model):
    """Реестр оборудования"""
    
    STATUS_CHOICES = [
        ('active', 'В эксплуатации'),
        ('maintenance', 'На обслуживании'),
        ('out_of_service', 'Неисправно'),
        ('decommissioned', 'Списано'),
    ]
    
    TYPE_CHOICES = [
        ('Насосы', 'Насосы'),
        ('Компрессоры', 'Компрессоры'),
        ('Электропривод', 'Электропривод'),
        ('Механика', 'Механика'),
        ('Вентиляция', 'Вентиляция'),
        ('Транспорт', 'Транспорт'),
        ('Металлообработка', 'Металлообработка'),
        ('Энергетика', 'Энергетика'),
        ('Электрика', 'Электрика'),
        ('Автоматика', 'Автоматика'),
    ]
    
    CRITICALITY_CHOICES = [
        (1, 'Критическое'),
        (2, 'Важное'),
        (3, 'Стандартное'),
        (4, 'Вспомогательное'),
    ]
    
    inv_number = models.CharField(max_length=30, unique=True, verbose_name='Инвентарный номер')
    name = models.CharField(max_length=200, verbose_name='Наименование')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Тип оборудования')
    workshop = models.CharField(max_length=50, verbose_name='Цех/Участок')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    install_date = models.DateField(null=True, blank=True, verbose_name='Дата установки')
    warranty_until = models.DateField(null=True, blank=True, verbose_name='Гарантия до')
    last_maintenance = models.DateField(null=True, blank=True, verbose_name='Последнее ТО')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    manufacturer = models.CharField(max_length=200, blank=True, null=True, verbose_name='Производитель')
    model = models.CharField(max_length=100, blank=True, null=True, verbose_name='Модель')
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Серийный номер')
    criticality = models.IntegerField(choices=CRITICALITY_CHOICES, default=3, verbose_name='Критичность')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Цена покупки')
    replacement_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Стоимость замены')
    expected_lifetime_years = models.PositiveIntegerField(null=True, blank=True, verbose_name='Срок службы (лет)')
    location_details = models.CharField(max_length=200, blank=True, null=True, verbose_name='Детали расположения')
    technical_specs = models.TextField(blank=True, null=True, verbose_name='Технические характеристики')
    manual_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на руководство')
    parent_equipment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_equipment', verbose_name='Родительское оборудование')
    qr_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='QR-код')
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name='Штрих-код')
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='responsible_equipment', verbose_name='Ответственный')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    
    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['inv_number']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['type']),
            models.Index(fields=['criticality']),
            models.Index(fields=['workshop']),
        ]
    
    def __str__(self):
        return f"{self.inv_number} - {self.name}"
    
    @property
    def is_warranty_valid(self):
        if self.warranty_until:
            from datetime import date
            return self.warranty_until >= date.today()
        return False
    
    @property
    def age_years(self):
        if self.install_date:
            from datetime import date
            return (date.today() - self.install_date).days / 365.25
        return None


class MaintenanceSchedule(models.Model):
    """График технического обслуживания"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('quarterly', 'Ежеквартально'),
        ('semi_annual', 'Полугодово'),
        ('annual', 'Ежегодно'),
        ('custom', 'По наработке'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='schedules', verbose_name='Оборудование')
    frequency_days = models.PositiveIntegerField(verbose_name='Периодичность (дней)')
    frequency_type = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly', verbose_name='Тип периодичности')
    next_due = models.DateField(verbose_name='Следующее ТО')
    last_completed = models.DateField(null=True, blank=True, verbose_name='Последнее выполненное')
    checklist = models.TextField(default='Проверка масла, натяжение, очистка фильтров, смазка, замер вибрации', verbose_name='Чек-лист')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    estimated_duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, verbose_name='Плановая длительность (час)')
    required_specialists = models.CharField(max_length=200, blank=True, null=True, verbose_name='Требуемые специалисты')
    required_parts = models.TextField(blank=True, null=True, verbose_name='Необходимые запчасти')
    safety_requirements = models.TextField(blank=True, null=True, verbose_name='Требования безопасности')
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Плановая стоимость')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'График ТО'
        verbose_name_plural = 'Графики ТО'
        ordering = ['next_due']
        indexes = [
            models.Index(fields=['next_due']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"График для {self.equipment.inv_number}"
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.next_due < date.today() and self.is_active
    
    @property
    def days_until_due(self):
        from datetime import date
        if self.next_due:
            return (self.next_due - date.today()).days
        return None


class EquipmentFailure(models.Model):
    """Журнал отказов оборудования"""
    
    FAILURE_TYPE_CHOICES = [
        ('mechanical', 'Механический'),
        ('electrical', 'Электрический'),
        ('hydraulic', 'Гидравлический'),
        ('pneumatic', 'Пневматический'),
        ('software', 'Программный'),
        ('operator_error', 'Ошибка оператора'),
        ('wear_out', 'Износ'),
        ('other', 'Другое'),
    ]
    
    SEVERITY_CHOICES = [
        (1, 'Критический'),
        (2, 'Высокий'),
        (3, 'Средний'),
        (4, 'Низкий'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='failures', verbose_name='Оборудование')
    failure_date = models.DateTimeField(verbose_name='Дата отказа')
    failure_type = models.CharField(max_length=20, choices=FAILURE_TYPE_CHOICES, verbose_name='Тип отказа')
    severity = models.IntegerField(choices=SEVERITY_CHOICES, verbose_name='Серьёзность')
    description = models.TextField(verbose_name='Описание отказа')
    root_cause = models.TextField(blank=True, null=True, verbose_name='Причина отказа')
    corrective_action = models.TextField(blank=True, null=True, verbose_name='Предпринятые действия')
    downtime_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='Время простоя (час)')
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стоимость ремонта')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reported_failures', verbose_name='Сообщил')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_failures', verbose_name='Устранил')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата устранения')
    work_order = models.ForeignKey('workorders.WorkOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_failures', verbose_name='Наряд-заказ')
    photos = models.JSONField(blank=True, null=True, verbose_name='Фотоотчёт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отказ оборудования'
        verbose_name_plural = 'Отказы оборудования'
        ordering = ['-failure_date']
        indexes = [
            models.Index(fields=['failure_date']),
            models.Index(fields=['severity']),
            models.Index(fields=['equipment', 'failure_date']),
        ]
    
    def __str__(self):
        return f"Отказ {self.equipment.inv_number} ({self.get_failure_type_display()})"


class EquipmentMeterReading(models.Model):
    """Показания счётчиков оборудования (наработка)"""
    
    READING_TYPE_CHOICES = [
        ('hours', 'Моточасы'),
        ('cycles', 'Циклы'),
        ('kilometers', 'Километры'),
        ('units', 'Единицы продукции'),
        ('pressure', 'Давление'),
        ('temperature', 'Температура'),
        ('vibration', 'Вибрация'),
        ('other', 'Другое'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='meter_readings', verbose_name='Оборудование')
    reading_type = models.CharField(max_length=20, choices=READING_TYPE_CHOICES, verbose_name='Тип показания')
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Значение')
    unit = models.CharField(max_length=20, default='', verbose_name='Единица измерения')
    reading_date = models.DateTimeField(verbose_name='Дата показания')
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Снял')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Показание счётчика'
        verbose_name_plural = 'Показания счётчиков'
        ordering = ['-reading_date']
        indexes = [
            models.Index(fields=['equipment', 'reading_date']),
            models.Index(fields=['reading_type']),
        ]
    
    def __str__(self):
        return f"{self.equipment.inv_number} - {self.reading_type}: {self.value} {self.unit}"


class EquipmentDocument(models.Model):
    """Документация оборудования"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('manual', 'Руководство'),
        ('passport', 'Паспорт'),
        ('certificate', 'Сертификат'),
        ('diagram', 'Схема'),
        ('specification', 'Спецификация'),
        ('protocol', 'Протокол'),
        ('act', 'Акт'),
        ('other', 'Другое'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='documents', verbose_name='Оборудование')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name='Тип документа')
    title = models.CharField(max_length=200, verbose_name='Название')
    file = models.FileField(upload_to='equipment_docs/%Y/%m/%d/', verbose_name='Файл')
    file_size = models.PositiveIntegerField(help_text='Размер в байтах', verbose_name='Размер файла')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Загрузил')
    version = models.CharField(max_length=20, blank=True, null=True, verbose_name='Версия')
    is_current = models.BooleanField(default=True, verbose_name='Актуальная версия')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    
    class Meta:
        verbose_name = 'Документ оборудования'
        verbose_name_plural = 'Документы оборудования'
        ordering = ['equipment', '-upload_date']
    
    def __str__(self):
        return f"{self.document_type} для {self.equipment.inv_number}"


class EquipmentChangeLog(models.Model):
    """Журнал изменений оборудования"""
    
    CHANGE_TYPE_CHOICES = [
        ('status', 'Изменение статуса'),
        ('location', 'Изменение места'),
        ('assignment', 'Изменение ответственного'),
        ('modification', 'Модификация'),
        ('repair', 'Ремонт'),
        ('inspection', 'Инспекция'),
        ('other', 'Другое'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='change_logs', verbose_name='Оборудование')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES, verbose_name='Тип изменения')
    old_value = models.TextField(blank=True, null=True, verbose_name='Старое значение')
    new_value = models.TextField(blank=True, null=True, verbose_name='Новое значение')
    description = models.TextField(verbose_name='Описание изменения')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Изменил')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    
    class Meta:
        verbose_name = 'Запись журнала изменений'
        verbose_name_plural = 'Журнал изменений'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.change_type} для {self.equipment.inv_number}"
