from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('app/', views.app_view, name='app'),
    path('api/login/', views.login_endpoint, name='login_api'),
    path('api/chat/', views.chat_endpoint, name='chat_api'),
]