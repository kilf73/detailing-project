from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingCreateForm, CarAddForm, LoginForm
from .models import BodyType, Box, Booking, BookingService, Car, Review, Service, ServiceCategory, User


def _get_demo_user():
    user, _ = User.objects.get_or_create(
        email='client@detailing73.ru',
        defaults={
            'phone': '+7 900 000 00 00',
            'first_name': 'Алексей',
            'last_name': 'Смирнов',
            'bonus_balance': Decimal('1250.00'),
        }
    )
    return user


def home_view(request):
    body_types = BodyType.objects.all()
    popular_services = Service.objects.filter(is_active=True).select_related('category')[:3]
    boxes = Box.objects.filter(is_active=True)
    reviews = Review.objects.select_related('user', 'booking')[:3]
    return render(request, 'core/home.html', {
        'body_types': body_types,
        'popular_services': popular_services,
        'boxes': boxes,
        'reviews': reviews,
    })


def service_list_view(request):
    qs = Service.objects.filter(is_active=True).select_related('category')
    categories = ServiceCategory.objects.all()
    body_types = BodyType.objects.all()

    cat_slug = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()
    body_id = request.GET.get('body_type', '')

    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))

    selected_body = BodyType.objects.filter(pk=body_id).first() if body_id.isdigit() else body_types.first()
    coeff = selected_body.price_coefficient if selected_body else Decimal('1.00')

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/service_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'body_types': body_types,
        'selected_body': selected_body,
        'coeff': coeff,
        'active_category': cat_slug,
        'query': q,
    })


def service_detail_view(request, pk):
    service = get_object_or_404(Service.objects.select_related('category'), pk=pk, is_active=True)
    body_types = BodyType.objects.all()
    related_services = Service.objects.filter(category=service.category, is_active=True).exclude(pk=pk)[:3]
    return render(request, 'core/service_detail.html', {
        'service': service,
        'body_types': body_types,
        'related_services': related_services,
    })


def booking_view(request):
    user = _get_demo_user()
    if request.method == 'POST':
        form = BookingCreateForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = user
            selected_services = form.cleaned_data['services']
            coeff = booking.car.body_type.price_coefficient
            total_price = sum((s.base_price * coeff for s in selected_services), Decimal('0.00'))
            total_minutes = sum(s.base_duration_minutes for s in selected_services) or 60
            dt_start = datetime.combine(booking.booking_date, booking.start_time)
            booking.end_time = (dt_start + timedelta(minutes=total_minutes)).time()
            booking.total_price = total_price
            booking.save()
            for srv in selected_services:
                BookingService.objects.create(
                    booking=booking,
                    service=srv,
                    price_at_moment=srv.base_price * coeff
                )
            messages.success(request, f'Запись №{booking.id} успешно оформлена! Ждём вас {booking.booking_date:%d.%m.%Y} в {booking.start_time:%H:%M}.')
            return redirect('core:profile')
        messages.error(request, 'Проверьте правильность заполнения формы записи.')
    else:
        initial_srv = request.GET.get('service')
        initial = {}
        if initial_srv and initial_srv.isdigit():
            initial['services'] = [int(initial_srv)]
        form = BookingCreateForm(initial=initial)

    form.fields['car'].queryset = Car.objects.filter(user=user)
    return render(request, 'core/booking.html', {
        'form': form,
        'boxes': Box.objects.filter(is_active=True),
    })


def profile_view(request):
    user = _get_demo_user()
    if request.method == 'POST':
        car_form = CarAddForm(request.POST)
        if car_form.is_valid():
            car = car_form.save(commit=False)
            car.user = user
            car.save()
            messages.success(request, f'Автомобиль {car.brand} {car.model} добавлен в гараж.')
            return redirect('core:profile')
        messages.error(request, 'Не удалось добавить автомобиль. Проверьте поля формы.')
    else:
        car_form = CarAddForm()

    bookings_qs = Booking.objects.filter(user=user).select_related('car', 'box').prefetch_related('services')
    paginator = Paginator(bookings_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/profile.html', {
        'profile_user': user,
        'cars': user.cars.select_related('body_type'),
        'page_obj': page_obj,
        'car_form': car_form,
    })


def about_view(request):
    boxes = Box.objects.all()
    reviews = Review.objects.select_related('user')[:6]
    return render(request, 'core/about.html', {
        'boxes': boxes,
        'reviews': reviews,
    })


def search_results_view(request):
    q = request.GET.get('q', '').strip()
    services = Service.objects.none()
    if q:
        services = Service.objects.filter(
            Q(name__icontains=q) | Q(category__name__icontains=q),
            is_active=True
        ).select_related('category')
    paginator = Paginator(services, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/search_results.html', {
        'query': q,
        'page_obj': page_obj,
        'total_count': services.count(),
    })


def auth_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Вы успешно вошли в личный кабинет.')
            return redirect('core:profile')
        messages.error(request, 'Ошибка: Неверный логин или пароль. Попробуйте ещё раз.')
    else:
        form = LoginForm()
    return render(request, 'core/auth.html', {'form': form})


def api_services_filter(request):
    cat = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()
    body_id = request.GET.get('body_type', '')

    qs = Service.objects.filter(is_active=True).select_related('category')
    if cat:
        qs = qs.filter(category__slug=cat)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))

    coeff = Decimal('1.00')
    if body_id.isdigit():
        bt = BodyType.objects.filter(pk=int(body_id)).first()
        if bt:
            coeff = bt.price_coefficient

    items = [
        {
            'id': s.id,
            'name': s.name,
            'category': s.category.name,
            'duration': s.base_duration_minutes,
            'price': float(round(s.base_price * coeff, 2)),
        }
        for s in qs[:20]
    ]
    return JsonResponse({'count': len(items), 'items': items})


def api_box_slots(request):
    box_id = request.GET.get('box_id')
    date_str = request.GET.get('date') or str(timezone.localdate())
    all_slots = ['09:00', '11:00', '13:00', '15:00', '17:00', '19:00']
    busy = set()
    if box_id and box_id.isdigit():
        booked = Booking.objects.filter(
            box_id=int(box_id),
            booking_date=date_str,
            status__in=['new', 'confirmed', 'in_progress']
        ).values_list('start_time', flat=True)
        busy = {t.strftime('%H:%M') for t in booked}

    slots = [{'time': t, 'is_free': t not in busy} for t in all_slots]
    return JsonResponse({'date': date_str, 'slots': slots})
