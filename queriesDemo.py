# Returns all customers
customers = Customer.objects.all() 

# Returns first customer
firstCustomer = Customer.objects.first()

# Returns Last customer
lastCustomer = Customer.objects.last()

# Returns a specific customer
customer1 = Customer.objects.get(name = "Chig Chik")
# now we can - 
customer1.email

## Selecting information
orders = customer1.order_set.all()
print(orders)

order = Order.object.first()
print(order.customer.name)