from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import WalletOrEmailAuthenticationForm


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("wallet_address", "username", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("wallet_address", "username", "email")
    ordering = ("wallet_address",)

    fieldsets = (
        (None, {"fields": ("wallet_address", "username", "email", "password")}),
        ("Web3 Auth", {"fields": ("nonce", "nonce_created_at", "last_nonce_used")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("wallet_address", "email", "password1", "password2", "is_staff", "is_active")}
        ),
    )

admin.site.login_form = WalletOrEmailAuthenticationForm
admin.site.login_template = 'admin/login.html'  # Optional override
admin.site.register(CustomUser, CustomUserAdmin)
