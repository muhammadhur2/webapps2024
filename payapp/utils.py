def convert_currency(amount, from_currency, to_currency):
    # Simplified example with hard-coded rates
    rates = {
        'GBP': {'USD': 1.3, 'EUR': 1.1},
        'USD': {'GBP': 0.77, 'EUR': 0.85},
        'EUR': {'GBP': 0.9, 'USD': 1.18},
    }
    if from_currency == to_currency:
        return amount
    else:
        return round(amount * rates[from_currency][to_currency], 2)
