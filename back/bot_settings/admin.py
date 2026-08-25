from django.contrib import admin
from .models import BotConfiguration


@admin.register(BotConfiguration)
class BotConfigurationAdmin(admin.ModelAdmin):
    list_display = ('token', 'is_active', 'updated_at')

    # Запрещаем добавлять новые записи, если одна уже существует
    def has_add_permission(self, request):
        if BotConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)

    # Запрещаем удалять единственную конфигурацию во избежание поломок
    def has_delete_permission(self, request, obj=None):
        return False
