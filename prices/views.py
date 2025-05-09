# prices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now
from django.db.models import Sum
from datetime import datetime, timedelta
import subprocess, os, logging

from .models import Product, Store, ShoppingList, Purchase
from .forms import ProductForm, StoreForm, ShoppingListForm, PurchaseForm, YearStartForm

logger = logging.getLogger(__name__)

def home(request):
    current_year = now().year
    store_filter = request.GET.get('store', '')
    product_filter = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    records_per_page = request.GET.get('records_per_page', 10)
    page_number = request.GET.get('page', 1)

    purchases = Purchase.objects.filter(date_of_purchase__year=current_year)

    if store_filter:
        purchases = purchases.filter(store_name__icontains=store_filter)
    if product_filter:
        purchases = purchases.filter(item_product__icontains=product_filter)
    if date_filter:
        purchases = purchases.filter(date_of_purchase=date_filter)

    purchases = purchases.order_by('-date_of_purchase')
    paginator = Paginator(purchases, records_per_page)
    page_obj = paginator.get_page(page_number)

    total_spent = purchases.aggregate(total_spent=Sum('total_cost'))['total_spent'] or 0
    total_running = sum(p.price_cost * p.quantity for p in purchases)

    return render(request, 'purchase/home.html', {
        'purchases': page_obj,
        'total_running': total_running,
        'total_spent': total_spent,
        'store_filter': store_filter,
        'product_filter': product_filter,
        'date_filter': date_filter,
        'records_per_page': records_per_page,
    })

def totals_view(request):
    today = now().date()
    current_year = today.year
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    selected_month = request.GET.get('month')
    month_filter = int(selected_month) if selected_month else None
    purchases_query = Purchase.objects.filter(date_of_purchase__year=current_year)

    if month_filter:
        purchases_query = purchases_query.filter(date_of_purchase__month=month_filter)

    store_totals = purchases_query.values('store_name').annotate(total=Sum('total_cost')).order_by('-total')
    weekly_total = purchases_query.filter(date_of_purchase__gte=start_of_week).aggregate(total=Sum('total_cost'))['total'] or 0
    monthly_total = purchases_query.filter(date_of_purchase__gte=start_of_month).aggregate(total=Sum('total_cost'))['total'] or 0
    yearly_total = purchases_query.aggregate(total=Sum('total_cost'))['total'] or 0

    return render(request, 'totals.html', {
        'store_totals': store_totals,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
        'selected_month': selected_month,
    })



def purchase_list(request):
    # Get filter parameters from the request
    store_filter = request.GET.get('store', '').strip()
    product_filter = request.GET.get('product', '').strip()
    date_filter = request.GET.get('date', '').strip()
    records_per_page = int(request.GET.get('records_per_page', 10))  # Default to 10 records per page

    # Base query for purchases
    purchases_query = Purchase.objects.all()

    # Apply filters if provided
    if store_filter:
        purchases_query = purchases_query.filter(store_name__icontains=store_filter)
    if product_filter:
        purchases_query = purchases_query.filter(item_product__icontains=product_filter)
    if date_filter:
        try:
            # Validate the date format before filtering
            datetime.strptime(date_filter, '%Y-%m-%d')
            purchases_query = purchases_query.filter(date_of_purchase=date_filter)
        except ValueError:
            pass

    # Calculate the total sum of purchases for the filtered query
    total_sum = purchases_query.aggregate(total=Sum('total_cost'))['total'] or 0

    # Paginate the results
    paginator = Paginator(purchases_query, records_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get unique store and product choices for the filter dropdowns
    store_choices = Purchase.objects.values_list('store_name', flat=True).distinct()
    product_choices = Purchase.objects.values_list('item_product', flat=True).distinct()

    return render(request, 'prices/purchase_list.html', {
        'purchases': page_obj,
        'store_choices': store_choices,
        'product_choices': product_choices,
        'records_per_page_options': [10, 30, 50],
        'total_sum': total_sum,  # Pass the total sum to the template
    })

def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            # Save the last entered store name and date in the session
            request.session['last_store_name'] = form.cleaned_data['store_name']
            request.session['last_date_of_purchase'] = str(form.cleaned_data['date_of_purchase'])
            messages.success(request, f"Purchase added for {purchase.store_name} on {purchase.date_of_purchase}.")
            # Redirect back to the add purchase page to allow entering another purchase
            return redirect('add_purchase')  # Redirect to the same page
    else:
        # Pre-fill the form with the last entered store name and date
        form = PurchaseForm(initial={
            'store_name': request.session.get('last_store_name', ''),
            'date_of_purchase': request.session.get('last_date_of_purchase', ''),
        })

    return render(request, 'purchase/add_purchase.html', {'form': form})

    return render(request, 'purchase/add_purchase.html', {'form': form})

def edit_purchase(request, purchase_id):
    logger.info("Edit purchase view triggered")
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if request.method == 'POST' and 'save' in request.POST:
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase updated successfully.")
            return redirect('purchase_list')
    else:
        form = PurchaseForm(instance=purchase)

    return render(request, 'purchase/edit_purchase.html', {'form': form, 'purchase': purchase})

def delete_purchase(request, purchase_id):
    logger.info("Delete purchase view triggered")
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, "Purchase deleted successfully.")
        return redirect('purchase_list')

    return render(request, 'purchase/delete_confirmation.html', {'purchase': purchase})

def calculator_view(request):
    calculator_path = os.path.join(settings.BASE_DIR, 'prices', 'calculator.py')
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
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            purchases = Purchase.objects.filter(date_of_purchase__gte=start_date)
            total = purchases.aggregate(total=Sum('total_cost'))['total'] or 0
            context = {'start_date': start_date, 'total': round(total, 2), 'purchases': purchases}
            return render(request, 'select_year_start.html', context)
    return render(request, 'select_year_start.html')

def index(request):
    return render(request, 'prices/index.html')

def products(request):
    products = Product.objects.all()
    return render(request, 'prices/products.html', {'products': products})

def stores(request):
    stores = Store.objects.all()
    return render(request, 'prices/stores.html', {'stores': stores})

def shopping_list(request):
    shopping_list = ShoppingList.objects.all()
    return render(request, 'prices/shopping_list.html', {'shopping_list': shopping_list})

def create_shopping_list(request):
    if request.method == 'POST':
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shopping_list')
    else:
        form = ShoppingListForm()
    return render(request, 'prices/create_shopping_list.html', {'form': form})

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'prices/create_product.html', {'form': form})

def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_list')
    else:
        form = StoreForm()
    return render(request, 'prices/stores.html', {'form': form})
