from django.contrib import admin
from .models import Product, Store, ShoppingList, Purchase
# Register your models here.
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(ShoppingList)

admin.site.register(Purchase)
# Compare this snippet from prices/views.py: