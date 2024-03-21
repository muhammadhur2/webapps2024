from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='register/login.html'), name='login'),
    path('accounts/profile/', views.profile, name='profile'),
]