from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from payapp.models import Transaction
from django.contrib import messages
from django.db import transaction as db_transaction
from django.core.mail import send_mail
from django.conf import settings
from payapp.utils import convert_currency
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.test import Client
from payapp.constants import CURRENCY_SYMBOLS
from django.db.models import Q
from decimal import Decimal











@login_required
def home(request):
    user = request.user
    user_currency = user.currency
    user_currency_symbol = CURRENCY_SYMBOLS.get(user_currency, '$')  # Retrieve the symbol directly

    # Currency conversion client
    client = Client()

    # Helper function to convert currency
    def convert_currency(amount):
        if user_currency != "GBP":
            response = client.get(f'/conversion/GBP/{user_currency}/{amount}/')
            if response.status_code == 200:
                return Decimal(response.json().get('converted_amount'))
            else:
                # Handle conversion failure
                return None
        return amount

    # Fetch recent transactions and convert if necessary
    recent_transactions = Transaction.objects.filter(
        Q(sender=user, transaction_type="PAYMENT") | 
        Q(recipient=user, transaction_type="REQUEST") |
        Q(recipient=user, transaction_type="PAYMENT") | 
        Q(sender=user, transaction_type="REQUEST")
    ).order_by('-created_at')[:5]  # Ensure you have a 'created_at' field or equivalent

    # Convert transaction amounts
    for transaction in recent_transactions:
        converted_amount = convert_currency(transaction.amount) or transaction.amount
        transaction.amount = converted_amount  # Update the transaction amount to the converted amount for display

    # Assuming 'user' model has a 'balance' field
    account_balance = user.balance

    context = {
        'account_balance': account_balance,
        'recent_transactions': recent_transactions,
        'user_currency_symbol': user_currency_symbol
    }
    return render(request, 'register/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            selected_currency = form.cleaned_data['currency']
            initial_balance_in_gbp = 1000

            # Use the Django test client for the conversion
            client = Client()
            response = client.get(f'/conversion/GBP/{selected_currency}/{initial_balance_in_gbp}/')

            if response.status_code == 200:
                user.balance = response.json().get('converted_amount', initial_balance_in_gbp)
            else:
                messages.error(request, "The currency conversion service is currently unavailable. Please try again later.")
                return render(request, 'register/register.html', {'form': form})

            user.currency = selected_currency
            user.save()
            
            login(request, user)
            send_mail(
                'Welcome to WebApp 2024!',
                'Hello, thank you for registering with our app.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "You have been successfully registered.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    user_currency = user.currency
    user_currency_symbol = CURRENCY_SYMBOLS.get(user_currency, '$')  # Retrieve the symbol directly

    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        if 'update_profile' in request.POST and user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('profile')
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important for updating session with new password
            messages.success(request, 'Your password was successfully updated.')
            return redirect('profile')
    else:
        user_form = CustomUserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
    pending_requests = Transaction.objects.filter(
        recipient=user,
        status='PENDING',
        transaction_type='REQUEST'
    ).exclude(sender=user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'pending_requests': pending_requests,
        'user_currency_symbol': user_currency_symbol,  # Add this line
    }
    return render(request, 'register/profile.html', context)


@login_required
def respond_to_request(request, transaction_id, action):
    transaction = get_object_or_404(Transaction, id=transaction_id, recipient=request.user, status='PENDING')

    if action == 'accept':
        # Logic for accepting the payment request
        with db_transaction.atomic():
            sender = transaction.sender
            recipient = transaction.recipient

            # Ensure that the recipient (Y) is the one making the payment to the sender (X), when accepting the request
            if recipient.balance >= transaction.amount:  # Check if Y has enough balance
                recipient.balance -= transaction.amount  # Deduct from Y's account
                sender.balance += transaction.amount  # Add to X's account
                recipient.save()
                sender.save()

                transaction.status = 'COMPLETED'  # Update the transaction status
                transaction.save()

                messages.success(request, "Payment request accepted.")
            else:
                messages.error(request, "You have insufficient funds.")
    elif action == 'reject':
        # Logic for rejecting the payment request
        transaction.status = 'REJECTED'  # Update the transaction status
        transaction.save()

        messages.info(request, "Payment request rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('profile')  # Redirect to the profile page or any other appropriate page
