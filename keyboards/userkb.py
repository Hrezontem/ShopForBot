
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callback_data import (
    AddToCartData,
    ChangeCartItemData,
    DeleteCartItemData,
    DeliveryData,
    EditProfileData,
    ProductClickData,
)

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✨ Каталог", callback_data="catalog")],
        [
            InlineKeyboardButton(text="🛍 Оформить заказ", callback_data="checkout"),
            InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
        ],
        [
            InlineKeyboardButton(text="📏 Подобрать размер", callback_data="picksize"),
            InlineKeyboardButton(
                text="🚚 Профиль", callback_data="myprofile"
            ),
        ],
        [
            InlineKeyboardButton(text="🤍 О бренде", callback_data="about"),
            InlineKeyboardButton(text="💬 Поддержка", callback_data="support"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите вариант ",
)


def back_button(to: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=to)


def to_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)

    return builder.as_markup()

def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_profile")
    return builder.as_markup()

def cart_keyboard(items) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if items != []:
        builder.button(text="✅ Оформить заказ", callback_data="checkout")
        builder.button(text="🗑️ Очистить корзину", callback_data="clearcart")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)

    return builder


def cart_items_keyboard(items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if items != []:
        for i in items:
            if i.variant is None:
                builder.button(text="⚠️ Данного товара нет")
                builder.button(
                    text="❌ Удалить",
                    callback_data=DeleteCartItemData(cart_item_id=i.id).pack(),
                )
                continue
            name = i.variant.product.name
            size = i.variant.size

            builder.button(
                text=f"✏️{name} - {size}",
                callback_data=ChangeCartItemData(cart_item_id=i.id).pack(),
            )
            builder.button(
                text="❌ Удалить",
                callback_data=DeleteCartItemData(cart_item_id=i.id).pack(),
            )
            builder.adjust(2)
    builder.attach(cart_keyboard(items))
    return builder.as_markup()


def catalog_keyboard(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"🛍️ {product.name} — {product.price} ₽",
            callback_data=ProductClickData(id=product.id).pack(),
        )

    builder.adjust(1)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)

    return builder.as_markup()


def variants_keyboard(variants) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for variant in variants:
        if variant.stock > 0:
            builder.button(
                text=f"📏 {variant.size} ({variant.stock} шт.)",
                callback_data=AddToCartData(variant_id=variant.id).pack(),
            )
    builder.adjust(2)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.row(back_button("catalog"))
    builder.adjust(2)
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить данные", callback_data="change_profile")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def change_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Фамилию", callback_data=EditProfileData(field="last_name").pack())
    builder.button(text="Имя", callback_data=EditProfileData(field="first_name").pack())
    builder.button(text="Отчество", callback_data=EditProfileData(field="mid_name").pack())
    builder.button(text="Номер телефона", callback_data=EditProfileData(field="phone").pack())
    builder.button(text="Почту", callback_data=EditProfileData(field="email").pack())
    builder.button(text="Адрес", callback_data=EditProfileData(field="address").pack())
    builder.adjust(2)
    builder.row(back_button("myprofile"))
    return builder.as_markup()


def checkout_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Выбрать способ доставки", callback_data="choice_delivery_method")
    builder.button(text="Добавить комментарий", callback_data="add_comment")
    builder.button(text="✅ Оформить заказ", callback_data="checkout_confirm")
    builder.button(text="❌ Выйти", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def delivery_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="СДЭК ПВЗ", callback_data=DeliveryData(method="post").pack())
    builder.button(text="СДЭК Курьер", callback_data=DeliveryData(method="courier").pack())
    builder.adjust(1)
    return builder.as_markup()
