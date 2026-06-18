from flask import Flask, render_template, request, redirect, session, Response
import csv
import os
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'expensetracker2026'

def format_date(date_str):
    if not date_str:
        return ''
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        return d.strftime('%d-%m-%Y')
    except:
        return date_str

def format_month(month_str):
    if not month_str:
        return ''
    try:
        d = datetime.strptime(month_str, '%Y-%m')
        return d.strftime('%B %Y')
    except:
        return month_str

app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['format_month'] = format_month

def get_file(username):
    return f'/tmp/expenses_{username}.csv'

def get_expenses(username):
    FILE = get_file(username)
    if not os.path.exists(FILE):
        return []
    with open(FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_category_data(expenses):
    categories = {
        'Food': {'icon': '🍜', 'amount': 0, 'count': 0},
        'Transport': {'icon': '🚗', 'amount': 0, 'count': 0},
        'Shopping': {'icon': '🛍️', 'amount': 0, 'count': 0},
        'Health': {'icon': '💊', 'amount': 0, 'count': 0},
        'Other': {'icon': '✨', 'amount': 0, 'count': 0},
    }
    for e in expenses:
        cat = e['category']
        if cat in categories:
            categories[cat]['amount'] += float(e['amount'])
            categories[cat]['count'] += 1
    return categories

def get_months(expenses):
    months = set()
    for e in expenses:
        d = e.get('date', '')
        if d and len(d) >= 7:
            months.add(d[:7])
    return sorted(months, reverse=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        budget = request.form.get('budget', '10000').strip()
        if username:
            session['username'] = username
            session['budget'] = float(budget) if budget else 10000
            return redirect('/home')
    return render_template('login.html')

@app.route('/home')
def index():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    budget = float(session.get('budget', 10000))
    all_expenses = get_expenses(username)

    current_month = date.today().strftime('%Y-%m')
    selected_month = request.args.get('month', current_month)
    category_filter = request.args.get('category', 'All')
    search = request.args.get('search', '')
    view = request.args.get('view', 'month')

    all_months = get_months(all_expenses)
    if current_month not in all_months:
        all_months = [current_month] + all_months

    if view == 'all':
        filtered_expenses = all_expenses
    else:
        filtered_expenses = [e for e in all_expenses if e.get('date', '')[:7] == selected_month]

    expenses = filtered_expenses
    if category_filter != 'All':
        expenses = [e for e in expenses if e['category'] == category_filter]
    if search:
        expenses = [e for e in expenses if search.lower() in e['name'].lower()]

    total = sum(float(e['amount']) for e in filtered_expenses)
    highest = max((float(e['amount']) for e in filtered_expenses), default=0)
    category_data = get_category_data(filtered_expenses)
    top_category = max(category_data, key=lambda k: category_data[k]['amount']) if filtered_expenses else 'None'
    percent = min(round((total / budget) * 100), 100) if budget > 0 else 0
    remaining = budget - total
    balance_left = remaining

    monthly_summary = {}
    for e in all_expenses:
        d = e.get('date', '')
        if d and len(d) >= 7:
            m = d[:7]
            if m not in monthly_summary:
                monthly_summary[m] = 0
            monthly_summary[m] += float(e['amount'])

    return render_template('index.html',
        expenses=expenses,
        total=total,
        highest=highest,
        top_category=top_category,
        category_data=category_data,
        budget=budget,
        percent=percent,
        remaining=remaining,
        balance_left=balance_left,
        selected=category_filter,
        search=search,
        count=len(filtered_expenses),
        username=username,
        all_months=all_months,
        selected_month=selected_month,
        current_month=current_month,
        view=view,
        monthly_summary=monthly_summary
    )

@app.route('/add', methods=['POST'])
def add():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    FILE = get_file(username)
    name = request.form['name']
    amount = request.form['amount']
    category = request.form['category']
    entered_date = request.form.get('date', '').strip()
    expense_date = entered_date if entered_date else str(date.today())
    file_exists = os.path.exists(FILE) and os.path.getsize(FILE) > 0
    with open(FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'category', 'date'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'name': name,
            'amount': amount,
            'category': category,
            'date': expense_date
        })
    return redirect('/home')

@app.route('/delete/<int:index>')
def delete(index):
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    all_expenses = get_expenses(username)
    if 0 <= index < len(all_expenses):
        all_expenses.pop(index)
    FILE = get_file(username)
    with open(FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'category', 'date'])
        writer.writeheader()
        writer.writerows(all_expenses)
    return redirect('/home')

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    expenses = get_expenses(username)
    FILE = get_file(username)

    if index < 0 or index >= len(expenses):
        return redirect('/home')

    if request.method == 'POST':
        expenses[index]['name'] = request.form['name']
        expenses[index]['amount'] = request.form['amount']
        expenses[index]['category'] = request.form['category']
        expenses[index]['date'] = request.form.get('date', expenses[index]['date'])
        with open(FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'category', 'date'])
            writer.writeheader()
            writer.writerows(expenses)
        return redirect('/home')

    return render_template('edit.html', expense=expenses[index], index=index)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/export')
def export():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    expenses = get_expenses(username)
    def generate():
        yield 'name,amount,category,date\n'
        for e in expenses:
            yield f"{e['name']},{e['amount']},{e['category']},{e['date']}\n"
    return Response(generate(), mimetype='text/csv',
                     headers={'Content-Disposition': 'attachment;filename=expenses.csv'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)