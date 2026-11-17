import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Booking, Car


class BookingCreateForm(forms.ModelForm):
    client_phone = forms.CharField(
        label='Телефон для подтверждения*',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (900) 000-00-00',
            'class': 'form-input',
            'data-validate': 'phone',
            'required': True,
        })
    )
    comment = forms.CharField(
        label='Комментарий к заказу (необязательно)',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Укажите пожелания по работам...',
            'class': 'form-input',
            'data-maxlength': '500',
        })
    )

    class Meta:
        model = Booking
        fields = ['car', 'box', 'services', 'booking_date', 'start_time']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-input'}),
            'box': forms.Select(attrs={'class': 'form-input'}),
            'services': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'required': True}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input', 'required': True}),
        }

    def clean_client_phone(self):
        phone = self.cleaned_data['client_phone'].strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10 or len(digits) > 15:
            raise ValidationError('Введите корректный номер телефона (от 10 до 15 цифр).')
        return phone

    def clean(self):
        cleaned = super().clean()
        box = cleaned.get('box')
        booking_date = cleaned.get('booking_date')
        start_time = cleaned.get('start_time')
        if box and booking_date and start_time:
            conflict = Booking.objects.filter(
                box=box,
                booking_date=booking_date,
                start_time=start_time,
                status__in=['new', 'confirmed', 'in_progress']
            ).exists()
            if conflict:
                raise ValidationError('Выбранное время в этом боксе уже занято. Выберите другой слот.')
        return cleaned


class LoginForm(forms.Form):
    login = forms.CharField(
        label='Email или телефон*',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000 00 00', 'required': True})
    )
    password = forms.CharField(
        label='Пароль*',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••', 'required': True})
    )


class CarAddForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['body_type', 'brand', 'model', 'license_plate', 'manufacture_year']
        widgets = {
            'body_type': forms.Select(attrs={'class': 'form-input'}),
            'brand': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: BMW', 'required': True}),
            'model': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: X5', 'required': True}),
            'license_plate': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'А777АА73', 'required': True}),
            'manufacture_year': forms.NumberInput(attrs={'class': 'form-input', 'min': 1970, 'max': 2026}),
        }
