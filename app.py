from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "expenses.json"


# Create JSON file if it doesn't exist
def initialize_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            json.dump([], file)


# Load transactions
def load_transactions():
    # Create the file if it does not exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            json.dump([], file)

    try:
        with open(DATA_FILE, "r") as file:
            data = file.read().strip()

            # If file is empty
            if not data:
                return []

            return json.loads(data)

    except (json.JSONDecodeError, FileNotFoundError):
        return []

# Save transactions
def save_transactions(transactions):
    with open(DATA_FILE, "w") as file:
        json.dump(transactions, file, indent=4)


@app.route("/")
def index():
    transactions = load_transactions()

    total_income = sum(
        float(item["amount"])
        for item in transactions
        if item["type"] == "Income"
    )

    total_expense = sum(
        float(item["amount"])
        for item in transactions
        if item["type"] == "Expense"
    )

    balance = total_income - total_expense

    # Category-wise expenses for chart
    category_data = {}

    for item in transactions:
        if item["type"] == "Expense":
            category = item["category"]
            amount = float(item["amount"])

            if category in category_data:
                category_data[category] += amount
            else:
                category_data[category] = amount

    return render_template(
        "index.html",
        transactions=transactions[::-1],
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        categories=list(category_data.keys()),
        amounts=list(category_data.values())
    )


@app.route("/add", methods=["POST"])
def add_expense():

    transactions = load_transactions()

    transaction = {
        "id": int(datetime.now().timestamp() * 1000),
        "title": request.form["title"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "type": request.form["type"],
        "date": request.form["date"]
    }

    transactions.append(transaction)

    save_transactions(transactions)

    return redirect(url_for("index"))


@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):

    transactions = load_transactions()

    transactions = [
        item for item in transactions
        if item["id"] != transaction_id
    ]

    save_transactions(transactions)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)