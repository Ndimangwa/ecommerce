from django.shortcuts import render, redirect
from cart.cart import Cart
#Local Imports
from .models import ShippingAddress, Order, OrderItem
from store.models import Profile
from .forms import ShippingForm, PaymentForm
from django.contrib import messages
import datetime
from authorization.authorize import Authorization
#PayPal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm 
from django.conf import settings
import uuid # for generating unique order id
#Include Management
from .order_management import OrderManagement

#shipping status
@Authorization.authorize_server(name='update_shipping_status')
def update_shipping_status(request):
    if request.user.is_authenticated and request.user.is_superuser and request.method == 'POST':
        status = request.POST['shipping_status']
        num = int(request.POST['num']) #primary-key
        now = datetime.datetime.now()
        #For update to work, we need to use filter instead of get
        #update is used to update multiple instances
        order = Order.objects.get(id=num)
        if status == "true":
            order.shipped = True
            order.date_shipped = now
        else:
            order.shipped = False
        #Now do saving
        order.save()
        messages.success(request, ('Shipping Status Updated'))
        return redirect('store:home')
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')  

#orders
@Authorization.authorize_server(name='orders')
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #Get Order
        order = Order.objects.get(id=pk)
        #Get Corresponding items
        items = OrderItem.objects.filter(order=order)
        context = {
            'order': order,
            'items': items
        }
        return render(request, 'payment/orders.html', context)
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home') 

#Shipped Dashboard
@Authorization.authorize_server(name='shipped_dash')
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        return render(request, 'payment/shipped_dash.html', {'orders' : orders}) 
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')

#Un-Shipped Dashboard
@Authorization.authorize_server(name='not_shipped_dash')
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        return render(request, 'payment/not_shipped_dash.html', {'orders' : orders}) 
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')

# Create your views here.
@Authorization.authorize_server(name='payment_success')
def payment_success(request):
    #We need to clear session and clear old-cart
    OrderManagement.clear_both_cart_session_as_well_as_db(request)
    if request.GET:
        #Trying to pull paypal stuff
        pass
    return render(request, 'payment/payment_success.html', {})

@Authorization.authorize_server(name='payment_failed')
def payment_failed(request):
    return render(request, 'payment/payment_failed.html', {})

# Checkout
@Authorization.authorize_server(name='checkout')
def checkout(request):
    #get the cart
    cart = Cart(request)
    #get products
    cart_products = cart.get_prods()
    #get quantities
    quantities = cart.get_quants();
    #get totals
    totals = cart.get_total()
    #preparing data
    context = {
        'cart_products' : cart_products,
        'quantities' : quantities,
        'totals': totals,
    }
    #Now working for form
    if request.user.is_authenticated:
        #Get user_shipping_address
        user_shipping_address = ShippingAddress.objects.get(user__id=request.user.id)
        #Get user shipping form
        shipping_form = ShippingForm(request.POST or None, instance=user_shipping_address)
        #packing in context dictionary
        context['shipping_form'] = shipping_form
        return render(request, 'payment/checkout.html', context)
    #Now the general part where no user is authenticated, we call this a guest user
    shipping_form = ShippingForm(request.POST or None)
    #packing in context dictionary
    context['shipping_form'] = shipping_form
    return render(request, 'payment/checkout.html', context)

#Billing Info
@Authorization.authorize_server(name='billing_info')
def billing_info(request):
    if request.POST:
        #Data were submitted
        #A -- get the cart
        cart = Cart(request)
        #get products
        cart_products = cart.get_prods()
        #get quantities
        quantities = cart.get_quants();
        #get totals
        totals = cart.get_total()
        #preparing data
        context = {
            'cart_products' : cart_products,
            'quantities' : quantities,
            'totals': totals,
        }
        #Let us handle shipping_info as well as billing_form
        #same whether user is authenticated or not
        #B -- shipping_info
        shipping_info = request.POST
        # Saving shipping info in session, so we can
        # take them to payment page
        request.session['my_shipping'] = shipping_info
        context['shipping_info'] = shipping_info
        #C -- billing_form , we need form forms.Form
        billing_form = PaymentForm()
        context['billing_form'] = billing_form
        #D -- Apart from normal Payment form with credit cards
        #       we also need PayPalPaymentsForm actual this is a button
        host = request.get_host() #we need host so reverse can work
        #create invoice number
        my_invoice = str(uuid.uuid4());
        #paypal dictionary
        paypal_dict = {
            'business' : settings.PAYPAL_RECEIVER_EMAIL,
            'amount' : totals,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': my_invoice,
            'currency_code': 'USD', #You can do EUR etc, TZ/TZS I do not know
            'notify_url' : 'https://{}{}'.format(host, reverse('payment:paypal-ipn')),
            'return_url' : 'https://{}{}'.format(host, reverse('payment:payment_success')),
            'cancel_return' : 'https://{}{}'.format(host, reverse('payment:payment_failed')),
        }
        #Now pack paypal_form
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        context['paypal_form'] = paypal_form
        #We need to actual create invoice with the same invoice-number
        #as PayPal , invoice is just an order marked as UNPAID
        OrderManagement.initialize_order(request, my_invoice)
        #We have our Order this is great
        return render(request, 'payment/billing_info.html', context)
    else:
       messages.success(request, ('Access Denied'))
       return redirect('store:home') 


@Authorization.authorize_server(name='process_payment')
def process_payment(request):
    if request.POST:
        #Initialize order
        OrderManagement.initialize_order(request)
        #Clearing Cart
        OrderManagement.clear_both_cart_session_as_well_as_db(request)
        #feedback
        messages.success(request, ('Order Placed Successful'))
        return redirect('store:home')
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')