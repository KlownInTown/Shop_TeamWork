# store/seller_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def add_product(request):
    # Защита: проверяем, точно ли этот пользователь — продавец
    if not request.user.profile.is_seller:
        messages.error(request, "Только продавцы могут добавлять товары!")
        return redirect('profile')

    if request.method == 'POST':
        # request.FILES обязательно нужен для загрузки картинок!
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False) # Создаем объект, но пока не пишем в БД
            product.seller = request.user     # Назначаем текущего пользователя продавцом
            product.save()                    # Теперь сохраняем в базу
            
            messages.success(request, f"Товар «{product.title}» успешно добавлен!")
            return redirect('profile')
    else:
        form = ProductForm()
    
    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    # Ищем товар по ID (pk - primary key)
    product = get_object_or_404(Product, pk=pk)
    
    # Важнейшая защита: проверяем, что этот товар принадлежит текущему продавцу
    if product.seller != request.user:
        messages.error(request, "Вы не можете редактировать чужой товар!")
        return redirect('profile')

    if request.method == 'POST':
        # Передаем в форму данные из POST, файлы и указываем instance=product (что именно обновляем)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно обновлен!")
            return redirect('profile')
    else:
        # Если это GET-запрос, заполняем форму текущими данными товара
        form = ProductForm(instance=product)
        
    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Снова защита от удаления чужих товаров
    if product.seller != request.user:
        messages.error(request, "Вы не можете удалить чужой товар!")
        return redirect('profile')

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Товар успешно удален.")
        return redirect('profile')
        
    return render(request, 'delete_product.html', {'product': product})