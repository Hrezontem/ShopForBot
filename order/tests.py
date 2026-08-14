from django.contrib.auth import get_user_model
from django.test import TestCase

from order.models import Cart, CartItem, Order, OrderItem
from order.services import add_to_cart, create_order
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


class CreateOrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123",
            last_name="Григорьев",
            first_name="Евгений",
            mid_name="Владимирович",
            address="ул. Пролетарская д. 239 подъезд 1",
            phone="88009993322"
        )
        self.product = Product.objects.create(name="Супер майка", price=1000)
        self.variant1 = ProductVariant.objects.create(
            product=self.product, size="М",  stock=10
        )
        self.variant2 = ProductVariant.objects.create(
            product=self.product, size="XL",  stock=10
        )
        self.delivery_method="courier"
        self.comment = 'Когда будете подъезжать к дому 239 остановитесь возле магазина Чижик. Ведутся дорожные работы и проехать не получится, а до подъезда только пешком можно дойти.'


    def test_success_order(self):
        add_to_cart(self.user, self.variant1.id, quantity=3)
        add_to_cart(self.user, self.variant2.id, quantity=1)

        create_order(self.user, self.comment, self.delivery_method)

        self.variant1.refresh_from_db()
        self.variant2.refresh_from_db()

        self.assertEqual(self.variant1.stock, 7)
        self.assertEqual(self.variant2.stock, 9)
        self.assertEqual(Cart.objects.count(), 0)

    def test_empty_cart(self):
        with self.assertRaises(ValueError):
            create_order(self.user, self.comment, self.delivery_method)

    def test_empty_product_stock(self):
        add_to_cart(self.user, self.variant1.id, quantity=3)
        add_to_cart(self.user, self.variant2.id, quantity=1)

        self.variant1.stock = 0
        self.variant2.stock = 0
        self.variant1.save()
        self.variant2.save()

        with self.assertRaises(ValueError):
            create_order(self.user, self.comment, self.delivery_method)

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 2)
