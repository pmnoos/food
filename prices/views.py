from django.shortcuts import render,redirect,  get_object_or_404
from .models import Product, Store, ShoppingList, Purchase
from .forms import  ProductForm, StoreForm, StoreForm, ShoppingListForm, PurchaseForm
from django.db.models import Sum
from decimal import Decimal
from django.core.paginator import Paginator

def home(request):
    store_filter = request.GET.get('store', '')
    product_filter = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    records_per_page = request.GET.get('records_per_page', 10)  # Default to 10 records per page
    page_number = request.GET.get('page', 1)  # Get the current page number

    purchases = Purchase.objects.all()

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
            # Store the store name and date in the session
            request.session['store_name'] = form.cleaned_data['store_name']
            request.session['date_of_purchase'] = form.cleaned_data['date_of_purchase']
            
            form.save()  # Save the new purchase to the database
            return redirect('purchase_list')  # Redirect to the purchase list after saving
    else:
        # Pre-fill the form with session values if they exist
        store_name = request.session.get('store_name', '')
        date_of_purchase = request.session.get('date_of_purchase', '')
        form = PurchaseForm(initial={
            'store_name': store_name,
            'date_of_purchase': date_of_purchase,
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





def purchase_list(request):
    store_filter = request.GET.get('store', '')
    product_filter = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    sort_order = request.GET.get('sort', 'asc')  # Default to ascending order

    purchases = Purchase.objects.all()

    # Filter by store name if provided
    if store_filter:
        purchases = purchases.filter(store_name__icontains=store_filter)
    
    # Filter by product name if provided
    if product_filter:
        purchases = purchases.filter(item_product__icontains=product_filter)

    # Filter purchases by the exact date if provided
    if date_filter:
        purchases = purchases.filter(date_of_purchase=date_filter)

    # Apply sorting based on the sort_order parameter
    if sort_order == 'desc':
        purchases = purchases.order_by('-date_of_purchase')  # Descending order
    else:
        purchases = purchases.order_by('date_of_purchase')  # Ascending order

    # Calculate the total amount spent at the store on the specified date
    total_spent = purchases.aggregate(total_spent=Sum('total_cost'))['total_spent'] or 0

    # Calculate the running total for display
    total_running = sum(purchase.price_cost * purchase.quantity for purchase in purchases)

    return render(request, 'purchase/purchase_list.html', {
        'purchases': purchases,
        'total_running': total_running,
        'total_spent': total_spent,
        'store_filter': store_filter,
        'product_filter': product_filter,
        'date_filter': date_filter,
        'sort_order': sort_order,  # Pass the sort order to the template
    })
def add_purchase(request):
    if request.method == 'POST':
        # Get the price cost and quantity from the form and convert to Decimal
        price_cost = Decimal(request.POST.get('price_cost', 0))
        quantity = Decimal(request.POST.get('quantity', 0))
        
        # Create a new Purchase object
        purchase = Purchase(
            store_name=request.POST.get('store_name'),
            date_of_purchase=request.POST.get('date_of_purchase'),
            item_product=request.POST.get('item_product'),
            package_unit_type=request.POST.get('package_unit_type'),
            price_cost=price_cost,
            quantity=quantity
        )
        
        # Save the purchase object to the database
        purchase.save()  # This will automatically calculate total_cost and running_total
        
        return redirect('purchase_list')  # Redirect to the purchase list after saving
    else:
        form = PurchaseForm()

    return render(request, 'purchase/add_purchase.html', {'form': form})




def edit_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            return redirect('purchase_list')  # Redirect to the purchase list after saving
    else:
        form = PurchaseForm(instance=purchase)
    
    return render(request, 'purchase/edit_purchase.html', {'form': form})

# View to delete a purchase
def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':
        purchase.delete()
        return redirect('purchase_list')  # Redirect to the purchase list after deletion
    
    return render(request, 'purchase/delete_confirmation.html', {'purchase': purchase})