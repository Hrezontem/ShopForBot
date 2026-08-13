from asgiref.sync import sync_to_async

from shop.models import Product


@sync_to_async
def get_all_products():
    """Возвращает список всех товаров."""
    # .only() или .values() можно использовать, если товаров сотни,
    # но list(Product.objects.all()) абсолютно подходит для небольшого каталога
    return list(Product.objects.all())


@sync_to_async
def get_product_with_variants(product_id: int):
    """
    Извлекает товар, его варианты и путь к изображению за один запрос.
    """
    try:
        product = Product.objects.prefetch_related('variants').get(id=product_id)
        variants = list(product.variants.all())

        # Безопасно достаем путь к файлу изображения
        image_path = None
        if product.image and hasattr(product.image, 'path'):
            image_path = product.image.path

        return product, variants, image_path
    except Product.DoesNotExist:
        return None, [], None
