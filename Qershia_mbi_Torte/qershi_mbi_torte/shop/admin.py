from django.contrib import admin
from .models import UserProfile, Product, Order, OrderItem

admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(OrderItem)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "available_quantity", "ordered_quantity")
    search_fields = ("name",)

    # Ky është filtri që kërkon ti
    list_filter = ("available_quantity",)