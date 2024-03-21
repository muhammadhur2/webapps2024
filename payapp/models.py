from django.db import models
from register.models import CustomUser  # Import CustomUser from register app

class Transaction(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    TRANSACTION_TYPE_CHOICES = [
        ('PAYMENT', 'Payment'),
        ('REQUEST', 'Request'),
    ]
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES, default='PAYMENT')

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"
