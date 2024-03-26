from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from payapp.models import Transaction
from django.contrib import messages
from django.db import transaction as db_transaction






from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to WebApp 2024!")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Adjust the redirect to where you want users to go after registering
    else:
        form = CustomUserCreationForm()
    return render(request, 'register/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if 'update_profile' in request.POST and user_form.is_valid():
            user_form.save()
            return redirect('profile')
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important for updating session with new password
            return redirect('profile')
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    pending_requests = Transaction.objects.filter(
        recipient=request.user,
        status='PENDING',
        transaction_type='REQUEST'
    ).exclude(sender=request.user)

    # Include pending_requests in the context passed to the template
    context = {
        'user_form': user_form,
        'password_form': password_form,
        'pending_requests': pending_requests  # Add this line
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

            # Check if the sender has enough balance
            if sender.balance >= transaction.amount:
                sender.balance -= transaction.amount
                recipient.balance += transaction.amount
                sender.save()
                recipient.save()

                transaction.status = 'COMPLETED'  # Update the transaction status
                transaction.save()

                messages.success(request, "Payment request accepted.")
            else:
                messages.error(request, "Sender has insufficient funds.")

    elif action == 'reject':
        # Logic for rejecting the payment request
        transaction.status = 'REJECTED'  # Update the transaction status
        transaction.save()

        messages.info(request, "Payment request rejected.")

    else:
        messages.error(request, "Invalid action.")

    return redirect('profile')  # Redirect to the profile page or any other appropriate page