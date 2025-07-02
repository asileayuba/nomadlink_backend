from django.contrib import admin
from .models import EmergencyAlert

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'alert_type', 'message', 'is_resolved', 'triggered_at')
    list_filter = ('alert_type', 'is_resolved', 'triggered_at')
    search_fields = ('user__wallet_address', 'message')
