from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from users.models import Color, Wallet

User = get_user_model()


class UserCustomAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name',
        'color', 'colored_name', 'is_staff',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'color'
        )}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_editable = ('color',)

    @admin.display
    def colored_name(self, obj):
        return format_html(
            '<span style="color: #{}">{}</span>',
            obj.color,
            obj.username,
        )


class WalletAdmin(admin.ModelAdmin):
    search_fields = ('owner',)
    list_display = ('owner', 'total_won', 'current_sum',)


admin.site.register(Color)
admin.site.register(User, UserCustomAdmin)
admin.site.register(Wallet, WalletAdmin)
