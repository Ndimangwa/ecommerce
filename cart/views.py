from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from store.models import Product
from .cart import Cart
from authorization.authorize import Authorization

# Create your views here.
@Authorization.authorize_server(name='cart_summary')
def cart_summary(request):
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
    return render(request, 'cart/cart_summary.html', context)

@Authorization.authorize_server(name='cart_add')
def cart_add(request):
    #get the cart
    cart = Cart(request)
    #testing
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        #Quantity
        product_qty = int(request.POST.get('product_qty'))
        #fetch product
        product = get_object_or_404(Product, id=product_id)
        #save to session
        cart.add(product=product, quantity=product_qty)
        #Now Calculate cart length 
        cart_quantity = len(cart)
        #messages.success(request, ('[ cart > add ] : You have successful added ' + product.name + ' with quantity ' + product_qty))
        messages.success(request, ('Successful Added the product'))
        #build response
        response = JsonResponse({ 'qty' : cart_quantity })
        return response
    else:
        messages.success(request, ('There were problem in adding a product'))
        return JsonResponse({'error' : '707', 'errormessage' : 'Could not get a valid action'})

@Authorization.authorize_server(name='cart_delete')
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        cart = Cart(request)
        product_id = int(request.POST.get('product_id'))
        #Delete cart
        cart.delete(product=product_id)
        #messages
        messages.success(request, ('An item was deleted, successful'))
        #build response
        response = JsonResponse({ 'product' : product_id })
        return response
    else:
        #messages
        messages.success(request, ('Failed to remove an item'))
        #response
        return JsonResponse({'error' : '808', 'errormessage' : 'Could not get a valid action'})

@Authorization.authorize_server(name='cart_update')
def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #update cart
        cart.update(product=product_id, quantity=product_qty)
        #messages
        messages.success(request, ('An item was updated, successful'))
        #build response
        response = JsonResponse({ 'qty' : product_qty })
        return response
    else:
        #messages
        messages.success(request, ('Failed to update an item'))
        #response
        return JsonResponse({'error' : '707', 'errormessage' : 'Could not get a valid action'})