from aiogram.filters.callback_data import CallbackData


class ProductClickData(CallbackData, prefix="prod"):
    id: int

class AddToCartData(CallbackData, prefix="addcart"):
    variant_id: int

class DeleteCartItemData(CallbackData, prefix="del_cart_item"):
    cart_item_id: int

class ChangeCartItemData(CallbackData, prefix="change_cart_item"):
    cart_item_id: int
