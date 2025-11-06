from django.contrib import admin
from django.utils.html import format_html
from .models import Customer

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'current_balance', 'status_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        ("Customer Info", {
            "fields": ("name", "phone", "email", "address")
        }),
        ("Account Info", {
            "fields": ("current_balance", "status_display")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def status_display(self, obj):
        """Show colored status (Due / Advance / Clear) in admin list."""
        color_map = {
            "Due": "red",
            "Advance": "green",
            "Clear": "gray",
        }
        color = color_map.get(obj.status, "black")
        return format_html(
            '<b><span style="color:{};">{}</span></b>',
            color,
            obj.status
        )
    status_display.short_description = "Status"  # column title in admin
