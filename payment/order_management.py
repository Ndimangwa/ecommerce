from cart.cart import Cart
from .forms import PaymentForm
from .models import Order, OrderItem
from store.models import Profile

#Processing payment
def mark_empty(val):
    return val if val else "__MIMI_SIPATIKANI__iiii__"

def clean_string(val):
    return val.replace("__MIMI_SIPATIKANI__iiii__\n", "")

class OrderManagement:
    def initialize_order(request, invoice=None):
        """
        Note: This function does not clear cart
                cart session is not cleared neither database Profile.old_cart is not cleared
                It just initialize UNPAID ORDER (Invoice)
        """
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
        #If we have an invoice
        if invoice != None:
            client_order_data['invoice'] = invoice
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

    def clear_cart_session(request):
        for key in list(request.session.keys()):
            if key == "session_key":
                #delete the key
                del request.session[key]

    def clear_cart_in_db(request):
        if request.user.is_authenticated:
            current_user_profile = Profile.objects.get(user=request.user)
            if current_user_profile:
                current_user_profile.old_cart = ""
                current_user_profile.save()

    def clear_both_cart_session_as_well_as_db(request):
        #After order is created delete cart
        OrderManagement.clear_cart_session(request)
        #We forgot items were saved permanetly in db
        #in Profile.old_card
        OrderManagement.clear_cart_in_db(request)