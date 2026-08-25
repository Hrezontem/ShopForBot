from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db import transaction

from user.models import TelegramProfile

User = get_user_model()


@sync_to_async
def get_user_from_telegram(telegram_user):
    tg_uid = str(telegram_user.id)
    profile = TelegramProfile.objects.select_related("user").filter(tg_uid=tg_uid).first()
    return profile.user if profile else None



@sync_to_async
def get_or_create_user_from_telegram(telegram_user):

    tg_uid = str(telegram_user.id)
    tg_username = telegram_user.username or ""
    tg_full_name = telegram_user.full_name or ""
    profile = TelegramProfile.objects.select_related("user").filter(tg_uid=tg_uid).first()
    if profile is not None:
        if profile.tg_username != tg_username:
            profile.tg_username = tg_username
            profile.save()
        return profile.user
    with transaction.atomic():
        user = User.objects.create_user(
            username=f"tg_{tg_uid}",
        )
        TelegramProfile.objects.create(
            user=user,
            tg_uid=tg_uid,
            tg_username=tg_username,
            tg_fullname=tg_full_name
        )
    return user


def update_profile(user, **fields):
    ALLOWED = {"first_name", "mid_name","last_name", "phone", "address", "email"}
    for key, value in fields.items():
        if key not in ALLOWED:
            raise ValueError(f"Поле {key} нельзя поменять")
        setattr(user, key, value)
    user.save()
