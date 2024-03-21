from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'amount')
    readonly_fields = ('created_at',)

admin.site.register(Transaction, TransactionAdmin)
