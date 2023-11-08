from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    # User can have 1 customer and vice versa
    user = models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default = "cutecat.jpeg",null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY = (
        ('North Indian','North Indian'),
        ('South Indian','South Indian'),
        ('Chinese','Chinese'),
        ('Snacks','Snacks'),
        ('Beverage','Beverage'),
    )
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    category = models.CharField(max_length=200, null=True,choices=CATEGORY)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add = True)
    tags = models.ManyToManyField(Tag)
    inventory = models.PositiveIntegerField(default=50)
    image = models.ImageField(default = "cutecat.jpeg",null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except: 
            url = ''
        return url

class Order(models.Model):
    STATUS = (
        ('Delivered','Delivered'),
        ('Pending','Pending'),
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    #product = models.ForeignKey(Product,null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    complete = models.BooleanField(default=False,null=True,blank=False)
    trasaction_id = models.CharField(max_length=200,null=True)
    def __str__(self):
        return str( self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product,null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order,null=True, on_delete=models.SET_NULL) 
    quantity = models.PositiveIntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add = True) 

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

