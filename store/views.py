from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import (
    Profile, Product, Category, Order, OrderItem, ShippingAddress
)
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        for item in items:
            if not item.product:
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
    if not request.user.is_authenticated:
        return redirect('index')
    product = Product.objects.get(id=pk)
    order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def index(request, category_slug=None):
    products = Product.objects.all()
    query = request.GET.get('search')
    if query:
        products = products.filter(title__icontains=query)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    context = {'products': products, 'query': query}
    return render(request, 'index.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item_quantity = 0
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        item = OrderItem.objects.filter(order=order, product=product).first()
        if item:
            cart_item_quantity = item.quantity
    context = {
        'product': product,
        'cart_item_quantity': cart_item_quantity,
    }
    return render(request, 'product_detail.html', context)


def search_results(request):
    query = request.GET.get('search')
    if query:
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
            # 1. Сохраняем пользователя (commit=True по умолчанию)
            user = form.save()

            # 2. Достаём значения новых полей из формы
            is_seller_flag = form.cleaned_data.get('is_seller')
            company = form.cleaned_data.get('company_name')

            # 3. Создаём профиль с нужными полями
            Profile.objects.create(
                user=user,
                is_seller=is_seller_flag,
                company_name=company
            )

            messages.success(request, 'Аккаунт создан! Теперь вы можете войти.')
            return redirect('login')
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


@login_required
def profile(request):
    # Получаем или создаем профиль, если его вдруг нет
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.FILES.get('profile_pic'):
        user_profile.image = request.FILES['profile_pic']
        user_profile.save()
        return redirect('profile')

    context = {}
    # Обращаемся к уже полученному объекту user_profile
    if user_profile.is_seller:
        my_products = Product.objects.filter(seller=request.user)
        context['my_products'] = my_products
        context['is_seller'] = True
        context['company_name'] = user_profile.company_name
    else:
        orders = Order.objects.filter(customer=request.user, complete=True).order_by('-date_ordered')
        context['orders'] = orders
        context['is_seller'] = False

    return render(request, 'users/profile.html', context) # Добавил 'users/' если нужно

@login_required
def checkout(request):
    order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    items = order.orderitem_set.all()
    total = sum([item.product.price * item.quantity for item in items if item.product])

    if request.method == 'POST':
        ShippingAddress.objects.create(
            customer=request.user,
            order=order,
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            zipcode=request.POST.get('zipcode')
        )

        line_items = []
        for item in items:
            if item.product:
                line_items.append({
                    'price_data': {
                        'currency': 'rub',
                        'unit_amount': int(item.product.price * 100),
                        'product_data': {
                            'name': item.product.title,
                        },
                    },
                    'quantity': item.quantity,
                })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('cart')),
        )
        return redirect(checkout_session.url, code=303)

    context = {'items': items, 'order': order, 'total': total}
    return render(request, 'checkout.html', context)


@login_required
def payment_success(request):
    order = Order.objects.get(customer=request.user, complete=False)
    order.complete = True
    order.save()
    return render(request, 'success.html')