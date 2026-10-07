import os
import re
import glob

# 1. Create context_processors.py
os.makedirs('core', exist_ok=True)
with open('core/context_processors.py', 'w', encoding='utf-8') as f:
    f.write('''def currency(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    currency_name = request.session.get('currency_name', 'rupees')
    return {'currency_symbol': currency_symbol, 'currency_name': currency_name}
''')

# 2. Modify settings.py to include context processor
with open('core/settings.py', 'r', encoding='utf-8') as f:
    settings = f.read()
if 'core.context_processors.currency' not in settings:
    settings = settings.replace(
        "'django.contrib.messages.context_processors.messages',",
        "'django.contrib.messages.context_processors.messages',\n                'core.context_processors.currency',"
    )
    with open('core/settings.py', 'w', encoding='utf-8') as f:
        f.write(settings)

# 3. Add view to finance/views.py
with open('finance/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

if 'def set_currency' not in views_content:
    new_view = '''
from django.shortcuts import redirect
def set_currency(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        currency_map = {
            'USA': ('$', 'dollars'),
            'India': ('₹', 'rupees'),
            'UK': ('£', 'pounds'),
            'Europe': ('€', 'euros'),
            'Japan': ('¥', 'yen'),
            'Australia': ('A$', 'dollars')
        }
        symbol, name = currency_map.get(country, ('₹', 'rupees'))
        request.session['currency_symbol'] = symbol
        request.session['currency_name'] = name
        request.session['country'] = country
    return redirect(request.META.get('HTTP_REFERER', '/'))
'''
    views_content += new_view
    with open('finance/views.py', 'w', encoding='utf-8') as f:
        f.write(views_content)

# 4. Add URL to finance/urls.py
with open('finance/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()
if 'set_currency' not in urls_content:
    urls_content = urls_content.replace(
        "urlpatterns = [",
        "urlpatterns = [\n    path('set_currency/', views.set_currency, name='set_currency'),"
    )
    with open('finance/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)

# 5. Modify base.html to add country selector
with open('templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

country_selector = '''
        <div style="margin-right: 1rem;">
            <form action="/set_currency/" method="POST" style="display: inline-block;">
                {% csrf_token %}
                <select name="country" onchange="this.form.submit()" style="padding: 0.3rem; border-radius: 4px; background: var(--surface-light); color: var(--text-primary); border: 1px solid var(--border-color);">
                    <option value="India" {% if request.session.country == 'India' %}selected{% endif %}>India (₹)</option>
                    <option value="USA" {% if request.session.country == 'USA' %}selected{% endif %}>USA ($)</option>
                    <option value="UK" {% if request.session.country == 'UK' %}selected{% endif %}>UK (£)</option>
                    <option value="Europe" {% if request.session.country == 'Europe' %}selected{% endif %}>Europe (€)</option>
                    <option value="Japan" {% if request.session.country == 'Japan' %}selected{% endif %}>Japan (¥)</option>
                    <option value="Australia" {% if request.session.country == 'Australia' %}selected{% endif %}>Australia (A$)</option>
                </select>
            </form>
        </div>
'''
if 'set_currency' not in base_html:
    base_html = base_html.replace('<div class="nav-actions">', '<div class="nav-actions">\n' + country_selector)
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_html)

# 6. Replace ₹ with {{ currency_symbol }} in all templates
for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    changed = False
    if '₹' in content:
        content = content.replace('₹', '{{ currency_symbol }}')
        changed = True
    if re.search(r'(?i)\\brupees\\b', content):
        content = re.sub(r'(?i)\\brupees\\b', '{{ currency_name }}', content)
        changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated', filepath)
