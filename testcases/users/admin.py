from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from users.models import Color, User


class UserCustomAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name',
        'color', 'colored_name', 'is_staff',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'color'
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


admin.site.register(Color)
admin.site.register(User, UserCustomAdmin)
