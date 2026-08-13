from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilderё

from handlers.userfnc import get_all_products, get_product_with_variants
import keyboards.userkb as kb

user = Router()


@user.message(CommandStart())
async def start(message: Message) -> None:
    menu_photo = FSInputFile("./media/bot/menu.png")
    await message.answer_photo(
        menu_photo,
        caption=f"Добро пожаловать в ТЧК SHOP, {message.from_user.full_name}!",
        reply_markup=kb.main
    )

class ProductClickData(CallbackData, prefix="prod"):
    id: int

class AddToCartData(CallbackData, prefix="cart"):
    variant_id: int  # Хранит ID строки из таблицы ProductVariant


# ─── АСИНХРОННЫЕ ХЭНДЛЕРЫ БОТА ───

# ШАГ 1: Показ списка товаров
@user.callback_query(F.data == 'catalog')
async def show_catalog_list(callback: CallbackQuery):
    # Вызываем функцию базы данных через await
    products = await get_all_products()

    if not products:
        await callback.answer("Каталог товаров пока пуст 😔", show_alert=True)
        return

    text = "📋 **Выберите интересующий вас товар:**"
    builder = InlineKeyboardBuilder()

    for product in products:
        builder.button(
            text=f"🛍️ {product.name} — {product.price} руб.",
            callback_data=ProductClickData(id=product.id).pack()
        )

    builder.adjust(1)
    await callback.answer()
    await callback.message.answer(text, reply_markup=builder.as_markup())


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

    builder = InlineKeyboardBuilder()

    # Итерируемся по уже готовому списку размеров, который мы извлекли в потоке СУБД
    for variant in variants:
        if variant.stock > 0:
            builder.button(
                text=f"📏 {variant.size} ({variant.stock} шт.)",
                callback_data=AddToCartData(variant_id=variant.id).pack()
            )

    builder.adjust(2)
    await callback.answer()
    if image_path:
        photo_file = FSInputFile(image_path)

        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo_file,
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    else:
        # Если фото у товара нет, просто отправляем карточку обычным текстом
        await callback.message.answer(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"

        )

@user.callback_query(AddToCartData.filter())
async def add_to_cart(callback: CallbackQuery, callback_data: ProductClickData):
    await callback.answer(f"{callback_data.id}")
