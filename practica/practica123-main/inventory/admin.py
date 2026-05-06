from django.contrib import admin
from .models import SparePart, PartRequest, InventoryTransaction, Supplier, PurchaseOrder, PurchaseOrderItem


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'unit_price', 'current_stock', 'min_stock', 'warehouse_location', 'is_low_stock']
    list_filter = ['category', 'warehouse_location', 'is_active']
    search_fields = ['sku', 'name', 'manufacturer']
    ordering = ['sku']


@admin.register(PartRequest)
class PartRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'work_order', 'spare_part', 'quantity_requested', 'quantity_issued', 'status', 'priority', 'requested_by']
    list_filter = ['status', 'priority']
    search_fields = ['work_order__equipment__inv_number', 'spare_part__sku']
    ordering = ['-created_at']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'spare_part', 'transaction_type', 'quantity', 'stock_before', 'stock_after', 'performed_by', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['spare_part__sku', 'spare_part__name']
    ordering = ['-created_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'rating', 'delivery_time_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'phone']
    ordering = ['name']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'expected_delivery_date', 'status', 'total_amount']
    list_filter = ['status']
    search_fields = ['order_number', 'supplier__name']
    ordering = ['-order_date']


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'spare_part', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price']
    list_filter = []
    search_fields = ['spare_part__sku', 'spare_part__name']
    ordering = ['-id']
