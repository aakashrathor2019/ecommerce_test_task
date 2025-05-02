from django.contrib import admin

from .models import AppUser, CartItem, Category, Order, OrderItem, Product, WishlistItem

# Register your models here.
admin.site.register(AppUser)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CartItem)
admin.site.register(WishlistItem)
admin.site.register(Order)
admin.site.register(OrderItem)
