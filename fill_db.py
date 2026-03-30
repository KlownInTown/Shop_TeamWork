import os
import django
import random

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_shop.settings')
django.setup()

from store.models import Product, Category

def seed_db():
    # Создаем категории
    categories = ['Худи', 'Футболки', 'Кепки', 'Рюкзаки']
    cat_objects = []
    for name in categories:
        cat, created = Category.objects.get_or_create(name=name, slug=name.lower())
        cat_objects.append(cat)

    # Создаем 20 случайных товаров
    for i in range(20):
        title = f"Товар №{i}"
        price = random.randint(1000, 5000)
        desc = "Описание крутого товара, который подчеркнет твой стиль."
        cat = random.choice(cat_objects)
        
        Product.objects.create(
            title=title,
            price=price,
            description=desc,
            category=cat,
            # image = ... (здесь можно указать путь к дефолтной картинке)
        )
    print("Готово! 20 товаров добавлено.")

if __name__ == '__main__':
    seed_db()