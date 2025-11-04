from .models import ContextPosition

class CommonData:
    def run_add():
        ContextPosition.objects.create(cName='about', cPosition=1, caption='About').save()
        ContextPosition.objects.create(cName='update_user', cPosition=2, caption='Update User').save()
        ContextPosition.objects.create(cName='update_info', cPosition=3, caption='Update Info').save()
        ContextPosition.objects.create(cName='update_password', cPosition=4, caption='Change Password').save()
        ContextPosition.objects.create(cName='product', cPosition=5, caption='Product').save()
        ContextPosition.objects.create(cName='category', cPosition=6, caption='Category').save()
        ContextPosition.objects.create(cName='category_summary', cPosition=7, caption='Category Summary').save()
        ContextPosition.objects.create(cName='search', cPosition=8, caption='Search').save()
        ContextPosition.objects.create(cName='payment_success', cPosition=9, caption='Payment Success').save()
        ContextPosition.objects.create(cName='checkout', cPosition=10, caption='Checkout').save()
        ContextPosition.objects.create(cName='billing_info', cPosition=11, caption='Billing Info').save()
        ContextPosition.objects.create(cName='process_payment', cPosition=12, caption='Process Payment').save()
        ContextPosition.objects.create(cName='shipped_dash', cPosition=13, caption='Shipped Dashboard').save()
        ContextPosition.objects.create(cName='not_shipped_dash', cPosition=14, caption='Yet to be Shipped Dashboard').save()
        ContextPosition.objects.create(cName='orders', cPosition=15, caption='Orders').save()
        ContextPosition.objects.create(cName='update_shipping_status', cPosition=16, caption='Update Shipping Status').save()
        ContextPosition.objects.create(cName='cart_summary', cPosition=17, caption='Cart Summary').save()
        ContextPosition.objects.create(cName='cart_add', cPosition=18, caption='Add to Cart').save()
        ContextPosition.objects.create(cName='cart_delete', cPosition=19, caption='Delete from Cart').save()
        ContextPosition.objects.create(cName='cart_update', cPosition=20, caption='Update the Cart').save()