# ✨ Expense Tracker

A full-stack web application to track daily expenses, set monthly budgets, and visualize spending by category — built as a college mini-project.

🔗 **Live demo:** Run locally (see instructions below) — not deployed online.

---

## 📋 Features

- **User login** — each person logs in with just their name and sets a monthly budget; data is kept separate per user
- **Add, edit, and delete expenses** — full CRUD (Create, Read, Update, Delete) functionality
- **Search and filter** — find expenses by name or category instantly
- **Month view & All-time view** — see spending for the current month or across all time
- **Monthly overview** — visual bar comparison of spending across different months
- **Budget tracking** — progress bar showing how much of the monthly budget has been used, with alerts when nearing or exceeding it
- **Spending breakdown** — category-wise totals (Food, Transport, Shopping, Health, Other) with a donut chart
- **Export to CSV** — download your expense history anytime
- **Dark mode** — toggle between light and dark themes, remembered across visits
- **Responsive, custom-designed UI** — soft pink/lavender theme built from scratch with CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Templating | Jinja2 |
| Frontend | HTML, CSS |
| Charts | Chart.js |
| Data storage | CSV files (per-user) |
| Fonts | Google Fonts (Playfair Display, DM Sans) |

---

## 🚀 Running it locally

**Prerequisites:** Python 3 installed on your computer.

1. Clone this repository
   ```bash
   git clone https://github.com/Gayathrisree23/Expense-Tracker-Final.git
   cd Expense-Tracker-Final
   ```

2. Install the required package
   ```bash
   pip install flask
   ```

3. Run the app
   ```bash
   python app.py
   ```

4. Open your browser and go to
   ```
   http://127.0.0.1:5000
   ```

5. Enter your name and a monthly budget to get started 🌸

---

## 📁 Project Structure

```
Expense-Tracker-Final/
├── app.py                 # Flask backend — routes, logic, data handling
├── requirements.txt       # Python dependencies
├── templates/
│   ├── login.html         # Login page
│   ├── index.html         # Main dashboard
│   └── edit.html          # Edit expense form
├── static/
│   └── style.css          # All styling, including dark mode
└── data/                  # Auto-created — stores one CSV file per user
```

---

## 💡 What I learned

This project helped me understand how a complete web application works end-to-end — from handling user sessions and form submissions on the backend (Flask), to rendering dynamic data into HTML (Jinja2), to styling and interactivity on the frontend (CSS, Chart.js), and finally version-controlling and publishing the project with Git and GitHub.

---

## 📌 Notes

- Built and tested locally; deployment (e.g. on Render) was intentionally skipped for this version to keep the project simple and stable for submission.
- Data is stored in CSV files for simplicity — a production version would use a proper database.
