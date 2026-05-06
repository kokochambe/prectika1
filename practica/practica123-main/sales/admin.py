from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_type', 'get_item_name', 'quantity', 'price', 'total_amount', 'seller', 'created_at')
    list_filter = ('sale_type', 'seller', 'created_at')
    search_fields = ('customer_name', 'notes')
    readonly_fields = ('total_amount', 'created_at')
    
    def get_item_name(self, obj):
        if obj.sale_type == 'equipment' and obj.equipment:
            return obj.equipment.name
        elif obj.sale_type == 'spare_part' and obj.spare_part:
            return obj.spare_part.name
        elif obj.sale_type == 'service':
            return obj.service_name
        return '-'
    get_item_name.short_description = 'Товар/Услуга'
