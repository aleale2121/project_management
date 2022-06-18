from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["username", "email"]
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (_("Personal Info"), {"fields": ("name",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email"),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Staff)
admin.site.register(models.Student)
admin.site.register(models.Batch)
admin.site.register(models.Group)
admin.site.register(models.Member)
admin.site.register(models.Examiner)
admin.site.register(models.Chat)
admin.site.register(models.Contact)
admin.site.register(models.Evaluation)
admin.site.register(models.Mark)


