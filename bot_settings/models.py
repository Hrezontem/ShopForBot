from django.db import models


class BotConfiguration(models.Model):
    token = models.CharField(
        max_length=255,
        verbose_name="Telegram Токен",
        help_text="Введите акутальный токен бота от @BotFather"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Бот активен"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения"
    )
    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Основные"

    def __str__(self):
        return f"Конфигурация от {self.updated_at}"
