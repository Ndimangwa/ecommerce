from django.db import models
from authorization.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime
from store.models import Product

# Create your models here.
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    #Don't pluralize address
    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
    
#User -> ShippingAddress; When User is created on saved activate signal
def create_shipping_address(sender, instance, created, **kwargs):
    if created:
        #User is Created
        user_shipping = ShippingAddress.objects.create(user=instance)
        user_shipping.save()
        #print(f"++++++++ Shipping Address for User : {instance.username} has been created successfull ++++++++")
    else:
        #User updated
        #print(f"++++++++ A User {instance.username} has been updated [ ShippingAddress has been signalled ] ++++++++")
        pass

#Connecting now
post_save.connect(create_shipping_address, sender=User)

#Create Order
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=2047)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    #PayPal Invoice and Paid
    invoice = models.CharField(max_length=255, null=True, blank=True)
    paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Order -- {str(self.id)}'
    
#Now adding receiver decorator
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        #This must be an update
        #in update we have pk primary key in advance
        #in creation we do not
        now = datetime.datetime.now()
        saved_obj = sender.objects.get(pk=instance.pk)
        if instance.shipped and not saved_obj.shipped:
            instance.date_shipped = now

#Create Order Item
class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order Item -- {str(self.id)}'