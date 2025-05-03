from django.urls import path
from .views import (
    home,
    products,
    stores,
    shopping_list,
    create_product,
    create_store,
    create_shopping_list,
    totals_view,
    purchase_list,
    add_purchase,
    edit_purchase,
    delete_purchase,
    calculator_view,
    select_year_start
)

urlpatterns = [
    path('', home, name='home'),  # Homepage URL
    path('products/', products, name='product_list'),  # List of products
    path('stores/', stores, name='store_list'),  # List of stores
    path('shopping-list/', shopping_list, name='shopping_list'),  # Shopping list
    path('create-product/', create_product, name='create_product'),  # Create a new product
    path('create-store/', create_store, name='create_store'), 
    path('create-shopping-list/', create_shopping_list, name='create_shopping_list'),
    path('purchase_list/', purchase_list, name='purchase_list'),
    path('add/', add_purchase, name='add_purchase'),
    path('edit_purchase/<int:purchase_id>/', edit_purchase, name='edit_purchase'),
    path('delete_purchase/<int:purchase_id>/', delete_purchase, name='delete_purchase'),
    path('totals/', totals_view, name='totals'),
    path('calculator/', calculator_view, name='calculator'),
    path('select-year-start/', select_year_start, name='select_year_start'),
]
