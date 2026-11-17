from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import User, BodyType, Car, Box, ServiceCategory, Service


class Command(BaseCommand):
    help = 'Наполнение базы данных начальными данными для демонстрации'

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            email='client@detailing73.ru',
            defaults={
                'phone': '+7 900 000 00 00',
                'first_name': 'Алексей',
                'last_name': 'Смирнов',
                'bonus_balance': Decimal('1250.00'),
            }
        )

        sedan, _ = BodyType.objects.get_or_create(name='Седан', defaults={'price_coefficient': Decimal('1.00')})
        crossover, _ = BodyType.objects.get_or_create(name='Кроссовер', defaults={'price_coefficient': Decimal('1.20')})
        suv, _ = BodyType.objects.get_or_create(name='Внедорожник', defaults={'price_coefficient': Decimal('1.40')})
        bus, _ = BodyType.objects.get_or_create(name='Микроавтобус', defaults={'price_coefficient': Decimal('2.00')})

        Car.objects.get_or_create(
            license_plate='А777АА73',
            defaults={
                'user': user,
                'body_type': sedan,
                'brand': 'LADA',
                'model': 'Granta',
                'manufacture_year': 2023,
            }
        )

        Box.objects.get_or_create(name='Бокс №1', defaults={'box_type': 'wash', 'is_active': True})
        Box.objects.get_or_create(name='Бокс №2', defaults={'box_type': 'detailing', 'is_active': True})
        Box.objects.get_or_create(name='Бокс №3', defaults={'box_type': 'universal', 'is_active': True})

        cat_wash, _ = ServiceCategory.objects.get_or_create(name='Мойка', slug='wash')
        cat_chem, _ = ServiceCategory.objects.get_or_create(name='Химчистка', slug='dry-cleaning')
        cat_polish, _ = ServiceCategory.objects.get_or_create(name='Полировка и защита', slug='polishing')

        services = [
            (cat_wash, 'Трёхфазная детейлинг-мойка', Decimal('2500.00'), 90),
            (cat_wash, 'Комплексная мойка кузова и салона', Decimal('1500.00'), 60),
            (cat_chem, 'Полная химчистка салона с разбором', Decimal('14500.00'), 360),
            (cat_chem, 'Локальная химчистка сидений', Decimal('4500.00'), 120),
            (cat_polish, 'Лёгкая восстановительная полировка', Decimal('25000.00'), 480),
            (cat_polish, 'Защитное покрытие «Антидождь»', Decimal('3000.00'), 50),
            (cat_polish, 'Керамическое покрытие кузова (2 слоя)', Decimal('32000.00'), 600),
        ]
        for cat, name, price, dur in services:
            Service.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'base_price': price,
                    'base_duration_minutes': dur,
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS('Демо-данные успешно загружены!'))
