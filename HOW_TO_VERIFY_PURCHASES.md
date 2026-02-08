# HOW TO CHECK YOUR DAILY STORE PURCHASES

## Quick Start - 3 Simple Steps:

### Step 1: Go to the Home Page
- Open your browser to: `http://localhost:8000/`

### Step 2: Set Your Filters
In the filter section, select:
- **Store**: Choose the store (e.g., "Walmart")
- **Date**: Leave blank or pick a specific date
- **Group By**: Select **"Store + Date"**

### Step 3: Click "Filter"
You'll see blue cards showing each day's purchases for that store!

---

## What You'll See:

When you use **"Store + Date"** grouping, you get:

```
┌─────────────────────────────────────────────────────────┐
│ 🏪 Walmart  |  📅 2026-02-05                            │
│                              3 items    Total: $45.67   │
├─────────────────────────────────────────────────────────┤
│ Item         │ Package │ Qty │ Price  │ Total  │ Edit  │
├─────────────────────────────────────────────────────────┤
│ Milk         │ litre   │ 2   │ $4.99  │ $9.98  │ [Edit]│
│ Bread        │ loaf    │ 1   │ $3.49  │ $3.49  │ [Edit]│
│ Eggs         │ dozen   │ 3   │ $5.99  │ $17.97 │ [Edit]│
├─────────────────────────────────────────────────────────┤
│                         Subtotal:        $45.67         │
└─────────────────────────────────────────────────────────┘
```

Each card shows:
- ✅ Store name and date in the header (blue)
- ✅ Number of items you entered
- ✅ Total amount for that day
- ✅ Every individual purchase listed
- ✅ Edit button for each purchase

---

## Example Use Cases:

### Check Yesterday's Walmart Purchases:
1. **Store**: Walmart
2. **Date**: 2026-02-06 (or leave blank to see all days)
3. **Group By**: Store + Date
4. **Click Filter**

Result: See all Walmart purchases organized by date with totals

### Verify Today's Entries:
1. **Store**: Choose your store
2. **Date**: Today's date
3. **Group By**: Store + Date
4. **Click Filter**

Result: See only today's purchases from that store

### Check All Purchases This Week:
1. **Store**: Leave blank (All Stores)
2. Click **"This Week"** button
3. **Group By**: Store + Date
4. **Click Filter**

Result: See all stores grouped by date for the past 7 days

---

## Verification Checklist:

When checking your entries, look for:
- ✅ **Correct store name** in the blue header
- ✅ **Right date** in the blue header
- ✅ **All items** are listed (count matches your receipt)
- ✅ **Quantities** are correct
- ✅ **Prices** match your receipt
- ✅ **Total** matches your receipt total
- ⚠️ If something's wrong, click **Edit** to fix it

---

## Common Mistakes to Catch:

1. **Wrong quantity**: Check the Qty column
2. **Typo in price**: Check the Price column  
3. **Missing item**: Count should match items on receipt
4. **Wrong date**: Check date in blue header
5. **Wrong store**: Check store name in blue header
6. **Duplicate entry**: Look for repeated items

---

## Tips:

- **No grouping selected?** You won't see the blue cards! Make sure "Store + Date" is selected.
- **Home page only shows current year by default** - if your purchases are from last year, select that year first.
- **Use "Purchase List" page** (`/purchase_list/`) to see ALL purchases regardless of year.
- **The blue cards appear ABOVE** the regular purchase table.
- Each blue card is one store + one date combination.

---

## Still Not Seeing Data?

If you select filters and click "Filter" but see nothing:

1. Check you selected **"Store + Date"** in the Group By dropdown
2. Make sure you have purchases in the database for that store/date
3. If on Home page, check the **Year** dropdown - it defaults to current year
4. Try the **Purchase List** page instead: `http://localhost:8000/purchase_list/`

---

## Pages with This Feature:

✅ **Home Page**: `http://localhost:8000/`
✅ **Purchase List**: `http://localhost:8000/purchase_list/`

Both pages work the same way!
