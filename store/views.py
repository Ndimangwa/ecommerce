from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Product, Category
from .forms import SignUpForm
# Create your views here.
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products' : products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
            messages.success(request, ('Congratulations!!!!, You have registered successful, You have now logged-in into your account!!!!'))
            return redirect('store:home')
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
        category = Category.objects.get(name=foo)
        products = Product.objects.get(category=category)
        context = {
            'products': products,
            'category': category,
        }
        return render(request, 'category.html', context)
    except:
        messages.success(request, ('Category does not exists'))
        return redirect('store:home')