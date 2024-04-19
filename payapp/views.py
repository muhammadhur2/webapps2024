from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.contrib import messages
from .models import Transaction, CustomUser
from .forms import PaymentForm, PaymentRequestForm
from .constants import CURRENCY_SYMBOLS
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseBadRequest
from payapp.utils import convert_currency
from django.test import Client
from decimal import Decimal






# @login_required
# def make_payment_view(request):
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             recipient_username = form.cleaned_data['recipient_username']
#             amount = form.cleaned_data['amount']
#             recipient = get_object_or_404(CustomUser, username=recipient_username)
#             if request.user.balance >= amount:
#                 with db_transaction.atomic():
#                     request.user.balance -= amount
#                     recipient.balance += amount
#                     request.user.save()
#                     recipient.save()
#                     Transaction.objects.create(sender=request.user, recipient=recipient, amount=amount, transaction_type='PAYMENT', status='COMPLETED')

#                 # Send an email notification
#                 send_mail(
#                     subject='Payment Sent',
#                     message=f'You have sent £{amount} to {recipient.username}.',
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[request.user.email],
#                     fail_silently=False,
#                 )

#                 messages.success(request, "Payment made successfully.")
#                 return redirect('webapps/make_payment.html')
#             else:
#                 messages.error(request, "Insufficient funds.")
#     else:
#         form = PaymentForm()
#     return render(request, 'webapps/make_payment.html', {'form': form})


@login_required
def make_payment_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount = Decimal(form.cleaned_data['amount'])
            recipient = get_object_or_404(CustomUser, username=recipient_username)

            client = Client()
            if request.user.currency != 'GBP':
                response = client.get(f'/conversion/{request.user.currency}/GBP/{amount}/')
                if response.status_code == 200:
                    amount1 = Decimal(response.json().get('converted_amount'))
                else:
                    messages.error(request, "Currency conversion service is currently unavailable. Please try again later.")
                    return render(request, 'webapps/make_payment.html', {'form': form})

            if request.user.balance >= amount:
                with db_transaction.atomic():
                    request.user.balance -= amount
                    recipient_amount = amount  
                    if recipient.currency != 'GBP':
                        response = client.get(f'/conversion/GBP/{recipient.currency}/{amount1}/')
                        if response.status_code == 200:
                            recipient_amount = Decimal(response.json().get('converted_amount'))
                    
                    recipient.balance += recipient_amount
                    request.user.save()
                    recipient.save()
                    Transaction.objects.create(sender=request.user, recipient=recipient, amount=amount, transaction_type='PAYMENT', status='COMPLETED')

                send_mail(
                    subject='Payment Sent',
                    message=f'You have sent {request.user.currency} {amount} to {recipient.username}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.success(request, "Payment made successfully.")
                return redirect('/')
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
            amount = Decimal(form.cleaned_data['amount'])  
            sender = get_object_or_404(CustomUser, username=sender_username)

            
            client = Client()

            if request.user.currency != 'GBP':
                response = client.get(f'/conversion/{request.user.currency}/GBP/{amount}/')
                if response.status_code == 200:
                    amount = Decimal(response.json().get('converted_amount'))
                else:
                    messages.error(request, "Currency conversion service is currently unavailable. Please try again later.")
                    return render(request, 'webapps/request_payment.html', {'form': form})

            Transaction.objects.create(
                sender=request.user, 
                recipient=sender, 
                amount=amount, 
                transaction_type='REQUEST', 
                status='PENDING'
            )

            
            send_mail(
                subject='Payment Request Received',
                message=f'You have received a payment request of {sender.currency} {amount} from {request.user.username}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sender.email],
                fail_silently=False,
            )

            messages.success(request, "Payment request made successfully.")
            return redirect('/')
    else:
        form = PaymentRequestForm()
    return render(request, 'webapps/request_payment.html', {'form': form})


@login_required
def transaction_notifications(request):
    user = request.user
    user_currency = user.currency
    user_currency_symbol = CURRENCY_SYMBOLS.get(user_currency, '$')  

    client = Client()

    
    def convert_currency(amount):
        if user_currency != "GBP":
            response = client.get(f'/conversion/GBP/{user_currency}/{amount}/')
            if response.status_code == 200:
                return Decimal(response.json().get('converted_amount'))
            else:
                
                return None
        return amount

    
    sent_transactions = []
    received_transactions = []
    pending_requests = []

    for transaction in Transaction.objects.filter(Q(sender=request.user, transaction_type="PAYMENT") | 
        Q(recipient=request.user, transaction_type="REQUEST")):
        if transaction.transaction_type == 'REQUEST' and transaction.status == 'PENDING' and transaction.recipient.currency=="GBP":
            sent_transactions.append(transaction)
            print(transaction)
        else:
        
            converted_amount = convert_currency(transaction.amount) or transaction.amount
            transaction.amount = converted_amount  
             
            sent_transactions.append(transaction)

    for transaction in Transaction.objects.filter(Q(recipient=request.user, transaction_type="PAYMENT") | 
        Q(sender=request.user, transaction_type="REQUEST")):
        converted_amount = convert_currency(transaction.amount) or transaction.amount
        transaction.amount = converted_amount  
        received_transactions.append(transaction)

    for transaction in Transaction.objects.filter(Q(recipient=request.user, transaction_type="REQUEST")):

        if transaction.transaction_type == 'REQUEST' and transaction.status == 'PENDING' and transaction.recipient.currency=="GBP":

            pending_requests.append(transaction)
        elif transaction.transaction_type == 'REQUEST' and transaction.status == 'PENDING' and transaction.recipient.currency!="GBP":
            converted_amount = convert_currency(transaction.amount) or transaction.amount
            transaction.amount = converted_amount  
            pending_requests.append(transaction)          


                

    return render(request, 'webapps/transaction_notifications.html', {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
        'pending_requests': pending_requests,
        'user_currency_symbol': user_currency_symbol,
    })


@login_required
def respond_to_request(request, transaction_id, action):
    transaction = get_object_or_404(Transaction, id=transaction_id, recipient=request.user, status='PENDING')

    if action == 'accept':

        with db_transaction.atomic():
            sender = transaction.sender
            recipient = transaction.recipient


            client = Client()
            recipient_amount = transaction.amount
            if recipient.currency != 'GBP':
                response = client.get(f'/conversion/GBP/{recipient.currency}/{transaction.amount}/')
                if response.status_code == 200:
                    recipient_amount = Decimal(response.json().get('converted_amount'))

            sender_amount = transaction.amount
            if sender.currency != 'GBP':
                response = client.get(f'/conversion/GBP/{sender.currency}/{transaction.amount}/')
                if response.status_code == 200:
                    sender_amount = Decimal(response.json().get('converted_amount'))

            




            if recipient.balance >= recipient_amount:  
                recipient.balance -= recipient_amount  
                sender.balance += sender_amount  
                recipient.save()
                sender.save()

                transaction.status = 'COMPLETED'  
                transaction.save()

                messages.success(request, "Payment request accepted.")
            else:
                messages.error(request, "You have insufficient funds.")
    elif action == 'reject':

        transaction.status = 'REJECTED'  
        transaction.save()

        messages.info(request, "Payment request rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('/')  

@login_required
def transaction_invoice(request, transaction_id):
    user_currency = request.user.currency
    user_currency_symbol = CURRENCY_SYMBOLS.get(user_currency, '$')  
    
    client = Client()


    def convert_currency(amount):
        if user_currency != "GBP":
            response = client.get(f'/conversion/GBP/{user_currency}/{amount}/')
            if response.status_code == 200:
                return Decimal(response.json().get('converted_amount'))
            else:

                return None
        return amount
    try:

        transaction = Transaction.objects.get(id=transaction_id, sender=request.user)
    except Transaction.DoesNotExist:

        transaction = get_object_or_404(Transaction, id=transaction_id, recipient=request.user)

    if user_currency != "GBP":
        converted_amount = convert_currency(transaction.amount)
        if converted_amount is not None:
            transaction.amount = converted_amount
        else:
            
            pass    

    return render(request, 'webapps/transaction_invoice.html', {
        'transaction': transaction,
        'user_currency_symbol': user_currency_symbol,
    })




def conversion_service(request, currency1, currency2, amount):
    try:
        amount = Decimal(amount)
    except (ValueError, Decimal.InvalidOperation):
        return HttpResponseBadRequest("Amount must be a valid number.")

    supported_currencies = ['GBP', 'USD', 'EUR']
    if currency1 not in supported_currencies or currency2 not in supported_currencies:
        return JsonResponse({'error': 'One or both currencies are not supported.'}, status=400)
    
    converted_amount = convert_currency(amount, currency1, currency2)
    return JsonResponse({'converted_amount': str(converted_amount)})