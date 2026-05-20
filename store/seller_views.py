# store/seller_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm

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