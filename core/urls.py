from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('services/', views.service_list_view, name='service_list'),
    path('services/<int:pk>/', views.service_detail_view, name='service_detail'),
    path('booking/', views.booking_view, name='booking'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about_view, name='about'),
    path('search/', views.search_results_view, name='search_results'),
    path('auth/', views.auth_view, name='auth'),
    path('api/services/', views.api_services_filter, name='api_services_filter'),
    path('api/box-slots/', views.api_box_slots, name='api_box_slots'),
]
