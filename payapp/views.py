from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.contrib import messages
from .models import Transaction, CustomUser
from .forms import PaymentForm, PaymentRequestForm

@login_required
def make_payment_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount = form.cleaned_data['amount']
            recipient = get_object_or_404(CustomUser, username=recipient_username)
            if request.user.balance >= amount:
                with db_transaction.atomic():
                    request.user.balance -= amount
                    recipient.balance += amount
                    request.user.save()
                    recipient.save()
                    Transaction.objects.create(sender=request.user, recipient=recipient, amount=amount, transaction_type='PAYMENT', status='COMPLETED')
                messages.success(request, "Payment made successfully.")
                return redirect('webapps/make_payment.html')
            else:
                messages.error(request, "Insufficient funds.")
    else:
        form = PaymentForm()
    return render(request, 'webapps/make_payment.html', {'form': form})

@login_required
def request_payment_view(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            sender_username = form.cleaned_data['sender_username']
            amount = form.cleaned_data['amount']
            sender = get_object_or_404(CustomUser, username=sender_username)
            Transaction.objects.create(sender=sender, recipient=request.user, amount=amount, transaction_type='REQUEST', status='PENDING')
            messages.success(request, "Payment request made successfully.")
            return redirect('webapps/request_payment.html')
    else:
        form = PaymentRequestForm()
    return render(request, 'webapps/request_payment.html', {'form': form})

@login_required
def transaction_notifications(request):
    sent_transactions = Transaction.objects.filter(sender=request.user)
    received_transactions = Transaction.objects.filter(recipient=request.user)

    # Debug: print to console to verify if queries are returning transactions
    print(f"Sent Transactions: {sent_transactions}")
    print(f"Received Transactions: {received_transactions}")

    return render(request, 'webapps/transaction_notifications.html', {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
    })

