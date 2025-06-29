from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import WalletOrEmailAuthenticationForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'wallet_address', 'email', 'is_staff')
    ordering = ('wallet_address',)
    search_fields = ('wallet_address', 'email', 'username')
    fieldsets = (
        (None, {'fields': ('wallet_address', 'username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('wallet_address', 'username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.login_form = WalletOrEmailAuthenticationForm
admin.site.login_template = 'admin/login.html'  # Optional override
admin.site.register(CustomUser, CustomUserAdmin)
