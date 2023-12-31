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
def createOrder(request,pk):
    OrderFormSet = inlineformset_factory(Customer,Order, fields=('product','status'),extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset = Order.objects.none(), instance = customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        #print('Printing post: ',request.POST)
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST,instance = customer)
        if formset.is_valid():
            formset.save()
            return redirect("/")
    
    context = {'formset':formset}
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

def canteen1(request):
    return render(request,'canteen/canteen1.html')
def canteen2(request):
    return HttpResponse('Hello Canteen 2')

    #@login_required(login_url='login')