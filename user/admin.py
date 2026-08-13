from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.models import TelegramProfile, User


# 1. Создаем встроенную панель для профиля Telegram
class TelegramProfileInline(admin.TabularInline):
    model = TelegramProfile
    can_delete = False
    verbose_name_plural = "Профиль Telegram"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["get_tg_username", "username","first_name", "phone"]
    inlines = [TelegramProfileInline]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ( "last_name", "first_name","mid_name", "phone", "email", "address")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2"),
        }),
        ("Персональная информация", {
            "fields": ("last_name", "first_name","mid_name", "phone", "email", "address"),
        }),
    )

    @admin.display(description="Telegram Никнейм")
    def get_tg_username(self, obj):
        try:
            # Убедитесь, что в вашей модели TelegramProfile поле называется именно так,
            # либо замените obj.tg_profile.username на ваше имя поля.
            return obj.tg_profile.tg_username or obj.tg_profile.tg_uid
        except TelegramProfile.DoesNotExist, AttributeError:
            return "-"
