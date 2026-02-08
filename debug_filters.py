"""
Quick Debug Script - Check if filters are working
Run this to see what data exists in your database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_costs.settings')
django.setup()

from prices.models import Purchase
from datetime import datetime

print("=" * 60)
print("PURCHASE DATA CHECK")
print("=" * 60)

# Get all purchases
all_purchases = Purchase.objects.all()
print(f"\nTotal purchases in database: {all_purchases.count()}")

# Get unique stores
stores = Purchase.objects.values_list('store_name', flat=True).distinct()
print(f"\nStores in database:")
for store in stores:
    if store:
        count = Purchase.objects.filter(store_name=store).count()
        total = sum(p.total_cost for p in Purchase.objects.filter(store_name=store))
        print(f"  - {store}: {count} purchases, ${total:.2f}")

# Get date range
dates = Purchase.objects.values_list('date_of_purchase', flat=True).order_by('date_of_purchase')
if dates:
    print(f"\nDate range:")
    print(f"  Earliest: {dates.first()}")
    print(f"  Latest: {dates.last()}")
    
# Get current year purchases
current_year = datetime.now().year
current_year_purchases = Purchase.objects.filter(date_of_purchase__year=current_year)
print(f"\nPurchases in {current_year}: {current_year_purchases.count()}")

# Show sample data
print(f"\nSample of recent purchases:")
recent = Purchase.objects.order_by('-date_of_purchase')[:5]
for p in recent:
    print(f"  {p.date_of_purchase} | {p.store_name} | {p.item_product} | ${p.total_cost}")

print("\n" + "=" * 60)
print("FILTER TEST")
print("=" * 60)

# Test grouping by store and date
from django.db.models import Sum, Count

print("\nGroup by Store + Date:")
grouped = Purchase.objects.values('store_name', 'date_of_purchase').annotate(
    total=Sum('total_cost'),
    count=Count('id')
).order_by('-date_of_purchase', 'store_name')[:10]

for item in grouped:
    print(f"  {item['store_name']} | {item['date_of_purchase']} | {item['count']} purchases | ${item['total']:.2f}")

print("\n" + "=" * 60)
print("URL EXAMPLES FOR TESTING")
print("=" * 60)
print("\nTry these URLs in your browser:")
print(f"1. Home with Store+Date grouping:")
print(f"   http://localhost:8000/?group_by=store_date")
print(f"\n2. Purchase list with specific store:")
if stores:
    first_store = [s for s in stores if s][0] if any(stores) else "YourStore"
    print(f"   http://localhost:8000/purchase_list/?store={first_store}&group_by=store_date")
print(f"\n3. All purchases grouped by date:")
print(f"   http://localhost:8000/?group_by=date")
print(f"\n4. All purchases grouped by store:")
print(f"   http://localhost:8000/purchase_list/?group_by=store")

print("\n" + "=" * 60)
