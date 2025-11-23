from django.urls import path
from .views import (
    home,
    products,
    product_details,
    shopping_list,
    create_product,
    create_store,
    store_list,
    store_edit,
    delete_store,
    create_shopping_list,
    edit_shopping_list,
    delete_shopping_list,
    totals_view,
    purchase_list,
    purchase_detail,
    add_purchase,
    edit_purchase,
    delete_purchase,
    
    calculator_view,
    select_year_start
)
app_name = "prices"  # 🔐 Enables {% url 'prices:view_name' %} namespacing

urlpatterns = [
    # 🔹 Core
    path('', home, name='home'),

    # 🔹 Shopping List
    path('shopping-list/', shopping_list, name='shopping_list'),
    path('create-shopping-list/', create_shopping_list, name='create_shopping_list'),
    path('shopping-list/<int:item_id>/edit/', edit_shopping_list, name='edit_shopping_list'),
    path('shopping-list/<int:item_id>/delete/', delete_shopping_list, name='delete_shopping_list'),

    # 🔹 Products
    path('products/', products, name='product_list'),
    path('create-product/', create_product, name='create_product'),

    # 🔹 Stores
    path('stores/', store_list, name='store_list'),
    path('create-store/', create_store, name='create_store'),
    path('stores/<int:store_id>/edit/', store_edit, name='store_edit'),
    path('delete-store/<int:store_id>/delete/', delete_store, name='delete_store'),
    # 🔹 Purchases
    path('purchase_list/', purchase_list, name='purchase_list'),
    path('add/', add_purchase, name='add_purchase'),
    path('purchase/<int:purchase_id>/', purchase_detail, name='purchase_detail'),
    path('edit_purchase/<int:purchase_id>/', edit_purchase, name='edit_purchase'),
    path('delete_purchase/<int:purchase_id>/', delete_purchase, name='delete_purchase'),
    # 🔹 Reports / Tools
    path('product-details/<int:product_id>/', product_details, name='product_details'),
    path('totals/', totals_view, name='totals'),
    path('calculator/', calculator_view, name='calculator'),
    path('select-year-start/', select_year_start, name='select_year_start'),
]
