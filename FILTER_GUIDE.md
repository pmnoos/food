# Filter Guide - How to Use the New Grouping Filters

## Where to Find the Filters

The new grouping filters are available on these pages:

1. **Home Page** - http://localhost:8000/ (or your main URL)
2. **Purchase List Page** - http://localhost:8000/purchase_list/

## How to Use the Filters

### Step-by-Step Example: View Purchases by Store and Date

1. **Go to the Home Page or Purchase List Page**

2. **Select your filters:**
   - **Store**: Choose a store from the dropdown (e.g., "Walmart")
   - **Date**: Leave blank or select a specific date range
   - **Group By**: Select "Store + Date" from the dropdown

3. **Click the "Filter" button**

4. **View the Results:**
   - You'll see a **blue highlighted table** at the top showing:
     - Store Name
     - Date of Purchase
     - Number of Purchases (in a badge)
     - Total Amount Spent

### Example Scenarios:

#### Scenario 1: Check all Walmart purchases by date
- **Store**: Select "Walmart"
- **Group By**: Select "Store + Date"
- **Click Filter**
- Result: See each day's Walmart purchases with totals

#### Scenario 2: See daily totals for all stores
- **Store**: Leave blank (All Stores)
- **Group By**: Select "By Date"
- **Click Filter**
- Result: See total spending per day across all stores

#### Scenario 3: Verify specific date and store
- **Store**: Select "Target"
- **Date**: Enter specific date (e.g., 2026-02-05)
- **Group By**: Select "Store + Date"
- **Click Filter**
- Result: See Target purchases for that specific date

#### Scenario 4: Check product prices
- **Product**: Select a product name
- **Group By**: Select "By Product"
- **Click Filter**
- Result: See purchase count, average price, and total for that product

## Troubleshooting

### If filters aren't working:

1. **Make sure you're on the right page:**
   - Home page: `/` 
   - Purchase List: `/purchase_list/`

2. **After selecting filters, click "Filter" button**

3. **The grouped results appear in a BLUE TABLE above the regular purchase list**

4. **If you don't see grouped data:**
   - Make sure you selected an option in the "Group By" dropdown
   - Check that there are purchases matching your filter criteria

### Testing the Filter:

Try this simple test:
1. Go to Home page
2. Don't select any filters except:
   - **Group By**: "By Store"
3. Click "Filter"
4. You should see a blue table listing all stores with their total purchases

## Filter Options Explained:

- **No Grouping**: Shows regular detailed list only
- **Store + Date**: Groups by store name AND date (perfect for verifying daily receipts)
- **By Date**: Groups all purchases by date only
- **By Store**: Groups all purchases by store only  
- **By Product**: Groups by product with average pricing

## What the Grouped Table Shows:

The grouped summary table displays:
- **Store/Date/Product**: Depending on grouping selected
- **Purchases**: Count of individual purchase entries (shown as a badge)
- **Total**: Sum of all purchases in that group (in bold, right-aligned)
- **Avg Price**: (Only for product grouping) Average price paid

This table appears **BEFORE** the regular detailed purchase list, making it easy to verify your data entry is correct.
