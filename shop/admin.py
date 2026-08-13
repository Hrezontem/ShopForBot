from django.contrib import admin

from shop.models import Product, ProductVariant


# Register your models here.
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]
    inlines = [ProductVariantInline]
