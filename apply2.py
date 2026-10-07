import re

with open('finance/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'def ' in line and '(request' in line:
        new_lines.append(line)
        if not 'set_currency' in line:
            new_lines.append("    currency_symbol = request.session.get('currency_symbol', '₹')\n")
    else:
        # replace ₹ with {currency_symbol} in f-strings where applicable, but we have to be careful
        if 'f"' in line or "f'" in line:
            line = line.replace('₹', '{currency_symbol}')
        else:
            # if it's just a normal string with ₹, make it an f-string or ignore
            if '₹100/mo' in line:
                line = line.replace('₹100', '{currency_symbol}100')
                if not 'f"' in line:
                    line = line.replace('"', 'f"')
        new_lines.append(line)

with open('finance/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
