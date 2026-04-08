from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Profile

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        # Проверка: если вдруг товар (Product) был удален из БД, 
        # но запись OrderItem осталась — чистим корзину
        items = order.orderitem_set.all()
        for item in items:
            if not item.product: # Если связь с продуктом потеряна
                item.delete()
                messages.warning(request, "Один из товаров больше не доступен и удален из базы.")
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'cart.html', context)

def add_to_cart(request, pk):
    product = Product.objects.get(id=pk)
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity += 1
        order_item.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def update_cart_item(request, pk, action):
    # Если пользователь не залогинен, пока просто возвращаем его (или делай редирект на логин)
    if not request.user.is_authenticated:
        return redirect('index')

    product = Product.objects.get(id=pk)
    # Получаем или создаем корзину
    order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    # Получаем или создаем позицию в корзине
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    
    order_item.save()

    # Удаляем позицию, если количество стало 0 или меньше
    if order_item.quantity <= 0:
        order_item.delete()
        
    # Возвращаем пользователя туда, откуда он пришел
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def index(request, category_slug=None):
    products = Product.objects.all()
    
    query = request.GET.get('search')
    if query:
        # Фильтруем по названию (icontains — регистр не важен)
        products = products.filter(name__icontains=query)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {'products': products, 'query': query}
    return render(request, 'index.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item_quantity = 0 

    if request.user.is_authenticated:
        # Пытаемся найти активную корзину пользователя
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        # Ищем, есть ли этот конкретный товар в этой корзине
        item = OrderItem.objects.filter(order=order, product=product).first()
        if item:
            cart_item_quantity = item.quantity

    context = {
        'product': product,
        'cart_item_quantity': cart_item_quantity, # Передаем число в шаблон
    }
    return render(request, 'product_detail.html', context)

def search_results(request):
    query = request.GET.get('search')
    if query:
        # Заменяем name на title, так как это имя поля в твоей модели
        products = Product.objects.filter(
            title__icontains=query
        ) | Product.objects.filter(description__icontains=query)
    else:
        products = Product.objects.none()

    return render(request, 'search_results.html', {'products': products, 'query': query})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Автоматически создаем профиль под аватарку при регистрации
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required # Доступ только для авторизованных
def profile(request):
    return render(request, 'users/profile.html')