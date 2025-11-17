from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings 

@receiver(valid_ipn_received)
def paypal_payment_received(sender, ipn, **kwargs):
    #grab the paypal object
    paypal_obj = ipn
    #printing
    print(paypal_obj)