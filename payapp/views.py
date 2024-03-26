from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.contrib import messages
from .models import Transaction, CustomUser
from .forms import PaymentForm, PaymentRequestForm
from django.core.mail import send_mail
from django.conf import settings

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

                # Send an email notification
                send_mail(
                    subject='Payment Sent',
                    message=f'You have sent £{amount} to {recipient.username}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

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
            Transaction.objects.create(sender=request.user, recipient=sender, amount=amount, transaction_type='REQUEST', status='PENDING')

            # Send an email notification to the recipient of the request
            send_mail(
                subject='Payment Request Received',
                message=f'You have received a payment request of £{amount} from {request.user.username}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sender.email],  # Assuming the recipient has an 'email' field
                fail_silently=False,
            )

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

def transaction_invoice(request, transaction_id):
    # Attempt to retrieve the transaction where the current user is either the sender or the recipient
    transaction = get_object_or_404(Transaction, id=transaction_id,
                                    sender=request.user)  # Try to get as sender first

    # If the above doesn't raise a 404 but the user is not the sender,
    # check if the user is the recipient instead.
    # This avoids the issue with the `or` operation.
    if transaction.sender != request.user:
        transaction = get_object_or_404(Transaction, id=transaction_id, recipient=request.user)

    return render(request, 'webapps/transaction_invoice.html', {'transaction': transaction})
