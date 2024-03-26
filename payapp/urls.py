from django.urls import path
from . import views

urlpatterns = [
    path('make_payment/', views.make_payment_view, name='make_payment'),
    path('request_payment/', views.request_payment_view, name='request_payment'),
    path('transactions/', views.transaction_notifications, name='transaction_notifications'),
    # Add other URLs as needed
]
