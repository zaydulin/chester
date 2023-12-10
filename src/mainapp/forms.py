from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ClearableFileInput
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField(label="Ник на сайте", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())

class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'account__file'}))

    class Meta:
        model = User
        fields = ['avatar', 'birthday',  'gender',  'email', 'time_zone']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')  # Добавьте поле для Email
    username = forms.CharField(required=True, label='Имя')  # Добавьте поле для Email
    birthday = forms.DateField(required=False, label='Дата рождения', widget=forms.DateInput(attrs={'id': 'datepicker'}))
    captcha = CaptchaField()
    class Meta:
        model = User  # Укажите модель пользователя, обычно 'User'
        fields = ('username','captcha', 'email', 'password1', 'password2', 'gender', 'birthday')  # Поля, которые будут отображаться в форме

