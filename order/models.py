from decimal import Decimal

from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from shop.models import ProductVariant


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина: {self.user.username}"

    @property
    def total_cart_cost(self) -> Decimal:
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.variant.product.name} ({self.variant.size}) x {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        price = self.variant.product.discount_price or self.variant.product.price
        return Decimal(price) * int(self.quantity)


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачен"),
        ("delivered", "Доставлен"),
        ("delivery", "В доставке"),
        ("canceled", "Отменен"),
    ]

    DELIVERY_CHOICES = [
        ("courier", "СДЭК курьер"),
        ("post", "СДЭК ПВЗ"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    recipient_last_name = models.CharField(
        max_length=255, blank=False, verbose_name="Фамилия получателя", default=""
    )
    recipient_first_name = models.CharField(
        max_length=255, blank=False, verbose_name="Имя получателя", default=""
    )
    recipient_mid_name = models.CharField(
        max_length=255, blank=True, verbose_name="Отчество получателя", default=""
    )
    recipient_phone = PhoneNumberField(
        region="RU", blank=False, verbose_name="Номер телефона", default=""
    )
    recipient_address = models.CharField(
        max_length=255, blank=False, verbose_name="Адрес получателя", default=""
    )
    recipient_email = models.EmailField(
        max_length=255, blank=True, verbose_name="Эл. почта получателя"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default="post"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.id} ({self.get_delivery_method_display()}) от {self.user.last_name} {self.user.first_name} {self.user.mid_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(blank=True, null=True)

    @property
    def total_price(self):
        return self.price_at_purchase * self.quantity

    @property
    def total_savings(self):
        return (self.price_before_discount - self.price_at_purchase) * self.quantity
