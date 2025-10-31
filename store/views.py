from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from authorization.models import User
from django.contrib import messages
from .models import Product, Category, Profile
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart

#Shipping Address and Payment
from payment.models import ShippingAddress
from payment.forms import ShippingForm
# Create your views here.
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products' : products})

def search(request):
    #determine if form filled
    if request.method == "POST":
        searched = request.POST['searched']
        #Query products
        products = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        #Test for Null
        if not products:
            messages.success(request, ('Product ', searched, ' is not found'))
            return redirect('store:search')
        else:
            return render(request, 'search.html', {'products' : products})
    return render(request, 'search.html', {})

def about(request):
    return render(request, 'about.html', {})

def update_info(request):
    if request.user.is_authenticated:
        current_user_profile = Profile.objects.get(user__id=request.user.id)
        #Get user_shipping_address
        user_shipping_address = ShippingAddress.objects.get(user__id=request.user.id)
        #Get user billing form
        form = UserInfoForm(request.POST or None, instance=current_user_profile)
        #Get user shipping form
        shipping_form = ShippingForm(request.POST or None, instance=user_shipping_address)
        if form.is_valid() or shipping_form.is_valid():
            if form.is_valid():
                form.save()
            if shipping_form.is_valid():
                shipping_form.save()
            messages.success(request, ('Congratulations!!!!! You have updated your user info successfully!!!!!'))
            return redirect('store:home')
        return render(request, 'update_info.html', {'form':form, 'shipping_form': shipping_form })
    else:
        messages.success(request, ('you must be logged in to access the page'))
        return redirect('store:home')

def update_password(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        current_user = request.user
        #Did they fill the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            #is form filled properly?
            if form.is_valid():
                form.save()
                messages.success(request, 'You have successful updated the password, please log in again')
                return redirect('store:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('store:update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form' : form})
    else:
        messages.success(request, 'You must be logged in to access the requested page')
        return redirect('store:home')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, ('User has been updated'))
            return redirect('store:home')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, ('you must be logged in to access the page'))
        return redirect('store:home')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #Do some shopping staff
            current_user = Profile.objects.get(user__id=request.user.id)
            #Get their saved cart
            saved_cart = current_user.old_cart
            #Convert old string to python dictionary
            if saved_cart:
                #convert saved cart to dictionary using json
                converted_cart = json.loads(saved_cart)
                #Add the loaded cart to session
                cart = Cart(request)
                #Now you need to merge cart in session and the db cart
                #Assume you had items in session prior logging
                #While logging you need to merge with old cart
                cart.merge_carts(converted_cart)
            messages.success(request, ('You have logged in'))
            return redirect('store:home')
        else:
            messages.success(request, ('Error! Plz try again!!!!'))
            return redirect('store:login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out successful!!!!'))
    return redirect('store:home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request, user)
            messages.success(request, ('Wonderfully!!! Now you can proceed to update your info'))
            return redirect('store:update_info')
        else:
            messages.success(request, ('Whoops!!!, kindly try again filling the form'))
            return redirect('store:register')
    else:
        return render(request, 'register.html', {'form' : form })
    

def product(request, pk):
    product = Product.objects.get(id=pk)
    context = {
        'product': product,
    }
    return render(request, 'product.html', context)

def category(request, foo):
    #Replace the - with ' '
    foo = foo.replace('-', ' ')
    try:
        # get return one item only
        category = Category.objects.get(name=foo)
        # filter returns multiple items
        products = Product.objects.filter(category=category)
        context = {
            'products': products,
            'category': category,
        }
        return render(request, 'category.html', context)
    except:
        messages.success(request, ('Category does not exists'))
        return redirect('store:home')

def category_summary(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'category_summary.html', context)
