from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class User(models.Model):
    ROLE_CHOICES = (('client', 'Клиент'), ('admin', 'Администратор'))
    email = models.EmailField(unique=True, verbose_name="Email (логин)")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', verbose_name="Роль")
    bonus_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Бонусный баланс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class BodyType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тип кузова")
    price_coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'), validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('3.00'))], verbose_name="Коэффициент цены")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип кузова"
        verbose_name_plural = "Типы кузовов"
        ordering = ['price_coefficient']

    def __str__(self):
        return f"{self.name} (коэф. {self.price_coefficient})"

class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars', verbose_name="Владелец")
    body_type = models.ForeignKey(BodyType, on_delete=models.PROTECT, related_name='cars', verbose_name="Тип кузова")
    brand = models.CharField(max_length=50, verbose_name="Марка")
    model = models.CharField(max_length=50, verbose_name="Модель")
    license_plate = models.CharField(max_length=20, unique=True, verbose_name="Госномер")
    manufacture_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Год выпуска")

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ['brand', 'model']

    def __str__(self):
        return f"{self.brand} {self.model} [{self.license_plate}]"

class Box(models.Model):
    BOX_TYPES = (('wash', 'Моечный бокс'), ('detailing', 'Детейлинг-бокс'), ('universal', 'Универсальный'))
    name = models.CharField(max_length=50, unique=True, verbose_name="Название бокса")
    box_type = models.CharField(max_length=20, choices=BOX_TYPES, default='universal', verbose_name="Специализация")
    is_active = models.BooleanField(default=True, verbose_name="Доступен к работе")

    class Meta:
        verbose_name = "Рабочий бокс"
        verbose_name_plural = "Рабочие боксы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_box_type_display()})"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Слаг (URL)")

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name="Категория")
    name = models.CharField(max_length=150, verbose_name="Название услуги")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Базовая цена (руб.)")
    base_duration_minutes = models.PositiveSmallIntegerField(verbose_name="Длительность (мин.)")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} — {self.base_price} руб."

class Booking(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Клиент")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings', verbose_name="Автомобиль")
    box = models.ForeignKey(Box, on_delete=models.PROTECT, related_name='bookings', verbose_name="Рабочий бокс")
    services = models.ManyToManyField(Service, through='BookingService', related_name='bookings', verbose_name="Услуги")
    booking_date = models.DateField(verbose_name="Дата записи")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания брони")

    class Meta:
        verbose_name = "Запись / Бронирование"
        verbose_name_plural = "Записи / Бронирования"
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"Заказ #{self.id} от {self.booking_date} ({self.get_status_display()})"

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name="Запись")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент заказа")

    class Meta:
        verbose_name = "Состав заказа"
        verbose_name_plural = "Состав заказов"
        unique_together = ('booking', 'service')

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review', verbose_name="Запись")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Клиент")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оценка (1-5)")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

class LoyaltyTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_transactions', verbose_name="Клиент")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='loyalty_ops', verbose_name="Заказ")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма бонусов (+/-)")
    description = models.CharField(max_length=255, verbose_name="Описание операции")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата операции")

    class Meta:
        verbose_name = "Бонусная транзакция"
        verbose_name_plural = "Бонусные транзакции"
        ordering = ['-created_at']
