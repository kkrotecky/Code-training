import math



customer_basket_cost = 34
customer_basket_weight = 44

if customer_basket_cost >= 100:
    print("Your shipping is: $" + 0)
else:
    print("Your shipping is: $" + str(customer_basket_weight * 1.2))