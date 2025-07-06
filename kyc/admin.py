from django.contrib import admin
from .models import KYC, KYCReview
from django.utils.html import format_html


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'review_status', 'is_verified', 'submitted_at')
    readonly_fields = ('preview_id_document', 'preview_selfie')

    def preview_id_document(self, obj):
        if obj.id_document:
            return format_html(
                f'<a href="{obj.id_document.url}" target="_blank">View PDF</a>'
            )
        return "No document"

    def preview_selfie(self, obj):
        if obj.selfie_photo:
            return format_html(
                f'<img src="{obj.selfie_photo.url}" width="150" />'
            )
        return "No selfie"

    preview_id_document.short_description = "ID Document"
    preview_selfie.short_description = "Selfie Photo"


@admin.register(KYCReview)
class KYCReviewAdmin(admin.ModelAdmin):
    list_display = ('kyc', 'review_status', 'reviewed_at', 'reviewer')
    readonly_fields = ('reviewed_at',)
