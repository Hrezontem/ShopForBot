from asgiref.sync import sync_to_async

from order.models import Cart
from shop.models import Product


@sync_to_async
def get_all_products():
    """Возвращает список всех товаров."""
    # .only() или .values() можно использовать, если товаров сотни,
    # но list(Product.objects.all()) абсолютно подходит для небольшого каталога
    return list(Product.objects.all())


@sync_to_async
def get_cart_with_items(user):
    cart = (
        Cart.objects.filter(user=user)
        .prefetch_related("items__variant__product")
        .first()
    )
    if cart is None:
        return None, []
    return cart, list(cart.items.all())


@sync_to_async
def get_product_with_variants(product_id: int):
    product = Product.objects.prefetch_related("variants").get(id=product_id)
    if product is None:
       return None, [], None

    # Безопасно достаем путь к файлу изображения
    image_path = None
    if product.image and hasattr(product.image, "path"):
        image_path = product.image.path


    return product, list(product.variants.all()), image_path
