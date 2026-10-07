def currency(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    currency_name = request.session.get('currency_name', 'rupees')
    return {'currency_symbol': currency_symbol, 'currency_name': currency_name}
