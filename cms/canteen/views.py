from django.db.models import F
#from .filters import OrderFilter, NameFilter, OrderFilter_1
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from django.contrib import messages
from .forms import OrderForm,CreateUserForm,CustomerForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from django.http import JsonResponse
import json
import datetime



def registerPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                messages.success(request,'Account was created for '+ username)
                return redirect('login')
        
        context = {'form':form}
        return render(request,'canteen/register.html',context)
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, 'Username or password is incorrect')
    
    context = {}
    return render(request, 'canteen/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status = "Delivered").count()
    pending = orders.filter(status = "Pending").count()

    context = {'orders':orders,'customers':customers,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request,'canteen/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status = "Delivered").count()
    pending = orders.filter(status = "Pending").count()
    print('ORDERS:',orders)
    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request,'canteen/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()
    context={'form':form}
    return render(request,'canteen/account_settings.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request,'canteen/products.html',{'products':products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk):
    customer = Customer.objects.get(id=pk)
    #querying all the child objects
    orders = customer.order_set.all()
    order_count = orders.count()
    context = {'customer':customer,'orders':orders,'order_count':order_count}
    return render(request,'canteen/customer.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def adjustInventory(request, pk):
    product = Product.objects.get(id=pk)

    if request.method == 'POST':
        new_inventory = request.POST['new_inventory']
        try:
            new_inventory = int(new_inventory)
        except ValueError:
            messages.error(
                request, 'Invalid inventory value. Please enter a valid number.')
            return redirect('adjust_inventory', pk=pk)

        if new_inventory < 0:
            messages.error(request, 'Inventory cannot be negative.')
        else:
            product.inventory = new_inventory
            product.save()
            messages.success(request, 'Inventory updated successfully.')
            return redirect('products')

    return render(request, 'canteen/adjust_inventory.html', {'product': product})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    customer = Customer.objects.get(id=pk)
    form = OrderForm()
    if request.method == 'POST':
        print('Printing post request:',request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=pk)
            order_item = OrderItem.objects.get(id=pk)
            if product.inventory > 0:
                order = form.save()
                product.inventory-=1
                messages.success(request, 'Order was created successfully')
                return redirect('/')
            else:
                messages.error(request, 'Product is out of stock')
                return redirect('create_order', pk=pk)          
    #OrderFormSet = inlineformset_factory(Customer,Order, fields=('product','status'),extra=10)
    #customer = Customer.objects.get(id=pk)
    #formset = OrderFormSet(queryset = Order.objects.none(), instance = customer)
    #form = OrderForm(initial={'customer':customer})
    #if request.method == 'POST':
        #print('Printing post: ',request.POST)
        #form = OrderForm(request.POST)
        #formset = OrderFormSet(request.POST,instance = customer)
        #if formset.is_valid():
            #formset.save()
            #
    
    context = {'form':form, 'customer': customer}
    return render(request,'canteen/order_form.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect("/")
    context = {'form':form}
    return render(request,'canteen/order_form.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect("/")
    context = {'item':order}
    return render(request,'canteen/delete.html',context)


def store(request):   
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request,'canteen/store.html',context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'canteen/cart.html',context)


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'canteen/checkout.html',context)

    #@login_required(login_url='login')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete = False)
    orderItem,created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added',safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
    else:
        print("User Not logged in")
    
    if total == order.get_cart_total:
        order.status = 'Pending'
        order.complete = True
    order.save()
    return JsonResponse('Payment Complete',safe=False)

from django.db import connection
from django.shortcuts import render
def adminstats(request, category_name):
    with connection.cursor() as cursor:
        cursor.callproc('GetProductsByCategory', [category_name])
        results = cursor.fetchall()

    categories = Product.objects.values_list('category', flat=True).distinct()
    print("Categories:", categories)  # Add this line for debugging

    context = {
        'products': results,
        'category_name': category_name,
        'categories': categories,
    }

    return render(request, 'canteen/stats.html', context)

from django.db import connection
from django.shortcuts import render

""" def product_sales_per_day(request, order_date):
    with connection.cursor() as cursor:
        cursor.callproc('GetProductSalesPerDay', [order_date])
        results = cursor.fetchall()

    context = {
        'sales_data': results,
        'order_date': order_date,
    }

    return render(request, 'canteen/sales.html', context)


def product_qty_sales(request,order_date):
    cursor = connection.cursor()
    query = "select GetTotalQuantityOrderedPerProduct(%s)"
    cursor.execute(query, [order_date])
    res = cursor.fetchone()
    print(res)
    print(connection.queries)
    return render(request,'canteen/trial.html' ,{'result': res})

 """

def statistics(request, order_date):
    # Cursor 1: Get product sales per day
    with connection.cursor() as cursor1:
        cursor1.callproc('GetProductSalesPerDay', [order_date])
        sales_results = cursor1.fetchall()

    # Cursor 2: Get total quantity ordered per product
    with connection.cursor() as cursor2:
        query = "SELECT GetTotalQuantityOrderedPerProduct(%s)"
        cursor2.execute(query, [order_date])
        qty_result = cursor2.fetchone()
    
    context = {
        'sales_data': sales_results,
        'qty_data': qty_result,
        'order_date': order_date,
    }

    return render(request, 'canteen/sales.html', context)


def overall_sales(request):
    with connection.cursor() as cursor3:
        query_category_sales = """
        SELECT p.category, SUM(oi.quantity * p.price) AS total_sales
        FROM canteen_product p
        LEFT JOIN canteen_orderitem oi ON p.id = oi.product_id
        GROUP BY p.category;
        """
        cursor3.execute(query_category_sales)
        category_sales_result = cursor3.fetchall()

    with connection.cursor() as cursor4:
        query = """
        SELECT o.id, c.name, o.status
        FROM canteen_order o
        INNER JOIN canteen_customer c ON o.customer_id = c.id;
        """
        cursor4.execute(query)
        order_data = cursor4.fetchall()

    with connection.cursor() as cursor5:
        query = """
        select (select name from canteen_customer where id = o.customer_id) as customer_name,o.id as order_id,
        (select SUM(oi.quantity * p.price) from canteen_orderitem oi 
        join canteen_product p ON oi.product_id = p.id where oi.order_id = o.id) as cost
        from canteen_order o
        order by cost desc;
        """
        cursor5.execute(query)
        customer_data = cursor5.fetchall()


    context = {'order_data': order_data,'category_sales_data': category_sales_result,'customer_data': customer_data,}

    return render(request, 'canteen/overall_sales.html', context)

def trial(request):
    with connection.cursor() as cursor5:
        query = """
        select (select name from canteen_customer where id = o.customer_id) as customer_name,o.id as order_id,
        (select SUM(oi.quantity * p.price) from canteen_orderitem oi 
        join canteen_product p ON oi.product_id = p.id where oi.order_id = o.id) as cost
        from canteen_order o
        order by cost desc;
        """
        cursor5.execute(query)
        order_data = cursor5.fetchall()
    
    context = {'customer_data': order_data,}

    return render(request, 'canteen/trial.html', context)


