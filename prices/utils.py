# prices/utils.py

from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .models import Purchase


def apply_purchase_filters(purchases, request):
    """
    Apply common filters to a Purchase queryset based on request parameters.
    Returns filtered queryset and filter values.
    """
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_day = request.GET.get('day')
    selected_store = request.GET.get('store', '')
    selected_product = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    
    if selected_year and selected_year.isdigit():
        purchases = purchases.filter(date_of_purchase__year=int(selected_year))
    if selected_month and selected_month.isdigit():
        purchases = purchases.filter(date_of_purchase__month=int(selected_month))
    if selected_day and selected_day.isdigit():
        purchases = purchases.filter(date_of_purchase__day=int(selected_day))
    if selected_store:
        purchases = purchases.filter(store_name=selected_store)
    if selected_product:
        purchases = purchases.filter(item_product=selected_product)
    if date_filter:
        purchases = purchases.filter(date_of_purchase=date_filter)
    
    return purchases, {
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_day': selected_day,
        'selected_store': selected_store,
        'selected_product': selected_product,
        'date_filter': date_filter,
    }


def calculate_totals(purchases, request=None):
    """
    Calculate various totals for a Purchase queryset.
    Returns dictionary with total values.
    """
    current_date = now().date()
    current_year = current_date.year
    current_month = current_date.month
    
    # Calculate weekly total from the last 7 days (unfiltered, for true weekly total)
    week_ago = current_date - timedelta(days=7)
    weekly_total = Purchase.objects.filter(date_of_purchase__gte=week_ago).aggregate(total=Sum('total_cost'))['total'] or 0
    
    # Calculate monthly total for current month (unfiltered, for true monthly total)
    monthly_total = Purchase.objects.filter(
        date_of_purchase__year=current_year,
        date_of_purchase__month=current_month
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    # Calculate yearly total for current year (unfiltered, for true yearly total)
    yearly_total = Purchase.objects.filter(
        date_of_purchase__year=current_year
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    # If filters are applied, also calculate filtered totals
    filtered_total = purchases.aggregate(total=Sum('total_cost'))['total'] or 0
    
    return {
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
        'filtered_total': filtered_total,
    }


def get_filter_choices():
    """
    Get common filter choices for dropdowns.
    Returns dictionary with choice lists.
    """
    year_choices = sorted(set(p.date_of_purchase.year for p in Purchase.objects.exclude(date_of_purchase__isnull=True)), reverse=True)
    month_choices = list(range(1, 13))
    day_choices = list(range(1, 32))
    store_choices = sorted(set(p.store_name for p in Purchase.objects.exclude(store_name__isnull=True)))
    product_choices = sorted(set(p.item_product for p in Purchase.objects.exclude(item_product__isnull=True)))
    
    return {
        'year_choices': year_choices,
        'month_choices': month_choices,
        'day_choices': day_choices,
        'store_choices': store_choices,
        'product_choices': product_choices,
    }
