from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('services/', views.service_list_view, name='service_list'),
    path('booking/', views.booking_view, name='booking'),
    path('auth/', views.auth_view, name='auth'),
]
