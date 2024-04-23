from django import forms

class PaymentForm(forms.Form):
    recipient_email = forms.CharField(max_length=150, label='Recipient Email')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount')

class PaymentRequestForm(forms.Form):
    sender_email = forms.CharField(max_length=150, label='Sender Email')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount')
