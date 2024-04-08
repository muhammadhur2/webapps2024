from decimal import Decimal

def convert_currency(amount, from_currency, to_currency):
    # Simplified example with hard-coded rates
    rates = {
        'GBP': {'USD': Decimal('1.3'), 'EUR': Decimal('1.1')},
        'USD': {'GBP': Decimal('0.77'), 'EUR': Decimal('0.85')},
        'EUR': {'GBP': Decimal('0.9'), 'USD': Decimal('1.18')},
    }
    if from_currency == to_currency:
        return amount
    else:
        # Ensure the amount is a Decimal, and perform multiplication with Decimal
        amount = Decimal(amount) if not isinstance(amount, Decimal) else amount
        converted_amount = amount * rates[from_currency][to_currency]
        # Use quantize to round to 2 decimal places properly
        return converted_amount.quantize(Decimal('0.01'))
