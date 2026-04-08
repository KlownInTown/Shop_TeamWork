from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Как в видео
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False) # False = это корзина, True = оформленный заказ
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        # Считаем сумму только тех товаров, которые реально существуют в базе
        total = sum([item.get_total for item in orderitems if item.product])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        # Считаем количество только существующих товаров
        total = sum([item.quantity for item in orderitems if item.product])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        if self.product: # Проверяем, существует ли продукт
            total = self.product.price * self.quantity
        else:
            total = 0
        return total


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Заглушка для фото. Не забудь положить default.jpg в папку media/
    avatar = models.ImageField(default='default.jpg', upload_to='profile_avatars')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'