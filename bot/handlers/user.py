import keyboards.userkb as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, reply_markup_union
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls.resolvers import re
from handlers.callback_data import (
    AddToCartData,
    DeleteCartItemData,
    DeliveryData,
    EditProfileData,
    ProductClickData,
)
from handlers.states import OrderStates, ProfileStates
from handlers.userfnc import (
    get_all_products,
    get_cart_with_items,
    get_product_with_variants,
)
from order.services import add_to_cart as add_to_cart_service
from order.services import clear_cart as clear_cart_service
from order.services import create_order
from order.services import remove_cart_item as remove_cart_item_service
from phonenumber_field.validators import validate_international_phonenumber
from user.services import (
    get_or_create_user_from_telegram,
    get_user_from_telegram,
    update_profile,
)

user = Router()
menu_photo = FSInputFile("./back/media/bot/menu.jpg")


# Helpers


REQUIRED = ["last_name", "first_name", "phone", "address"]
QUESTIONS = {
    "last_name": "Введите фамилию",
    "first_name": "Введите имя",
    "mid_name": "Введите отчество (Необязательное поле)",
    "phone": "Введите телефон",
    "address": "Введите адрес доставки",
    "email": "Эл. почта (Необязательное поле)",
}

VALIDATORS = {
    "phone": validate_international_phonenumber,
    "email": validate_email,
}


def normalize_phone(value):
    v = re.sub(r"[\s\-\(\)]", "", value.strip())
    if v.startswith("8"):  # 8 999 ... → +7 999 ...
        v = "+7" + v[1:]
    elif v.startswith("9"):  # 999 ... → +7 999 ...
        v = "+7" + v
    elif v.startswith("7") and not v.startswith("+7"):
        v = "+" + v  # 7999... → +7999...
    return v


def validate_field(field, value):
    if not value:
        return None
    if field == "phone":
        value = normalize_phone(value)  # приводим к +7...
    validator = VALIDATORS.get(field)
    if validator:
        try:
            validator(value)
        except ValidationError:
            return None
    return value


async def after_field_saved(event, state, user):
    data = await state.get_data()
    if data.get("mode") != "checkout":
        await state.clear()
        await render_profile(event, user)
        return

    # режим checkout: следующее пустое обязательное или завершение
    for field in REQUIRED:
        if not getattr(user, field):
            await state.set_state(getattr(ProfileStates, field))
            await event.answer(QUESTIONS[field])
            return

    # checkout-ветка после последнего обязательного поля:
    await state.set_state(None)
    await state.set_data({"delivery": "post", "comment": ""})
    django_user = await get_or_create_user_from_telegram(event.from_user)
    await render_checkout(event, django_user, await state.get_data())


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


DELIVERY_LABELS = {"post": "СДЭК ПВЗ", "courier": "СДЭК курьер"}


async def render_checkout(event, user, data):
    cart, items = await get_cart_with_items(user)

    if cart is None or not items:
        text = "🛒 Корзина пуста. Добавьте товар и оформите заказ."
        markup = kb.cart_items_keyboard(items)
    else:
        delivery = DELIVERY_LABELS.get(data.get("delivery", "post"))
        comment = data.get("comment") or "—"
        text = (
            "🛒 Ваш заказ\n\n"
            + build_cart_text(items)
            + "\n"
            + f"Итого: {cart.total_cart_cost} ₽\n"
            + f"🚚 Доставка: {delivery}\n"
            + f"💬 Комментарий: {comment}"
        )
        markup = kb.checkout_keyboard()

    if isinstance(event, CallbackQuery):
        await event.message.edit_media(
            media=InputMediaPhoto(media=menu_photo, caption=text),
            reply_markup=markup,
        )
    else:
        await event.answer_photo(menu_photo, caption=text, reply_markup=markup)


async def render_cart(callback, user):
    cart, items = await get_cart_with_items(user)

    if cart is None or items == []:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=menu_photo, caption="🛒 Ваша корзина пуста"),
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
        caption=f"Добро пожаловать в shop name, {message.from_user.full_name}!",
        reply_markup=kb.main,
    )


@user.callback_query(F.data == "main_menu")
async def send_main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption=f"Добро пожаловать в shop name, {callback.from_user.full_name}!",
        ),
        reply_markup=kb.main,
    )


@user.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption=f"Описание бренда магазина",
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


def build_profile_text(user):
    return (
        "Ваш профиль\n\n"
        + f"Фамилия: {user.last_name or 'Не заполнено'}\n"
        + f"Имя: {user.first_name or 'Не заполнено'}\n"
        + f"Отчество: {user.mid_name or 'Не заполнено'}\n"
        + f"Номер телефона: {user.phone or 'Не заполнено'}\n"
        + f"Адрес: {user.address or 'Не заполнено'}\n"
        + f"Почта: {user.email or 'Не заполнено'}"
    )


async def render_profile(event, user):
    text = build_profile_text(user)
    if isinstance(event, CallbackQuery):
        await event.message.edit_caption(
            caption=text, reply_markup=kb.profile_keyboard()
        )
    else:
        await event.answer_photo(
            menu_photo, caption=text, reply_markup=kb.profile_keyboard()
        )


@user.callback_query(F.data == "myprofile")
async def show_profile(callback):
    django_user = await get_user_from_telegram(callback.from_user)
    await callback.answer()
    await render_profile(callback, django_user)


@user.callback_query(F.data == "change_profile")
async def change_profile(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption="Что изменить?", reply_markup=kb.change_profile_keyboard()
    )


@user.callback_query(EditProfileData.filter())
async def change_profile_field(
    callback: CallbackQuery, callback_data: EditProfileData, state: FSMContext
):
    await state.set_state(getattr(ProfileStates, callback_data.field))
    await state.update_data(mode="edit")
    await callback.answer()
    await callback.message.edit_caption(
        caption=QUESTIONS[callback_data.field], reply_markup=kb.cancel_keyboard()
    )


@user.callback_query(F.data == "cancel_profile")
async def cancel_profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # выходим из FSM
    await callback.answer()
    django_user = await get_user_from_telegram(callback.from_user)
    await render_profile(callback, django_user)  # возвращаем интерфейс


@user.message(ProfileStates.last_name)
@user.message(ProfileStates.first_name)
@user.message(ProfileStates.mid_name)
@user.message(ProfileStates.address)
@user.message(ProfileStates.phone)
@user.message(ProfileStates.email)
async def save_profile_field(message: Message, state: FSMContext):
    print(await state.get_state())
    field = (await state.get_state()).split(":")[-1]
    value = message.text.strip()

    clean = validate_field(field, value)
    if clean is None:
        await message.answer(QUESTIONS[field])
        return
    django_user = await get_user_from_telegram(message.from_user)
    await sync_to_async(update_profile)(django_user, **{field: clean})
    await after_field_saved(message, state, django_user)


@user.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    django_user = await get_user_from_telegram(callback.from_user)
    if django_user is None:
        await callback.answer("Вы не зарегистрированы.", show_alert=True)
        return
    await callback.answer()

    for field in REQUIRED:
        if not getattr(django_user, field):
            await state.set_state(getattr(ProfileStates, field))
            await state.update_data(mode="checkout")
            await callback.message.edit_caption(
                caption=QUESTIONS[field], reply_markup=kb.cancel_keyboard()
            )
            return

    await state.set_data({"delivery": "post", "comment": ""})
    await render_checkout(callback, django_user, await state.get_data())


@user.callback_query(F.data == "choice_delivery_method")
async def choice_delivery(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption="Выберите способ доставки:",
        reply_markup=kb.delivery_keyboard(),
    )


@user.callback_query(F.data == "add_comment")
async def add_comment(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.comment)
    await callback.answer()
    await callback.message.edit_caption(caption="Напишите комментарий:")


@user.message(OrderStates.comment)
async def save_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text.strip())
    await state.set_state(None)
    django_user = await get_user_from_telegram(message.from_user)
    await render_checkout(message, django_user, await state.get_data())


@user.callback_query(DeliveryData.filter())
async def set_delivery(callback, callback_data: DeliveryData, state: FSMContext):
    await state.update_data(delivery=callback_data.method)
    await callback.answer()
    django_user = await get_user_from_telegram(callback.from_user)
    await render_checkout(callback, django_user, await state.get_data())


def order_success_text(order):
    return (
        f"✅ Заказ №{order.id} оформлен!\n"
        f"Итого: {order.total_order_cost} ₽\n"
        "Мы свяжемся с вами для подтверждения."
    )


@user.callback_query(F.data == "checkout_confirm")
async def checkout_confirm(callback: CallbackQuery, state: FSMContext):
    django_user = await get_user_from_telegram(callback.from_user)
    if django_user is None:
        await callback.answer("Вы не зарегистрированы.", show_alert=True)
        return

    data = await state.get_data()
    try:
        order = await sync_to_async(create_order)(
            django_user,
            comment=data.get("comment", ""),
            delivery_method=data.get("delivery", "post"),
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await state.clear()  # заказ создан — checkout-данные больше не нужны
    text = await sync_to_async(order_success_text)(order)
    await callback.answer()
    await callback.message.edit_caption(
        caption=text, reply_markup=kb.to_main_menu_keyboard()
    )
