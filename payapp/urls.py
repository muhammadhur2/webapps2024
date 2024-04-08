from django.urls import path
from . import views

urlpatterns = [
    path('make_payment/', views.make_payment_view, name='make_payment'),
    path('request_payment/', views.request_payment_view, name='request_payment'),
    path('transactions/', views.transaction_notifications, name='transaction_notifications'),
    path('transaction/<int:transaction_id>/invoice/', views.transaction_invoice, name='transaction_invoice'),
    path('conversion/<str:currency1>/<str:currency2>/<int:amount>', views.conversion_service, name='conversion_service'),


    # Add other URLs as needed
]
