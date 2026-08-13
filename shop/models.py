from decimal import Decimal
from tabnanny import verbose

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название продукции")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_percent = models.PositiveIntegerField(blank=True, null=True, verbose_name="Скидка (%)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена со скидкой")
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.discount_percent and self.price:
            discount_amount = self.price * (Decimal(self.discount_percent) / Decimal('100.0'))
            self.discount_price = (self.price - discount_amount).quantize(Decimal('0.01'))
        else:
            self.discount_price = None
            self.discount_percent = None
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("XXS", "XXS"),
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("3XL", "3XL"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Товар"
    )
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, verbose_name="Размер")
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Количество на складе",
    )

    class Meta:
        verbose_name = "Вариант товара (размер)"
        verbose_name_plural = "Варианты товаров (Размеры)"
        unique_together = ("product", "size")

    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()} ({self.stock} шт.)"
