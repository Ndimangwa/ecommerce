from django.shortcuts import render, redirect
from cart.cart import Cart
#Local Imports
from .models import ShippingAddress, Order, OrderItem
from store.models import Profile
from .forms import ShippingForm, PaymentForm
from django.contrib import messages
import datetime

#shipping status
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
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        return render(request, 'payment/shipped_dash.html', {'orders' : orders}) 
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')

#Un-Shipped Dashboard
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        return render(request, 'payment/not_shipped_dash.html', {'orders' : orders}) 
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')

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
        # Saving shipping info in session, so we can
        # take them to payment page
        request.session['my_shipping'] = shipping_info
        context['shipping_info'] = shipping_info
        #C -- billing_form , we need form forms.Form
        billing_form = PaymentForm()
        context['billing_form'] = billing_form
        return render(request, 'payment/billing_info.html', context)
    else:
       messages.success(request, ('Access Denied'))
       return redirect('store:home') 


#Processing payment
def mark_empty(val):
    return val if val else "__MIMI_SIPATIKANI__iiii__"

def clean_string(val):
    return val.replace("__MIMI_SIPATIKANI__iiii__\n", "")

def process_payment(request):
    if request.POST:
        #A -- get the cart ; Aim is just to get totals
        cart = Cart(request)
        #get products
        cart_products = cart.get_prods()
        #get quantities
        quantities = cart.get_quants();
        #get totals
        totals = cart.get_total()

        #B -- Get Payment form
        payment_form = PaymentForm(request.POST or None)
        
        #C -- Get shipping session data
        my_shipping = request.session.get('my_shipping')
        #We need to create order both for guest and for users who are logged in
        shipping_address = f"{mark_empty(my_shipping['shipping_address1'])}\n{mark_empty(my_shipping['shipping_address2'])}\n{mark_empty(my_shipping['shipping_city'])}\n{mark_empty(my_shipping['shipping_state'])}\n{mark_empty(my_shipping['shipping_zipcode'])}\n{mark_empty(my_shipping['shipping_country'])}\n"
        shipping_address = clean_string(shipping_address)
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        amount_paid = totals
        #Now saving to database -- let us work smart from dictionary
        client_order_data = {
            'full_name': full_name,
            'email': email,
            'shipping_address': shipping_address,
            'amount_paid': amount_paid
        }
        #Same wise prepare a client_order_item_data
        client_order_item_data = {}
        #Now we need to check if we have user, user is authenticated
        if request.user.is_authenticated:
            client_order_data['user'] = request.user
            client_order_item_data['user'] = request.user
        #Now do actual saving
        client_order = Order(**client_order_data)
        client_order.save()
        #save a reference to client_order_item_data 
        client_order_item_data['order'] = client_order
        #Now working looping through products
        for product in cart_products:
            #make a copy of client_order_item_data
            item_data = client_order_item_data.copy()
            item_data['product'] = product
            #get price
            price = 0
            if product.is_sale:
                price = product.sale_price 
            else:
                price = product.price
            item_data['price'] = price
            #get quantity
            for key,quantity in quantities.items():
                if int(key) == product.id: #Make sure it is int
                    item_data['quantity'] = quantity
                    client_order_item = OrderItem(**item_data)
                    client_order_item.save()
                    break
        #After order is created delete cart
        for key in list(request.session.keys()):
            if key == "session_key":
                #delete the key
                del request.session[key]
        #We forgot items were saved permanetly in db
        #in Profile.old_card
        if request.user.is_authenticated:
            current_user_profile = Profile.objects.get(user=request.user)
            if current_user_profile:
                current_user_profile.old_cart = ""
                current_user_profile.save()
        #feedback
        messages.success(request, ('Order Placed Successful'))
        return redirect('store:home')
    else:
        messages.success(request, ('Access Denied'))
        return redirect('store:home')