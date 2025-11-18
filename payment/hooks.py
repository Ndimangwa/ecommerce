from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings 
import datetime
import time
from .models import Order

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    #Atmost delay 10s , 
    time.sleep(10)
    #grab the paypal object
    paypal_obj = sender
    #grabing invoice
    my_invoice = str(paypal_obj.invoice)
    #We need to pull this Order and mark as paid
    my_order = Order.objects.get(invoice=my_invoice)
    #Mark Paid and put timestamp
    now = datetime.datetime.now()
    my_order.paid=True
    my_order.date_paid = now
    my_order.save()
    #We need to clear the cart at this point , delete all sessions and clear Profile.old_cart