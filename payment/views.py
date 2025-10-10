from django.shortcuts import render, redirect
from cart.cart import Cart
#Local Imports
from .models import ShippingAddress
from .forms import ShippingForm, PaymentForm
from django.contrib import messages

# Create your views here.
def payment_success(request):
    return render(request, 'payment/payment_success.html', {})

# Checkout
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
        context['shipping_info'] = shipping_info
        #C -- billing_form , we need form forms.Form
        billing_form = PaymentForm()
        context['billing_form'] = billing_form
        return render(request, 'payment/billing_info.html', context)
    else:
       messages.success(request, ('Access Denied'))
       return redirect('store:home') 
    