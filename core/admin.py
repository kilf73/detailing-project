from django.contrib import admin
from .models import User, BodyType, Car, Box, ServiceCategory, Service, Booking, Review, LoyaltyTransaction

admin.site.register(User)
admin.site.register(BodyType)
admin.site.register(Car)
admin.site.register(Box)
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(LoyaltyTransaction)
