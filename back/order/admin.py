from django.contrib import admin

from order.models import Cart, CartItem, Order, OrderItem

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = ('price_before_discount', 'price_at_purchase', 'get_total_price')

    @admin.display(description="Итоговая цена")
    def get_total_price(self, obj):
        return f"{obj.total_price} руб." if obj.id else "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = ('id', 'user', 'delivery_method', 'status', 'created_at', 'get_total_cost')
    list_filter = ('status', 'delivery_method', 'created_at')
    search_fields = ('id', 'user__last_name', 'user__username')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'get_total_cost')

    @admin.display(description="Сумма заказа")
    def get_total_cost(self, obj):
        return f"{obj.total_order_cost} руб."


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_current_price',)

    @admin.display(description="Актуальная цена за 1 шт.")
    def get_current_price(self, obj):
        if obj.id and obj.variant:
            price = obj.variant.product.discount_price or obj.variant.product.price
            return f"{price} руб."
        return "-"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('id', 'user', 'created_at', 'updated_at', 'get_cart_total')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at', 'get_cart_total')

    @admin.display(description="Стоимость содержимого")
    def get_cart_total(self, obj):
        return f"{obj.total_cart_cost} руб."
