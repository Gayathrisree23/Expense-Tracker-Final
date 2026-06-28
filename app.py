from flask import Flask, render_template, request, redirect, session, Response
import csv
import os
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'expensetracker2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)


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
    safe_name = "".join(c for c in username if c.isalnum() or c in ('-', '_')).strip()
    return os.path.join(DATA_DIR, f'expenses_{safe_name}.csv')


def get_expenses(username):
    FILE = get_file(username)
    if not os.path.exists(FILE):
        return []
    with open(FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_expenses(username, expenses):
    FILE = get_file(username)
    with open(FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'category', 'date'])
        writer.writeheader()
        writer.writerows(expenses)


def get_category_data(expenses):
    categories = {
        'Food': {'icon': '🍜', 'amount': 0, 'count': 0},
        'Transport': {'icon': '🚗', 'amount': 0, 'count': 0},
        'Shopping': {'icon': '🛍️', 'amount': 0, 'count': 0},
        'Health': {'icon': '💊', 'amount': 0, 'count': 0},
        'Other': {'icon': '✨', 'amount': 0, 'count': 0},
    }
    for e in expenses:
        cat = e.get('category', 'Other')
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
        expenses = [e for e in expenses if e.get('category') == category_filter]
    if search:
        expenses = [e for e in expenses if search.lower() in e.get('name', '').lower()]

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
            monthly_summary[m] = monthly_summary.get(m, 0) + float(e['amount'])

    # Attach the REAL index from the full list so edit/delete always hit the
    # correct row, even when a filter or search is narrowing what's shown.
    indexed_expenses = []
    for e in expenses:
        try:
            real_index = all_expenses.index(e)
        except ValueError:
            real_index = None
        indexed_expenses.append({**e, '_index': real_index})

    return render_template('index.html',
        expenses=indexed_expenses,
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
    name = request.form['name']
    amount = request.form['amount']
    category = request.form['category']
    entered_date = request.form.get('date', '').strip()
    expense_date = entered_date if entered_date else str(date.today())

    expenses = get_expenses(username)
    expenses.append({
        'name': name,
        'amount': amount,
        'category': category,
        'date': expense_date
    })
    save_expenses(username, expenses)
    return redirect('/home')


@app.route('/delete/<int:index>')
def delete(index):
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    expenses = get_expenses(username)
    if 0 <= index < len(expenses):
        expenses.pop(index)
        save_expenses(username, expenses)
    return redirect('/home')


@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    expenses = get_expenses(username)

    if index < 0 or index >= len(expenses):
        return redirect('/home')

    if request.method == 'POST':
        expenses[index]['name'] = request.form['name']
        expenses[index]['amount'] = request.form['amount']
        expenses[index]['category'] = request.form['category']
        expenses[index]['date'] = request.form.get('date') or expenses[index]['date']
        save_expenses(username, expenses)
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