from django.contrib import admin
from .models import WorkOrder, WorkReport, TaskNotification


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment', 'order_type', 'priority', 'status', 'assigned_user', 'created_at']
    list_filter = ['status', 'order_type', 'priority']
    search_fields = ['equipment__inv_number', 'description']
    ordering = ['-created_at']
    raw_id_fields = ['equipment', 'assigned_user', 'created_by']


@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'worker', 'work_order', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['worker__username', 'work_order__equipment__inv_number', 'message']
    ordering = ['-created_at']
    raw_id_fields = ['worker', 'work_order', 'created_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkReport)
class WorkReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'work_order', 'report_date', 'hours_spent', 'technician_signature']
    list_filter = ['report_date']
    search_fields = ['work_order__equipment__inv_number']
