from django.shortcuts import render,redirect,  get_object_or_404
from .models import Product, Store, ShoppingList, Purchase
from .forms import  ProductForm, StoreForm, StoreForm, ShoppingListForm, PurchaseForm
from django.contrib import messages
import logging

# Configure logger
logger = logging.getLogger(__name__)
from django.db.models import Sum
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.core.paginator import Paginator
import subprocess
import os
import logging
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from datetime import datetime

from .models import Purchase

from .forms import YearStartForm

from datetime import timedelta
from django.db.models import Sum
from django.shortcuts import render
from django.utils.timezone import now
from .models import Purchase

def totals_view(request):
    today = now().date()
    current_year = today.year
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Get selected month from query parameters
    selected_month = request.GET.get('month')
    year_filter = current_year
    month_filter = int(selected_month) if selected_month else None

    # Filter purchases by year
    purchases_query = Purchase.objects.filter(date_of_purchase__year=year_filter)

    # Apply additional filter by selected month if provided
    if month_filter:
        purchases_query = purchases_query.filter(date_of_purchase__month=month_filter)

    # Totals per store
    store_totals = purchases_query.values('store_name').annotate(
        total=Sum('total_cost')
    ).order_by('-total')

    # Weekly, monthly, and yearly totals
    weekly_total = purchases_query.filter(date_of_purchase__gte=start_of_week).aggregate(
        total=Sum('total_cost')
    )['total'] or 0

    monthly_total = purchases_query.filter(date_of_purchase__gte=start_of_month).aggregate(
        total=Sum('total_cost')
    )['total'] or 0

    yearly_total = purchases_query.aggregate(total=Sum('total_cost'))['total'] or 0

    return render(request, 'totals.html', {
        'store_totals': store_totals,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
        'selected_month': selected_month,
    })


def home(request):
    current_year = now().year  # 🆕 Get the current year
    store_filter = request.GET.get('store', '')
    product_filter = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    records_per_page = request.GET.get('records_per_page', 10)  # Default to 10 records per page
    page_number = request.GET.get('page', 1)  # Get the current page number

    # 🆕 Only show purchases from the current year
    purchases = Purchase.objects.filter(date_of_purchase__year=current_year)

    # Filter by store name if provided
    if store_filter:
        purchases = purchases.filter(store_name__icontains=store_filter)
    
    # Filter by product name if provided
    if product_filter:
        purchases = purchases.filter(item_product__icontains=product_filter)

    # Filter purchases by the exact date if provided
    if date_filter:
        purchases = purchases.filter(date_of_purchase=date_filter)

    # Order the purchases by a specific field, e.g., date_of_purchase
    purchases = purchases.order_by('-date_of_purchase')  # Change this to your desired ordering field

    # Create a Paginator object
    paginator = Paginator(purchases, records_per_page)  # Paginate with the specified number of records
    page_obj = paginator.get_page(page_number)  # Get the current page of purchases

    # Calculate the total amount spent at the store on the specified date
    total_spent = purchases.aggregate(total_spent=Sum('total_cost'))['total_spent'] or 0

    # Calculate the running total for display
    total_running = sum(purchase.price_cost * purchase.quantity for purchase in purchases)

    return render(request, 'purchase/home.html', {
        'purchases': page_obj,  # Pass the paginated purchases to the template
        'total_running': total_running,
        'total_spent': total_spent,
        'store_filter': store_filter,
        'product_filter': product_filter,
        'date_filter': date_filter,
        'records_per_page': records_per_page,  # Pass the records per page to the template
    })


def purchase_list(request):
    purchases = Purchase.objects.all()
    return render(request, 'purchase_list.html', {'purchases': purchases})

def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()

            # Store selected values in session
            request.session['last_store_name'] = form.cleaned_data['store_name']
            request.session['last_date_of_purchase'] = str(form.cleaned_data['date_of_purchase'])

            messages.success(request, f"Purchase added for {purchase.store_name} on {purchase.date_of_purchase}.")
            return redirect('purchase_list')
    else:
        form = PurchaseForm(initial={
            'store_name': request.session.get('last_store_name', ''),
            'date_of_purchase': request.session.get('last_date_of_purchase', ''),
        })

    return render(request, 'purchase/add_purchase.html', {'form': form})


# Create your views here.
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
            return redirect('shopping_list')  # Redirect to a shopping list view
    else:
        form = ShoppingListForm()
    return render(request, 'prices/create_shopping_list.html', {'form': form})

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to a product list view
    else:
        form = ProductForm()
    return render(request, 'prices/create_product.html', {'form': form})

def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_list')  # Redirect to a store list view
    else:
        form = StoreForm()
    return render(request, 'prices/stores.html', {'form': form})


def calculator_view(request):
    calculator_path = os.path.join(settings.BASE_DIR, 'prices', 'calculator.py')

    try:
        # Run the textual calculator
        result = subprocess.run(
            ['python', calculator_path],
            capture_output=True,
            text=True
        )
        
        # Check for errors
        if result.returncode != 0:
            return HttpResponse(f"<h1>Error:</h1><pre>{result.stderr}</pre>")

        # Display calculator output
        return HttpResponse(f"<pre>{result.stdout}</pre>")
    except Exception as e:
        return HttpResponse(f"<h1>Error:</h1><pre>{str(e)}</pre>")





def purchase_list(request):
    # Get filter parameters from the request
    store_filter = request.GET.get('store', '').strip()
    product_filter = request.GET.get('product', '').strip()
    date_filter = request.GET.get('date', '').strip()

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
            # If the date is invalid, ignore the filter or handle the error
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

    # Calculate totals
    total_running = sum(purchase.price_cost * purchase.quantity for purchase in purchases_query)
    total_spent = purchases_query.aggregate(total=Sum('total_cost'))['total'] or 0

    # Paginate the results
    paginator = Paginator(purchases_query, 10)  # Show 10 purchases per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase/purchase_list.html', {
        'purchases': page_obj,
        'page_obj': page_obj,
        'store_filter': store_filter,
        'product_filter': product_filter,
        'date_filter': date_filter,
        'total_running': total_running,
        'total_spent': total_spent,
    })
from django.contrib import messages

def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()

            # Store selected values in session
            request.session['last_store_name'] = form.cleaned_data['store_name']
            request.session['last_date_of_purchase'] = str(form.cleaned_data['date_of_purchase'])

            messages.success(request, f"Purchase added for {purchase.store_name} on {purchase.date_of_purchase}.")
            return redirect('purchase_list')
    else:
        form = PurchaseForm(initial={
            'store_name': request.session.get('last_store_name', ''),
            'date_of_purchase': request.session.get('last_date_of_purchase', ''),
        })

    return render(request, 'purchase/add_purchase.html', {'form': form})

        
    # Save the purchase object to the database
    # Remove this redundant block as it duplicates functionality already present earlier in the `add_purchase` function.



def edit_purchase(request, purchase_id):
    import logging
    
    # Configure logger at the top of the file
    logger = logging.getLogger(__name__)
    
    # Add this line where the logger is used
    logger.info("Edit purchase view triggered")
def edit_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST' and 'save' in request.POST:  # Check for a specific action
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase updated successfully.")
            return redirect('purchase_list')  # Redirect to the purchase list after saving
    else:
        form = PurchaseForm(instance=purchase)
    
    return render(request, 'purchase/edit_purchase.html', {'form': form, 'purchase': purchase})

# View to delete a purchase
def delete_purchase(request, purchase_id):
    logger.info("Delete purchase view triggered")
def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':  # Ensure only POST requests are processed
        purchase.delete()
        messages.success(request, "Purchase deleted successfully.")
        return redirect('purchase_list')  # Redirect to the purchase list after deletion
    
    # If the request is not POST, show a confirmation page
    return render(request, 'purchase/delete_confirmation.html', {'purchase': purchase})


def close_year_view(request):
    current_year = now().year
    year_purchases = Purchase.objects.filter(date_of_purchase__year=current_year)

    yearly_total = year_purchases.aggregate(total=Sum('total_cost'))['total'] or 0

    # Optionally, save to a YearlySummary model if you want to track year totals:
    # YearlySummary.objects.create(year=current_year, total_spent=yearly_total)

    # Mark purchases as archived (you can add a BooleanField for `archived`)
    year_purchases.update(archived=True)

    messages.success(request, f"Closed year {current_year}. Total spent: ${yearly_total:.2f}")
    return redirect('totals')  # Adjust to your dashboard view

def select_year_start(request):
    if request.method == 'POST':
        # Get date from the form
        start_date_str = request.POST.get('start_date')
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            # Get purchases from start date onwards
            purchases = Purchase.objects.filter(date_of_purchase__gte=start_date)
            total = purchases.aggregate(total=Sum('total_cost'))['total'] or 0

            context = {
                'start_date': start_date,
                'total': round(total, 2),
                'purchases': purchases
            }
            return render(request, 'select_year_start.html', context)

    return render(request, 'select_year_start.html')
