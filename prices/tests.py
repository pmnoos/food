from django.test import TestCase, RequestFactory
from django.utils.timezone import datetime
from .models import Purchase
from .utils import calculate_totals, apply_purchase_filters

class TotalsPeriodTests(TestCase):
	def setUp(self):
		# Create purchases across different weeks, months, years
		# Year 2025
		Purchase.objects.create(store_name="Alpha", date_of_purchase=datetime(2025, 1, 3).date(), item_product="Milk", package_unit_type="litre", price_cost=2.50, quantity=2)
		Purchase.objects.create(store_name="Alpha", date_of_purchase=datetime(2025, 1, 5).date(), item_product="Bread", package_unit_type="loaf", price_cost=3.00, quantity=1)
		Purchase.objects.create(store_name="Beta",  date_of_purchase=datetime(2025, 2, 10).date(), item_product="Eggs", package_unit_type="dozen", price_cost=4.00, quantity=1)
		Purchase.objects.create(store_name="Beta",  date_of_purchase=datetime(2025, 2, 15).date(), item_product="Cheese", package_unit_type="kg", price_cost=8.00, quantity=0.5)
		# Year 2024
		Purchase.objects.create(store_name="Alpha", date_of_purchase=datetime(2024, 12, 28).date(), item_product="Butter", package_unit_type="kg", price_cost=6.00, quantity=1)

		self.factory = RequestFactory()

	def test_weekly_total(self):
		# Filter to week of 2025-01-05 (contains Jan 3 and Jan 5)
		request = self.factory.get('/', {
			'start_date': '2025-01-01',
			'end_date': '2025-01-07'
		})
		purchases = Purchase.objects.all()
		purchases, _ = apply_purchase_filters(purchases, request)
		totals = calculate_totals(purchases, request)
		expected = (2.50*2) + (3.00*1)
		self.assertAlmostEqual(float(totals['filtered_total']), expected, places=2)

	def test_monthly_total(self):
		# Filter to February 2025
		request = self.factory.get('/', {
			'start_date': '2025-02-01',
			'end_date': '2025-02-28'
		})
		purchases = Purchase.objects.all()
		purchases, _ = apply_purchase_filters(purchases, request)
		totals = calculate_totals(purchases, request)
		expected = (4.00*1) + (8.00*0.5)
		self.assertAlmostEqual(float(totals['filtered_total']), expected, places=2)

	def test_yearly_total(self):
		# Filter to entire year 2025
		request = self.factory.get('/', {
			'start_date': '2025-01-01',
			'end_date': '2025-12-31'
		})
		purchases = Purchase.objects.all()
		purchases, _ = apply_purchase_filters(purchases, request)
		totals = calculate_totals(purchases, request)
		expected = (2.50*2) + (3.00*1) + (4.00*1) + (8.00*0.5)
		self.assertAlmostEqual(float(totals['filtered_total']), expected, places=2)

	def test_cross_year_excludes(self):
		# Ensure 2024 purchase excluded when filtering 2025
		request = self.factory.get('/', {
			'start_date': '2025-01-01',
			'end_date': '2025-12-31'
		})
		purchases = Purchase.objects.all()
		purchases, _ = apply_purchase_filters(purchases, request)
		totals = calculate_totals(purchases, request)
		# 2024 purchase is 6.00*1, should not be included
		not_expected = 6.00
		self.assertNotAlmostEqual(float(totals['filtered_total']), not_expected, places=2)
