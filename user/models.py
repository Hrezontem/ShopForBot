from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    mid_name = models.CharField(
        max_length=255, blank=True, verbose_name="Отчество"
    )
    phone = PhoneNumberField(
        region="RU", blank=True, null=True, verbose_name="Номер телефона"
    )
    address = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Адрес"
    )
    email = models.EmailField(
        max_length=255, blank=True, null=True, verbose_name="Эл. почта"
    )

    class Meta(AbstractUser.Meta):
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.mid_name}".strip() or self.username

class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tg_profile")
    tg_uid = models.CharField(max_length=255, verbose_name="TG ID")
    tg_username = models.CharField(max_length=255, verbose_name="Имя пользователя TG")

    def __str__(self):
        return f"TG Profile: {self.tg_uid}"
