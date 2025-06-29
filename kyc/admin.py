from django.contrib import admin
from .models import KYC

@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'is_verified', 'review_status', 'submitted_at', 'reviewed_at')
    list_filter = ('is_verified', 'review_status', 'level')
    search_fields = ('user__wallet_address', 'user__email')
