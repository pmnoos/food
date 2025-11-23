# prices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now
from django.db.models import Sum
from datetime import datetime as native_datetime, timedelta
import subprocess, os, logging
from django.http import JsonResponse

from .models import Product, Store, ShoppingList, Purchase
from .forms import ProductForm, StoreForm, ShoppingListForm, PurchaseForm, YearStartForm
from .utils import apply_purchase_filters, calculate_totals, get_filter_choices

logger = logging.getLogger(__name__)

# ----------------------
# Homepage / Dashboard
# ----------------------


    # Get the current year and filter purchases accordingly
def home(request):
    # Start with current year purchases, but allow filtering
    current_year = now().year
    purchases = Purchase.objects.filter(date_of_purchase__year=current_year)
    
    # Apply filters using utility function
    purchases, filter_values = apply_purchase_filters(purchases, request)
    
    # Handle pagination
    try:
        records_per_page = int(request.GET.get('records_per_page', 10))
    except ValueError:
        records_per_page = 10
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    purchases = purchases.order_by('-date_of_purchase')
    paginator = Paginator(purchases, records_per_page)
    page_obj = paginator.get_page(page_number)

    # Calculate totals
    totals = calculate_totals(purchases, request)
    total_spent = totals['filtered_total']  # Use filtered total for home page
    total_running = sum(getattr(p, 'price_cost', 0) * getattr(p, 'quantity', 0) for p in purchases)
    
    # Get filter choices
    filter_choices = get_filter_choices()

    context = {
        'purchases': page_obj,
        'total_running': total_running,
        'total_spent': total_spent,
        'records_per_page': records_per_page,
        **filter_values,
        **filter_choices,
        **totals,  # Include all totals for potential use
    }
    
    return render(request, 'prices/home.html', context)

# ----------------------
# Totals View with Filtering

# ----------------------
# Totals View with Filtering
# ----------------------
def totals_view(request):
    purchases = Purchase.objects.all()
    purchases, filter_values = apply_purchase_filters(purchases, request)
    totals = calculate_totals(purchases, request)
    filter_choices = get_filter_choices()
    
    store_totals = purchases.values('store_name').annotate(total=Sum('total_cost')).order_by('-total')

    context = {
        'store_totals': store_totals,
        'purchases': purchases.order_by('-date_of_purchase'),
        **totals,
        **filter_values,
        **filter_choices,
    }
    
    return render(request, 'totals.html', context)

# ----------------------
# Purchase CRUD
# ----------------------
def purchase_list(request):
    purchases = Purchase.objects.all()
    purchases, filter_values = apply_purchase_filters(purchases, request)
    totals = calculate_totals(purchases, request)
    filter_choices = get_filter_choices()
    
    store_totals = purchases.values('store_name').annotate(total=Sum('total_cost')).order_by('-total')

    context = {
        'purchases': purchases.order_by('-date_of_purchase'),
        'store_totals': store_totals,
        **totals,
        **filter_values,
        **filter_choices,
    }
    
    return render(request, 'prices/purchase_list.html', context)
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            # Store the store's ID, not the object itself
            # Fix: form.cleaned_data['store_name'] may be a str if the field is not a ForeignKey
            # Use purchase.store_name.id if store_name is a ForeignKey, else just store the value
            if hasattr(purchase.store_name, 'id'):
                request.session['last_store_id'] = purchase.store_name.id
            else:
                request.session['last_store_id'] = purchase.store_name
            request.session['last_date_of_purchase'] = str(purchase.date_of_purchase)
            messages.success(request, f"Purchase added for {purchase.store_name} on {purchase.date_of_purchase}.")
            return redirect('prices:add_purchase')
    else:
        initial = {}
        last_store_id = request.session.get('last_store_id')
        if last_store_id:
            initial['store_name'] = last_store_id
        last_date = request.session.get('last_date_of_purchase')
        if last_date:
            initial['date_of_purchase'] = last_date
        form = PurchaseForm(initial=initial)
    return render(request, 'purchase/add_purchase.html', {'form': form})


def delete_purchase(request, purchase_id):
    try:
        purchase = Purchase.objects.get(id=purchase_id)
    except Purchase.DoesNotExist:
        messages.error(request, "That purchase does not exist or was already deleted.")
        return redirect('prices:purchase_list')
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, "Purchase deleted successfully.")
        return redirect('prices:purchase_list')
    return render(request, 'prices/delete_confirmation.html', {'purchase': purchase})

def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, 'prices/purchase_detail.html', {'purchase': purchase})
# ----------------------
# Tools and Utilities
# ----------------------
def calculator_view(request):
    calculator_path = os.path.join(settings.BASE_DIR, 'prices', 'calculator.py')
    if not os.path.exists(calculator_path):
        return HttpResponse("<h1>Error:</h1><pre>Calculator script not found.</pre>")
    try:
        result = subprocess.run(['python', calculator_path], capture_output=True, text=True)
        if result.returncode != 0:
            return HttpResponse(f"<h1>Error:</h1><pre>{result.stderr}</pre>")
        return HttpResponse(f"<pre>{result.stdout}</pre>")
    except Exception as e:
        return HttpResponse(f"<h1>Error:</h1><pre>{str(e)}</pre>")


def close_year_view(request):
    current_year = now().year
    year_purchases = Purchase.objects.filter(date_of_purchase__year=current_year)
    yearly_total = year_purchases.aggregate(total=Sum('total_cost'))['total'] or 0
    year_purchases.update(archived=True)
    messages.success(request, f"Closed year {current_year}. Total spent: ${yearly_total:.2f}")
    return redirect('totals')


def select_year_start(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        if start_date_str:
            try:
                start_date = native_datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return render(request, 'select_year_start.html')
            purchases = Purchase.objects.filter(date_of_purchase__gte=start_date)
            total = purchases.aggregate(total=Sum('total_cost'))['total'] or 0
            context = {'start_date': start_date, 'total': round(total, 2), 'purchases': purchases}
            return render(request, 'select_year_start.html', context)
    return render(request, 'select_year_start.html')


# ----------------------
# Products, Stores, Shopping List
# ----------------------
def products(request):
    products = Product.objects.all()
    return render(request, 'prices/products.html', {'products': products})

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'prices/create_product.html', {'form': form})

def store_list(request):
    stores = Store.objects.all().order_by('name')
    return render(request, 'prices/store_list.html', {'stores': stores})

def store_edit(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('prices:store_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'prices/store_edit.html', {'form': form, 'store': store})

def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prices:store_list')
    else:
        form = StoreForm()
    return render(request, 'prices/stores.html', {'form': form})

def delete_store(request, store_id):
     item = get_object_or_404(Store, id=store_id)
     if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted.")
        return redirect('store_list')
     return render(request, 'prices:delete_store.html', {'store': item})

def shopping_list(request):
    store_filter = request.GET.get('store', '')
    product_filter = request.GET.get('product', '')

    items = ShoppingList.objects.all()

    if store_filter:
        items = items.filter(store__name__icontains=store_filter)
    if product_filter:
        items = items.filter(product__name__icontains=product_filter)

    # Add pagination if needed
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'prices/shopping_list.html', {
        'items': page_obj,
    })


def create_shopping_list(request):
    if request.method == 'POST':
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            shopping_item = form.save(commit=False)
            shopping_item.total = shopping_item.quantity * shopping_item.product.price
            shopping_item.save()
            messages.success(request, "Shopping list item added.")
            return redirect('shopping_list')
    else:
        form = ShoppingListForm()

    return render(request, 'prices/create_shopping_list.html', {'form': form})
def edit_shopping_list(request, item_id):
    item = get_object_or_404(ShoppingList, id=item_id)
    if request.method == 'POST':
        form = ShoppingListForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.total = item.quantity * item.product.price
            item.save()
            messages.success(request, "Item updated.")
            return redirect('shopping_list')
    else:
        form = ShoppingListForm(instance=item)
    return render(request, 'prices/edit_shopping_list.html', {'form': form})


def delete_shopping_list(request, item_id):
    item = get_object_or_404(ShoppingList, id=item_id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted.")
        return redirect('shopping_list')
    return render(request, 'prices/delete_shopping_list.html', {'item': item})



def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'price_cost': product.price,
        'package_unit_type': product.packaging,
    })
    
def edit_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            return redirect('prices:home')
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, 'purchase/edit_purchase.html', {'form': form, 'purchase': purchase})    