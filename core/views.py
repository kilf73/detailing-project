from django.shortcuts import render

def home_view(request):
    return render(request, 'core/home.html', {'title': 'Главная — Детейлинг-Бокс'})

def service_list_view(request):
    return render(request, 'core/service_list.html', {'title': 'Услуги и каталог'})

def booking_view(request):
    return render(request, 'core/booking.html', {'title': 'Оформление записи'})

def auth_view(request):
    return render(request, 'core/auth.html', {'title': 'Вход и регистрация'})
