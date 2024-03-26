from django import forms

class PaymentForm(forms.Form):
    recipient_username = forms.CharField(max_length=150, label='Recipient Username')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount')

class PaymentRequestForm(forms.Form):
    sender_username = forms.CharField(max_length=150, label='Sender Username')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount')
