#!/usr/bin/env python
"""
Cleanup script to merge duplicate store names in the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_costs.settings')
django.setup()

from prices.models import Purchase

def cleanup_store_names():
    """Clean up and merge duplicate store names."""
    
    # Define mapping of incorrect names to correct names
    store_corrections = {
        'Aldi ': 'Aldi',
        'BWS ': 'BWS',
        "Dan Murphy's ": "Dan Murphy's",
        'Footes Pharmacy ': 'Footes Pharmacy',
        "Foote's Pharmacy's ": 'Footes Pharmacy',
        'Woolworths ': 'Woolworths',
        'Amplol ': 'Amplol',
    }
    
    total_updated = 0
    
    print("Starting store name cleanup...")
    print("-" * 60)
    
    for incorrect_name, correct_name in store_corrections.items():
        count = Purchase.objects.filter(store_name=incorrect_name).count()
        if count > 0:
            print(f"Merging '{incorrect_name}' -> '{correct_name}' ({count} purchases)")
            Purchase.objects.filter(store_name=incorrect_name).update(store_name=correct_name)
            total_updated += count
    
    # Also trim all store names just in case there are other spaces
    print("\nTrimming all store names...")
    all_purchases = Purchase.objects.all()
    trim_count = 0
    for purchase in all_purchases:
        original = purchase.store_name
        if original:
            trimmed = original.strip()
            if original != trimmed:
                purchase.store_name = trimmed
                purchase.save()
                trim_count += 1
                print(f"  Trimmed: '{original}' -> '{trimmed}'")
    
    print("-" * 60)
    print(f"Total purchases updated: {total_updated + trim_count}")
    
    # Show final store list
    print("\n" + "=" * 60)
    print("Final unique store names:")
    print("=" * 60)
    stores = Purchase.objects.values_list('store_name', flat=True).distinct().order_by('store_name')
    for store in stores:
        count = Purchase.objects.filter(store_name=store).count()
        print(f"  {store:<30} ({count} purchases)")
    
    print("\nCleanup complete!")

if __name__ == '__main__':
    cleanup_store_names()
