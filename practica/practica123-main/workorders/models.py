from django.db import models
from django.conf import settings


class WorkOrder(models.Model):
    """Наряд-заказ на техническое обслуживание и ремонт"""
    
    ORDER_TYPE_CHOICES = [
        ('planned', 'Плановое ТО'),
        ('emergency', 'Аварийный ремонт'),
        ('modernization', 'Модернизация'),
        ('inspection', 'Инспекция'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('assigned', 'Назначен'),
        ('in_progress', 'В работе'),
        ('pending_parts', 'Ожидание запчастей'),
        ('completed', 'Выполнен'),
        ('rejected', 'Отклонен'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Критический'),
        (2, 'Высокий'),
        (3, 'Средний'),
        (4, 'Низкий'),
        (5, 'Отложенный'),
    ]
    
    equipment = models.ForeignKey('equipment.Equipment', on_delete=models.CASCADE, related_name='work_orders', verbose_name='Оборудование')
    order_type = models.CharField(max_length=30, choices=ORDER_TYPE_CHOICES, verbose_name='Тип работ')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3, verbose_name='Приоритет')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_work_orders', verbose_name='Исполнитель')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_work_orders', verbose_name='Создал')
    description = models.TextField(default='Техническое обслуживание / устранение неисправности', verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начало работ')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершение работ')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='Плановые часы')
    actual_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='Фактические часы')
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Плановая стоимость')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Фактическая стоимость')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='Место выполнения')
    safety_measures = models.TextField(blank=True, null=True, verbose_name='Меры безопасности')
    completion_notes = models.TextField(blank=True, null=True, verbose_name='Комментарий о завершении')
    
    class Meta:
        verbose_name = 'Наряд-заказ'
        verbose_name_plural = 'Наряды-заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_user']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Наряд #{self.id} - {self.equipment.inv_number}"


class TaskNotification(models.Model):
    """Уведомления о задачах для работников"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('read', 'Прочитано'),
        ('accepted', 'Взято в работу'),
        ('in_progress', 'Выполняется'),
        ('done', 'Выполнено'),
    ]
    
    NOTIFICATION_TYPE_CHOICES = [
        ('task', 'Задание'),
        ('message', 'Сообщение'),
        ('alert', 'Предупреждение'),
        ('reminder', 'Напоминание'),
    ]
    
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='Работник')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='notifications', verbose_name='Наряд-заказ')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='task', verbose_name='Тип уведомления')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_notifications', verbose_name='Отправил')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата прочтения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Уведомление о задаче'
        verbose_name_plural = 'Уведомления о задачах'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['worker', 'is_read']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Уведомление #{self.id} для {self.worker.username}"


class WorkReport(models.Model):
    """Отчёт о выполненных работах"""
    
    QUALITY_CHOICES = [
        (1, 'Неудовлетворительно'),
        (2, 'Плохо'),
        (3, 'Удовлетворительно'),
        (4, 'Хорошо'),
        (5, 'Отлично'),
    ]
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='reports', verbose_name='Наряд-заказ')
    report_date = models.DateField(verbose_name='Дата отчёта')
    hours_spent = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Затрачено часов')
    description = models.TextField(default='Работы выполнены по регламенту. Замечаний нет.', verbose_name='Описание работ')
    technician_signature = models.CharField(max_length=100, blank=True, null=True, verbose_name='Подпись исполнителя')
    quality_rating = models.IntegerField(choices=QUALITY_CHOICES, default=3, verbose_name='Оценка качества')
    parts_used = models.TextField(blank=True, null=True, verbose_name='Использованные запчасти')
    issues_found = models.TextField(blank=True, null=True, verbose_name='Выявленные проблемы')
    recommendations = models.TextField(blank=True, null=True, verbose_name='Рекомендации')
    photos = models.JSONField(blank=True, null=True, verbose_name='Фотоотчёт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отчёт о работах'
        verbose_name_plural = 'Отчёты о работах'
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Отчёт для наряда #{self.work_order.id}"


class WorkOrderComment(models.Model):
    """Комментарии к нарядам-заказам"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='comments', verbose_name='Наряд-заказ')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_order_comments', verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='Ответ на комментарий')
    is_edited = models.BooleanField(default=False, verbose_name='Изменён')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['work_order', 'created_at']),
        ]
    
    def __str__(self):
        return f"Комментарий #{self.id} к наряду #{self.work_order.id}"


class WorkOrderStatusHistory(models.Model):
    """История изменений статусов нарядов-заказов"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='status_history', verbose_name='Наряд-заказ')
    old_status = models.CharField(max_length=20, verbose_name='Старый статус')
    new_status = models.CharField(max_length=20, verbose_name='Новый статус')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Изменил')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий к изменению')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    
    class Meta:
        verbose_name = 'История статуса'
        verbose_name_plural = 'Истории статусов'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.old_status} → {self.new_status} (наряд #{self.work_order.id})"


class WorkAttachment(models.Model):
    """Вложения к нарядам-заказам (документы, фото)"""
    
    ATTACHMENT_TYPE_CHOICES = [
        ('photo', 'Фотография'),
        ('document', 'Документ'),
        ('diagram', 'Схема'),
        ('manual', 'Руководство'),
        ('act', 'Акт'),
        ('other', 'Другое'),
    ]
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='attachments', verbose_name='Наряд-заказ')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Загрузил')
    file = models.FileField(upload_to='work_attachments/%Y/%m/%d/', verbose_name='Файл')
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPE_CHOICES, default='other', verbose_name='Тип вложения')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Описание')
    file_size = models.PositiveIntegerField(help_text='Размер в байтах', verbose_name='Размер файла')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Вложение #{self.id} к наряду #{self.work_order.id}"


class WorkLog(models.Model):
    """Журнал работ по наряду-заказу"""
    
    LOG_TYPE_CHOICES = [
        ('start', 'Начало работы'),
        ('pause', 'Пауза'),
        ('resume', 'Возобновление'),
        ('complete', 'Завершение этапа'),
        ('note', 'Заметка'),
        ('issue', 'Проблема'),
    ]
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='work_logs', verbose_name='Наряд-заказ')
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Техник')
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, verbose_name='Тип записи')
    description = models.TextField(verbose_name='Описание')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='Начало')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Окончание')
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name='Длительность (мин)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Запись журнала работ'
        verbose_name_plural = 'Журнал работ'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Запись #{self.id} ({self.get_log_type_display()})"


class WorkOrderRating(models.Model):
    """Оценка качества выполненной работы"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='ratings', verbose_name='Наряд-заказ')
    rated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Оценивший')
    quality_score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оценка качества')
    timeliness_score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оценка своевременности')
    professionalism_score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оценка профессионализма')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    
    class Meta:
        verbose_name = 'Оценка работы'
        verbose_name_plural = 'Оценки работ'
        unique_together = ['work_order', 'rated_by']
    
    def __str__(self):
        return f"Оценка наряда #{self.work_order.id} от {self.rated_by.username}"


class WorkTemplate(models.Model):
    """Шаблоны типовых работ"""
    
    name = models.CharField(max_length=200, verbose_name='Название шаблона')
    description = models.TextField(verbose_name='Описание')
    equipment_type = models.CharField(max_length=50, verbose_name='Тип оборудования')
    checklist = models.TextField(default='', verbose_name='Чек-лист работ')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=1.0, verbose_name='Плановые часы')
    required_parts = models.TextField(blank=True, null=True, verbose_name='Необходимые запчасти')
    safety_requirements = models.TextField(blank=True, null=True, verbose_name='Требования безопасности')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Шаблон работ'
        verbose_name_plural = 'Шаблоны работ'
        ordering = ['name']
    
    def __str__(self):
        return self.name
