# Analytics Data Dictionary (sample document)

The analytics dataset is the TheLook e-commerce dataset. Always confirm exact columns with describe_table.

The orders table has one row per order. The order_items table has one row per item in an order and carries the item status and sale price.

Item and order status values include Processing, Shipped, Complete, Returned and Cancelled. A Returned status means the customer sent the item back under the returns policy.

The users table holds customer demographics and location. The products table holds category, brand, cost and retail price.

Revenue is defined as the sum of sale_price on order_items whose status is not Cancelled or Returned.
