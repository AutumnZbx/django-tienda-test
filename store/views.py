from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from .forms import ProductForm
from django.shortcuts import get_object_or_404,redirect
from django.shortcuts import render,redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, completed=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    if not created:
        order_item.quantity += 1
        order_item.save()
    if request.is_ajax():
        count = order.items.count()
        return JsonResponse({'count': count})
    return redirect('home')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order = Order.objects.get(user=request.user, completed=False)
    order.products.remove(product)
    return redirect('cart')

@login_required
def cart_view(request):
    order = Order.objects.filter(user=request.user, completed=False).first()
    return render(request, 'cart.html', {'order': order})


@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, completed=False).first()
    if order:
        order.completed = True
        order.save()
    return render(request, 'checkout.html')

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # manejar archivos
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})