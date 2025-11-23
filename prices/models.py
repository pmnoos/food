from django.db import models
from django.db.models import Sum
from decimal import Decimal
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Increased max_digits for larger prices
    packaging = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} - {self.price} - {self.packaging}'
    
class Store(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class ShoppingList(models.Model):  # Class names should be capitalized
    date = models.DateField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shopping_lists')  # Added related_name for clarity
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Increased max_digits for larger totals

    def __str__(self):
        return f'{self.product} - {self.store} - {self.quantity} - {self.date}'





class Purchase(models.Model):
    store_name = models.CharField(max_length=255)
    date_of_purchase = models.DateField()
    item_product = models.CharField(max_length=255)
    package_unit_type = models.CharField(max_length=50)  # e.g., kilo, litre, can
    price_cost = models.DecimalField(max_digits=10, decimal_places=4)
    quantity = models.DecimalField(max_digits=8, decimal_places=4) 
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    running_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    year = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set year from date if not already set
        if self.date_of_purchase and not self.year:
            self.year = self.date_of_purchase.year
            
        # Calculate total cost
        self.total_cost = self.price_cost * self.quantity
        
        # Calculate running total
        if self.pk is None:  # Only calculate running total for new purchases
            previous_total = Purchase.objects.aggregate(Sum('total_cost'))['total_cost__sum'] or Decimal('0.00')
            self.running_total = previous_total + self.total_cost
        else:
            # If updating an existing purchase, you may want to recalculate the running total
            # This logic can be adjusted based on your requirements
            self.running_total = self.total_cost  # Adjust as needed for updates

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_product} from {self.store_name} on {self.date_of_purchase}"
