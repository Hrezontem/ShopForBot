from django.core.management.base import BaseCommand

from order.models import Cart
from order.services import add_to_cart
from shop.models import Product, ProductVariant
from user.models import User


class Command(BaseCommand):
    help = "Проверяет работу add_to_cart"

    def handle(self, *args, **options):

        user = User.objects.first()
        Cart.objects.filter(user=user).delete()
        variant = ProductVariant.objects.first()

        self.stdout.write(f"Тестируем: {user}, {variant}")

        item = add_to_cart(user, variant.id, quantity=2)
        self.stdout.write(f"После первого добавления: {item.quantity}")

        item = add_to_cart(user, variant.id, quantity=1)
        self.stdout.write(f"После второго добавления: {item.quantity}")
