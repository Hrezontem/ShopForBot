from statistics import quantiles

from django.core.exceptions import ValidationError
from django.db import models, transaction

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


# Входными данными будет User от которого будут ссылаться на Cart, а с него на CartItem, которые надо перенести В Order
# а также комментарий и способ доставки
# Работать всё будет в одной транзакции
# 1. Находим Cart по User
# 2. Проверяем пустая ли Cart
# 2.1 Если пустая, то возвращаем ошибку, что корзина пустая и заказ оформить не получается
# 3. Создаем Order, присваиваем ему user и переносим перс данные
# в поля с припиской recipient
# 4. Далее переносим все CartItem в OrderItem и блокируем все строки, чтобы не было того что юзеры спишут один и тот же товар
# 5. Заполняем цены из товаров для сохранения историчности
# 6. Заполняется комментарий, если требуется и способ доставки
# 7. Списываем сток с товаров
# 8. Очищаем корзину
# 9. Сохраняем заказ

def create_order(user, comment, delivery_method="post"):
    with transaction.atomic():
        cart = Cart.objects.filter(user=user).first()
        if cart is None or not cart.items.exists():
            raise ValueError("Корзина пуста или несуществует")
        order = Order.objects.create(
            user=user,
            recipient_last_name=user.last_name,
            recipient_first_name=user.first_name,
            recipient_mid_name=user.mid_name,
            recipient_phone=user.phone,
            recipient_address=user.address,
            recipient_email=user.email,
            comment=comment,
            delivery_method=delivery_method,

        )
        variant_ids = [item.variant_id for item in cart.items.all()]
        locked = (ProductVariant.objects.select_for_update().select_related("product").filter(id__in=variant_ids))
        variants = {v.id: v for v in locked}
        for item in cart.items.select_related("variant__product"):
            variant = variants[item.variant_id]
            product = variant.product
            if variant.stock < item.quantity:
                raise ValueError(f"Недостаточно товара: {product.name}, осталось {variant.stock}")
            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=item.quantity,
                price_before_discount=product.price,
                price_at_purchase = product.discount_price or product.price,
                discount_percent = product.discount_percent
            )
            variant.stock -= item.quantity
            variant.save()
        cart.delete()
    return order
