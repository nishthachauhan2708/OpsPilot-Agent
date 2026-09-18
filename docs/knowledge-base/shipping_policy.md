# UrbanCart Shipping & Delivery Policy

## 1. Shipping Methods & Expected Delivery Windows
- **Standard Shipping**: 3 - 5 business days.
- **Express Shipping**: 1 - 2 business days.
- **Same-Day Local Delivery**: Available in select metro zones for orders placed before 11:00 AM.

## 2. Order Delay Classification
An order is officially flagged as **`delayed`** in OpsPilot if:
1. Current date exceeds the `expected_delivery` date.
2. Carrier tracking status has not updated in over **48 hours** while order status remains `shipped` or `in_transit`.
3. Order processing time at warehouse exceeds **24 hours** without handover to logistics carrier.

## 3. Customer Compensation for Delays
- **Minor Delay (1 - 2 days past expected delivery)**: OpsPilot drafts proactive notification message with tracking update.
- **Significant Delay (3+ days past expected delivery)**: Customer is eligible for a $10 UrbanCart credit code or free return shipping voucher.
- **Lost Package (No carrier scan for 7+ days)**: Eligible for immediate re-shipment or full refund.
