from django.urls import path
from . import views

urlpatterns = [
    path('make_payment/', views.make_payment_view, name='make_payment'),
    path('request_payment/', views.request_payment_view, name='request_payment'),
    path('transactions/', views.transaction_notifications, name='transaction_notifications'),
    path('transaction/<int:transaction_id>/invoice/', views.transaction_invoice, name='transaction_invoice'),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>/', views.conversion_service, name='conversion_service'),
    path('respond_to_request/<int:transaction_id>/<str:action>/', views.respond_to_request, name='respond_to_request'),



    # Add other URLs as needed
]
