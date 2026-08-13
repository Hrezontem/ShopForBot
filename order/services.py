from django.core.exceptions import ValidationError
from django.db import transaction

from shop.models import ProductVariant

from .models import Cart, CartItem, Order, OrderItem


# Для такой функции понадобится сам юзер, изделие(плюс размер) и его количество
# Этапы:
# 1. Пользователь нажимает на кнопку "Добавить в корзину".
# Эта кнопка должна передавать tg id пользователя,
# по которому уже будет искаться существующий юзер в базе, id изделия и количество изделия
# 2. add_to_cart срабатывает, с имеющимися данными ищет пользователя и изделие
# 3. Проверка на существование корзины для пользователя
# 3.1. Если существует, то просто получить его данные и перейти этапу 4
# 3.2  Иначе создать новый для конкретного пользователя и добавляет новый Cart в базу, который будет привязан к User
# 4. В этот Cart добавляет CartItem, который будет привязан уже к ProductVariant и подставлено quantity
# 5. Не забыть сохранить
def add_to_cart(user, product_variant_id, quantity=1):
    variant = ProductVariant.objects.get(id=product_variant_id)
    cart, _ = Cart.objects.get_or_create(user=user)
    existing_item = CartItem.objects.filter(cart=cart, variant=variant).first()
    already = existing_item.quantity if existing_item else 0
    if already + quantity > variant.stock:
        raise ValueError(
            f"Недостаточно товара: на складе {variant.stock}, в корзине {already}, добавляют {quantity}"
        )
    item, item_created = CartItem.objects.get_or_create(
        cart=cart, variant=variant, defaults={"quantity": quantity}
    )

    if not item_created:
        item.quantity += quantity
        item.save()

    return item

def checkout_cart_to_order(user, delivery_method="post", delivery_address=""):
    """
    Конвертирует корзину пользователя в реальный заказ.
    Возвращает созданный объект Order или вызывает ValidationError.
    """
    with transaction.atomic():
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError("Корзина пуста или не существует")

        cart_items = cart.items.select_related("variant__product").all()
        if not cart_items.exists():
            raise ValidationError("В вашей корзине нет товаров")

        for item in cart_items:
            if item.variant.stock < item.quantity:
                raise ValidationError(
                    f"Недостаточно товара {item.variant.product.name} (Размер: {item.variant.size}) на складе."
                    f"Доступно: {item.variant.stock} шт., в корзине: {item.quantity} шт."
                )
        order = Order.objects.create(
            user=user,
            delivery_method=delivery_method,
            comment=f"Оформлено из корзины. Адрес по умолчанию: {delivery_address}"
            if delivery_address
            else "",
        )

        for item in cart_items:
            product = item.variant.product

            price_before = product.price
            price_final = product.discount_price or product.price
            pct = product.discount_percent

            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price_before_discount=price_before,
                price_at_purchase=price_final,
                discount_percent=pct,
            )

            variant = item.variant
            variant.stock -= item.quantity
            variant.save()

        cart_items.delete()

        return order
