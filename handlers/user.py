from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from asgiref.sync import sync_to_async

import keyboards.userkb as kb
from handlers.callback_data import AddToCartData, DeleteCartItemData, ProductClickData
from handlers.userfnc import (
    get_all_products,
    get_cart_with_items,
    get_product_with_variants,
)
from order.services import add_to_cart as add_to_cart_service
from order.services import clear_cart as clear_cart_service
from order.services import remove_cart_item as remove_cart_item_service
from user.services import get_or_create_user_from_telegram, get_user_from_telegram

user = Router()
menu_photo = FSInputFile("./media/bot/menu.png")
tempusername = ""


# Helpers


def build_cart_text(items):
    cart_text = ""
    for num, item in enumerate(items, start=1):
        if item.variant is None:
            cart_text += "Данного товара нет"
        name = item.variant.product.name
        price = item.variant.product.price
        size = item.variant.size
        qty = item.quantity

        cart_text += f"{num}. {name} — {size}\n     x {qty} — {price} ₽\n"
    return cart_text


async def render_cart(callback, user):
    cart, items = await get_cart_with_items(user)

    if cart is None or items == []:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=menu_photo,
                caption="🛒 Ваша корзина пуста"
            ),
            reply_markup=kb.cart_items_keyboard(items),
        )
        return
    text = build_cart_text(items)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption="🛒 Ваша корзина\n\n"
            + f"{text}\n"
            + f"Итого: {cart.total_cart_cost} ₽",
        ),
        reply_markup=kb.cart_items_keyboard(items),
    )


@user.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer_photo(
        menu_photo,
        caption=f"Добро пожаловать в ТЧК SHOP, {message.from_user.full_name}!",
        reply_markup=kb.main,
    )


@user.callback_query(F.data == "main_menu")
async def send_main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption=f"Добро пожаловать в ТЧК SHOP, {callback.from_user.full_name}!",
        ),
        reply_markup=kb.main,
    )


@user.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption=f"Корочи, наш бренд самый лучши, берите у нас, ибо мы руски с нами бог 🇷🇺🇷🇺🇷🇺.\n\nНа наших майках нет ни одной ворсинки, которой можно будет зацепиться за че-нибудь. \nА ещё наши изделия пропитаны специальными целебными маслами из подорожника, которые имеют эффект ускоренной регенерации на тот случай если поранитесь. \n\nПросто разорвите футболку, приложите к ране и исцеление на лицо :)) ",
        reply_markup=kb.to_main_menu_keyboard(),
    )


# ─── АСИНХРОННЫЕ ХЭНДЛЕРЫ БОТА ───


# ШАГ 1: Показ списка товаров
@user.callback_query(F.data == "catalog")
async def show_catalog_list(callback: CallbackQuery):
    # Вызываем функцию базы данных через await
    products = await get_all_products()

    if not products:
        await callback.answer("Каталог товаров пока пуст 😔", show_alert=True)
        return

    text = "📋 **Выберите интересующий вас товар:**"

    await callback.answer()
    await callback.message.edit_caption(
        text, reply_markup=kb.catalog_keyboard(products)
    )


# ШАГ 2: Показ карточки товара и размеров
@user.callback_query(ProductClickData.filter())
async def show_product_card(callback: CallbackQuery, callback_data: ProductClickData):

    product, variants, image_path = await get_product_with_variants(callback_data.id)

    if not product:
        await callback.answer("Товар не найден ❌", show_alert=True)
        return

    text = (
        f"👕 **{product.name}**\n\n"
        f"📝 {product.description or 'Описание отсутствует'}\n"
        f"💰 Цена: {product.price} руб.\n\n"
        f"👇 Выберите подходящий размер для добавления в корзину:"
    )

    await callback.answer()
    if image_path:
        photo_file = FSInputFile(image_path)

        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo_file, caption=text),
            reply_markup=kb.variants_keyboard(variants),
            parse_mode="Markdown",
        )
    else:
        # Если фото у товара нет, просто отправляем карточку обычным текстом
        await callback.message.edit_caption(
            text=text,
            reply_markup=kb.variants_keyboard(variants),
            parse_mode="Markdown",
        )


@user.callback_query(AddToCartData.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: AddToCartData):
    django_user = await get_or_create_user_from_telegram(callback.from_user)
    try:
        item = await sync_to_async(add_to_cart_service)(
            django_user, callback_data.variant_id, quantity=1
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await callback.answer(
        f"✅ Добавлено в корзину: {item.quantity} шт. ", show_alert=True
    )


@user.callback_query(F.data == "clearcart")
async def clear_cart(callback: CallbackQuery):
    django_user = await get_user_from_telegram(callback.from_user)
    try:
        await sync_to_async(clear_cart_service)(django_user)
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return
    await callback.answer()
    await render_cart(callback, django_user)



@user.callback_query(DeleteCartItemData.filter())
async def remove_to_cart(callback: CallbackQuery, callback_data: DeleteCartItemData):
    django_user = await get_user_from_telegram(callback.from_user)
    try:
        await sync_to_async(remove_cart_item_service)(
            django_user, callback_data.cart_item_id
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return
    await callback.answer()
    await render_cart(callback, django_user)


@user.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    django_user = await get_or_create_user_from_telegram(callback.from_user)
    if django_user is None:
        await callback.answer("Вы не зарегистрированы в базе.", show_alert=True)
        return

    await callback.answer()
    await render_cart(callback, django_user)
