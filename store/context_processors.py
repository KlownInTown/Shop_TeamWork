from .models import Category, Order

def cart_status(request):
    categories = Category.objects.all() # Получаем все категории
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        cart_total = order.get_cart_items
    else:
        cart_total = 0
    return {
        'cart_total': cart_total,
        'all_categories': categories # Теперь категории доступны везде
    }