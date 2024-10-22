from .models import Purchase
from decimal import Decimal

purchases = Purchase.objects.all().order_by('id')
running_total = Decimal('0.00')

for purchase in purchases:
    running_total += purchase.total_cost
    purchase.running_total = running_total
    purchase.save()