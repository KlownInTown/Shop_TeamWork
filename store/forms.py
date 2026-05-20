# store/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# ОБЯЗАТЕЛЬНО импортируем модель товара, чтобы форма знала, с чем работать
from .models import Product 

# Твоя рабочая форма регистрации
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    is_seller = forms.BooleanField(required=False, label="Я хочу стать продавцом (партнером)")
    company_name = forms.CharField(max_length=150, required=False, label="Название организации")

    class Meta:
        model = User
        fields = ['username', 'email']


# --- ДОБАВЬ ЭТОТ КЛАСС НИЖЕ, ЕСЛИ ЕГО ТАМ НЕТ ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Эти поля продавец будет заполнять на странице
        fields = ['title', 'description', 'price', 'image', 'category']
        
        # Красивые стили для полей формы
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ccc;'}),
            'description': forms.Textarea(attrs={'style': 'width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ccc;', 'rows': 3}),
            'price': forms.NumberInput(attrs={'style': 'width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ccc;'}),
            'category': forms.Select(attrs={'style': 'width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ccc;'}),
        }