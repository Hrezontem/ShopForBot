
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✨ Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛍 Купить", callback_data="buy"),InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton(text="📏 Подобрать размер", callback_data="size"), InlineKeyboardButton(text="🚚 Отслеживание заказа", callback_data="delivery")],
        [InlineKeyboardButton(text="🤍 О бренде", callback_data="about"),InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите вариант ",
)
