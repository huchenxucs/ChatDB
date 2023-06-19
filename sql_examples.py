import re

eg_purchase = """
USER INPUT: On 2023-01-22, the shop purchased 100kg banana from supplier 'ABC' (contact number: 67543, email: abc_sup@gmail.com) at 1.2 dollar/kg and planed sell at 1.8 dollar/kg. Banana's fruit type is berry and shelf life is 15 days.
ANSWER:
```
Step1: Insert supplier 'ABC' if not exists
`INSERT INTO suppliers (supplier_name, contact_number, email)
SELECT 'ABC', '67543', 'abc_sup@gmail.com'
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_name = 'ABC');`

Step2: Insert fruit (set the selling price to NULL and stock quantity to 0) if not exists
`INSERT INTO fruits (fruit_name, selling_price, stock_quantity, fruit_type, shelf_life)
SELECT 'banana', NULL, 0, 'berry', 15
WHERE NOT EXISTS (SELECT 1 FROM fruits WHERE fruit_name = 'banana');`

Step3: Insert purchase 
`INSERT INTO purchases (supplier_id, purchase_date, total_cost)
VALUES ((SELECT supplier_id FROM suppliers WHERE supplier_name = 'ABC'), '2023-01-22', 100 * 1.2);`

Step4: Insert purchase item
`INSERT INTO purchase_items (purchase_id, fruit_id, quantity_purchased, cost_per_item, item_total_cost)
VALUES ((SELECT MAX(purchase_id) FROM purchases), (SELECT fruit_id FROM fruits WHERE fruit_name = 'banana'), 100, 1.2, 100 * 1.2);`

Step5: Update the stock quantity of banana
`UPDATE fruits 
SET stock_quantity = stock_quantity + 100
WHERE fruit_name = 'banana';`

Step6: Update the selling price of banana if given new selling price
`UPDATE fruits 
SET selling_price = 1.8
WHERE fruit_name = 'banana';`
```
"""

eg_ask_sale = """
USER INPUT: Who bought 100kg apple on 2010-03-27 and what is he/she name, detailed information and costumer id?
ANSWER:
```
Step1: Retrieve the customer information who made the purchase
`SELECT c.customer_id, c.first_name, c.last_name, c.phone_number, c.email
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN fruits f ON si.fruit_id = f.fruit_id
WHERE f.fruit_name = 'apple' AND si.quantity_sold = 100 AND s.sale_date = '2010-03-27';`
```
"""

eg_if_new_customer_sale = """
USER INPUT: A customer named 'Chenzhuang Du' with a phone number as 120056 and e-mail as chenzhuang@gmail.com bought 10kg apple and 5kg pear on 2010-03-27.
ANSWER:
```
Step1: Insert customer 'Chenzhuang Du' if not exists
`INSERT INTO customers (first_name, last_name, phone_number, email)
SELECT 'Chenzhuang', 'Du', '120056', 'chenzhuang@gmail.com'
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE phone_number = '120056');`

Step2: Insert sale
`INSERT INTO sales (customer_id, sale_date, total_price)
VALUES ((SELECT customer_id FROM customers WHERE phone_number = '120056'), '2010-03-27', (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10 + (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);`

Step3: Insert sale item
`INSERT INTO sale_items (sale_id, fruit_id, quantity_sold, price_per_item, item_total_price)
VALUES ((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'apple'), 10, (SELECT selling_price FROM fruits WHERE fruit_name = 'apple'), (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10),
((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'pear'), 5, (SELECT selling_price FROM fruits WHERE fruit_name = 'pear'), (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);`

Step4: Update the stock quantity of apple and pear
`UPDATE fruits 
SET stock_quantity = CASE 
    WHEN fruit_name = 'apple' THEN stock_quantity - 10
    WHEN fruit_name = 'pear' THEN stock_quantity - 5
    ELSE stock_quantity
END
WHERE fruit_name IN ('apple', 'pear');`
```
"""

eg_delete_pro = """
USER INPUT: Because the customer returned the goods, roll back a sales record which is made by the customer with customer id as 8 on 2023-01-29.
ANSWER:
```
Step1: Find the sale_id for this customer on this date
`SELECT sale_id FROM sales WHERE customer_id = 8 AND sale_date = '2023-01-29';`

Step2: Get all the fruit_id and quantity_sold for this sale, replace <sale_id> with the results from the previous queries
`SELECT fruit_id, quantity_sold FROM sale_items WHERE sale_id = <sale_id>;`

Step3: Increase the stock_quantity for each fruit sold in this sale, replace <quantity_sold> <fruit_id> with the results from the previous queries
`UPDATE fruits
SET stock_quantity = stock_quantity + <quantity_sold>
WHERE fruit_id = <fruit_id>;`

Step4: Delete the sale items for this sale, replace <sale_id> with the results from the previous queries
`DELETE FROM sale_items WHERE sale_id = <sale_id>;`

Step5: Delete the sale record, replace <sale_id> with the results from the previous queries
`DELETE FROM sales WHERE sale_id = <sale_id>;`
```
"""


egs = [eg_ask_sale, eg_purchase, eg_if_new_customer_sale, eg_delete_pro]
