from django.contrib.auth import get_user_model
from django.test import TestCase

from order.models import CartItem
from order.services import add_to_cart
from shop.models import Product, ProductVariant

# Create your tests here.

User = get_user_model()


class AddToCartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123")
        self.product = Product.objects.create(name="Супер майка", price=1000)
        self.variant = ProductVariant.objects.create(
            product=self.product, size="М",  stock=10
        )

    def test_first_add_creates_item(self):
        item = add_to_cart(self.user, self.variant.id, quantity=2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_repeated_add_increases_quantity(self):
        item = add_to_cart(self.user, self.variant.id, quantity=2)
        item = add_to_cart(self.user, self.variant.id, quantity=1)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_exceeding_stock_raises_error(self):
        with self.assertRaises(ValueError):
            item = add_to_cart(self.user, self.variant.id, quantity=11)
