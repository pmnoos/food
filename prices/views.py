# prices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now
from django.db.models import Sum, Q
from datetime import datetime as native_datetime, timedelta
import subprocess, os, logging
from django.http import JsonResponse

from .models import Product, Store, ShoppingList, Purchase
from .forms import ProductForm, StoreForm, ShoppingListForm, PurchaseForm, YearStartForm
from .utils import apply_purchase_filters, calculate_totals, get_filter_choices, get_grouped_purchases
from .find_replace_form import FindReplaceForm

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
    
    # Get grouped data if requested
    group_by = filter_values.get('group_by', '')
    grouped_data = get_grouped_purchases(purchases, group_by) if group_by else None

    context = {
        'purchases': page_obj,
        'total_running': total_running,
        'total_spent': total_spent,
        'records_per_page': records_per_page,
        'grouped_data': grouped_data,
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
    
    # Calculate the total for percentage calculations
    # Use filtered_total if filters are applied, otherwise use yearly_total
    has_filters = any([
        filter_values.get('selected_year'),
        filter_values.get('selected_month'),
        filter_values.get('selected_store'),
        filter_values.get('selected_product'),
        filter_values.get('date_filter'),
        filter_values.get('start_date'),
        filter_values.get('end_date'),
    ])
    percentage_base = totals['filtered_total'] if has_filters else totals['yearly_total']

    context = {
        'store_totals': store_totals,
        'purchases': purchases.order_by('-date_of_purchase'),
        'percentage_base': percentage_base,
        'has_filters': has_filters,
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
    
    # Get grouped data if requested
    group_by = filter_values.get('group_by', '')
    grouped_data = get_grouped_purchases(purchases, group_by) if group_by else None
    
    store_totals = purchases.values('store_name').annotate(total=Sum('total_cost')).order_by('-total')

    context = {
        'purchases': purchases.order_by('-date_of_purchase'),
        'store_totals': store_totals,
        'grouped_data': grouped_data,
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
            if purchase.store_id:
                request.session['last_store_id'] = purchase.store_id
            else:
                request.session['last_store_id'] = purchase.store_name
            request.session['last_date_of_purchase'] = str(purchase.date_of_purchase)
            messages.success(request, f"Purchase added for {purchase.store_name} on {purchase.date_of_purchase}.")
            return redirect('prices:add_purchase')
    else:
        initial = {}
        # Allow prefill via query params from store list
        store_id = request.GET.get('store_id')
        store_name_qs = request.GET.get('store_name')
        if store_id and not store_name_qs:
            try:
                store_obj = Store.objects.get(id=store_id)
                initial['store'] = store_obj.id
            except Store.DoesNotExist:
                pass
        elif store_name_qs:
            try:
                initial_store = Store.objects.get(name=store_name_qs)
                initial['store'] = initial_store.id
            except Store.DoesNotExist:
                # fallback: leave store empty; store_name will sync on save if text provided via other means
                pass
        last_store_id = request.session.get('last_store_id')
        if last_store_id:
            # If last_store_id is numeric it may reference a Store, else it's the name string
            if isinstance(last_store_id, int):
                try:
                    initial['store'] = Store.objects.get(id=last_store_id).id
                except Store.DoesNotExist:
                    initial['store'] = None
            else:
                try:
                    initial['store'] = Store.objects.get(name=last_store_id).id
                except Store.DoesNotExist:
                    initial['store'] = None
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

def get_last_purchase(request):
    """API endpoint to get the last purchase details for a given item name"""
    item_name = request.GET.get('item_name', '').strip()
    
    if not item_name:
        return JsonResponse({'found': False})
    
    # Find the most recent purchase for this item
    last_purchase = Purchase.objects.filter(
        item_product__iexact=item_name
    ).order_by('-date_of_purchase', '-id').first()
    
    if last_purchase:
        return JsonResponse({
            'found': True,
            'price_cost': str(last_purchase.price_cost),
            'quantity': str(last_purchase.quantity),
            'package_unit_type': last_purchase.package_unit_type,
        })
    else:
        return JsonResponse({'found': False})


def price_changes_report(request):
    """Report showing monthly price changes for items over time"""
    from django.db.models import Min, Max, Avg, Count
    from decimal import Decimal
    from datetime import datetime
    from collections import defaultdict
    
    # Get filter parameters
    current_year = now().year
    selected_year = request.GET.get('year', str(current_year))
    selected_month = request.GET.get('month', '')
    
    # Start with all purchases
    all_purchases = Purchase.objects.all()
    
    # Apply year filter (default to current year)
    if selected_year:
        try:
            year_int = int(selected_year)
            all_purchases = all_purchases.filter(date_of_purchase__year=year_int)
        except ValueError:
            pass
    
    # Apply month filter if selected
    if selected_month:
        try:
            month_int = int(selected_month)
            all_purchases = all_purchases.filter(date_of_purchase__month=month_int)
        except ValueError:
            pass
    
    # Get all items with their price history
    items = all_purchases.values('item_product', 'package_unit_type').distinct()
    
    price_history = []
    
    for item in items:
        # Get all purchases of this item within the filtered time period
        purchases = all_purchases.filter(
            item_product=item['item_product'],
            package_unit_type=item['package_unit_type']
        ).order_by('date_of_purchase')
        
        if purchases.count() < 2:
            continue  # Skip items with only one purchase
        
        # Group by year-month and get average price per month
        monthly_data = defaultdict(lambda: {'total': 0, 'count': 0, 'dates': []})
        
        for p in purchases:
            month_key = p.date_of_purchase.strftime('%Y-%m')
            monthly_data[month_key]['total'] += float(p.price_cost)
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['dates'].append(p.date_of_purchase)
        
        # Calculate average price per month
        monthly_prices = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            avg_price = data['total'] / data['count']
            monthly_prices.append({
                'month': month_key,
                'month_display': datetime.strptime(month_key, '%Y-%m').strftime('%B %Y'),
                'avg_price': avg_price,
                'purchase_count': data['count']
            })
        
        if len(monthly_prices) < 1:
            continue  # Need at least 1 month to show
        
        # Get first and last month data
        first_month = monthly_prices[0]
        last_month = monthly_prices[-1]
        
        # Calculate price change
        price_change = last_month['avg_price'] - first_month['avg_price']
        
        if first_month['avg_price'] > 0:
            percent_change = (price_change / first_month['avg_price']) * 100
        else:
            percent_change = 0
        
        # Get overall stats
        all_prices = [m['avg_price'] for m in monthly_prices]
        min_price = min(all_prices)
        max_price = max(all_prices)
        avg_price = sum(all_prices) / len(all_prices)
        
        # Calculate most recent change (last 2 months)
        recent_change = 0
        recent_percent = 0
        if len(monthly_prices) >= 2:
            prev_month = monthly_prices[-2]
            recent_change = last_month['avg_price'] - prev_month['avg_price']
            if prev_month['avg_price'] > 0:
                recent_percent = (recent_change / prev_month['avg_price']) * 100
        
        price_history.append({
            'item_product': item['item_product'],
            'package_unit_type': item['package_unit_type'],
            'first_month': first_month['month_display'],
            'last_month': last_month['month_display'],
            'first_price': first_month['avg_price'],
            'last_price': last_month['avg_price'],
            'price_change': price_change,
            'percent_change': percent_change,
            'recent_change': recent_change,
            'recent_percent': recent_percent,
            'min_price': min_price,
            'max_price': max_price,
            'avg_price': avg_price,
            'total_purchases': purchases.count(),
            'months_tracked': len(monthly_prices),
            'monthly_prices': monthly_prices,
        })
    
    # Sort by recent percent change (most recent increases first)
    sort_by = request.GET.get('sort', 'recent_percent')
    reverse = request.GET.get('order', 'desc') == 'desc'
    
    if sort_by == 'recent_percent':
        price_history.sort(key=lambda x: x['recent_percent'], reverse=reverse)
    elif sort_by == 'percent_change':
        price_history.sort(key=lambda x: x['percent_change'], reverse=reverse)
    elif sort_by == 'recent_change':
        price_history.sort(key=lambda x: x['recent_change'], reverse=reverse)
    elif sort_by == 'item':
        price_history.sort(key=lambda x: x['item_product'], reverse=not reverse)
    
    # Filter options - default to showing increases only
    show_increases_only = request.GET.get('increases_only', 'true') == 'true'
    show_decreases_only = request.GET.get('decreases_only') == 'true'
    show_all = request.GET.get('show_all') == 'true'
    
    # Apply filters
    if show_decreases_only:
        price_history = [item for item in price_history if item['recent_change'] < 0]
    elif show_all:
        # Show everything including no change
        pass
    elif show_increases_only:
        # Default: only show increases
        price_history = [item for item in price_history if item['recent_change'] > 0]
    
    # Get available years for filter
    available_years = sorted(
        set(p.date_of_purchase.year for p in Purchase.objects.exclude(date_of_purchase__isnull=True)),
        reverse=True
    )
    
    context = {
        'price_history': price_history,
        'sort_by': sort_by,
        'order': request.GET.get('order', 'desc'),
        'show_increases_only': show_increases_only,
        'show_decreases_only': show_decreases_only,
        'show_all': show_all,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'available_years': available_years,
        'current_year': current_year,
    }
    
    return render(request, 'prices/price_changes.html', context)


def find_replace_tool(request):
    """Tool for finding and replacing values in purchase records"""
    results = None
    affected_count = 0
    preview_purchases = []
    
    if request.method == 'POST':
        form = FindReplaceForm(request.POST)
        if form.is_valid():
            field = form.cleaned_data['field_to_search']
            find_value = form.cleaned_data['find_value']
            replace_value = form.cleaned_data['replace_value']
            case_sensitive = form.cleaned_data['case_sensitive']
            preview_only = form.cleaned_data['preview_only']
            
            # Build query
            purchases = Purchase.objects.all()
            
            # Apply search filter
            if find_value:
                if field == 'date_of_purchase':
                    # Exact date match
                    purchases = purchases.filter(date_of_purchase=find_value)
                elif case_sensitive:
                    purchases = purchases.filter(**{f'{field}': find_value})
                else:
                    purchases = purchases.filter(**{f'{field}__iexact': find_value})
            else:
                # Find empty/null values
                purchases = purchases.filter(**{f'{field}__isnull': True}) | purchases.filter(**{f'{field}': ''})
            
            affected_count = purchases.count()
            
            if preview_only:
                # Show preview of what would be changed
                preview_purchases = list(purchases[:50])  # Limit to 50 for preview
                results = {
                    'preview': True,
                    'count': affected_count,
                    'message': f'Found {affected_count} record(s) that would be changed.',
                }
            else:
                # Actually apply the changes
                if affected_count > 0:
                    purchases.update(**{field: replace_value})
                    messages.success(
                        request,
                        f'Successfully updated {affected_count} record(s). '
                        f'Changed {field} from "{find_value or "(empty)"}" to "{replace_value}"'
                    )
                    results = {
                        'preview': False,
                        'count': affected_count,
                        'message': f'Successfully updated {affected_count} record(s).',
                    }
                else:
                    messages.info(request, 'No matching records found.')
                    results = {
                        'preview': False,
                        'count': 0,
                        'message': 'No matching records found.',
                    }
    else:
        form = FindReplaceForm()
    
    context = {
        'form': form,
        'results': results,
        'affected_count': affected_count,
        'preview_purchases': preview_purchases,
    }
    
    return render(request, 'prices/find_replace.html', context)


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

def store_purchases(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    purchases = Purchase.objects.filter(Q(store=store) | Q(store_name=store.name)).order_by('-date_of_purchase')
    # Reuse existing totals and filter helpers for consistency
    purchases, filter_values = apply_purchase_filters(purchases, request)
    totals = calculate_totals(purchases, request)
    filter_choices = get_filter_choices()

    context = {
        'purchases': purchases,
        'selected_store': store,
        **totals,
        **filter_values,
        **filter_choices,
    }
    return render(request, 'prices/purchase_list.html', context)

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