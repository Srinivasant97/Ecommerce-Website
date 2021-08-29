from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
# Create your models here.

CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sport Wear'),
    ('OW','Out Wear')
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
) 


class Item(models.Model):
    title = models.CharField(max_length=100)
    price= models.IntegerField()
    discount_price= models.IntegerField(blank=True,null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label=models.CharField(choices=LABEL_CHOICES,max_length=1)
    slug=models.SlugField()  
    description=models.TextField()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:product",kwargs={
            'slug' : self.slug
        })
    def get_add_to_cart(self):
        return reverse("products:add_to_cart",kwargs={
            'slug' : self.slug
        })
    def get_remove_from_cart(self):
        return reverse("products:remove_from_cart",kwargs={
            'slug' : self.slug
        })


class OrderItem(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True, blank=True)
    ordered=models.BooleanField(default=False)
    item = models.ForeignKey(Item,on_delete = models.CASCADE)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return self.item.title

    def get_total_item_price(self):
        return self.quantity * self.item.price

    
    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price()

    def Amount(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()

class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True, blank=True)
    items=models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField()
    ordered=models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,null=True, blank=True)
    payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,null=True, blank=True)

    def __str__(self):
        return self.user.username

    def total(self):
        T=0
        for i in self.items.all():
            T+=i.Amount()
        return T

class BillingAddress(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True, blank=True)
    street_name=models.CharField(max_length=100)
    apartment_no=models.CharField(max_length=100)
    country=CountryField(multiple=False)
    zip=models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True, blank=True)
    amount=models.IntegerField()
    timestamp =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



