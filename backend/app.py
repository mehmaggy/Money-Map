import csv
import io
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db, init_db, categorize

app = Flask(__name__)
CORS(app)            # allow the React dev server to call this API
init_db()            # create tables + seed data on startup


# ---------- helpers ----------
def rows_to_list(rows):
    return [dict(r) for r in rows]

def previous_month(month):
    d = datetime.strptime(month, "%Y-%m")
    if d.month == 1:
        return f"{d.year - 1}-12"
    return f"{d.year}-{d.month - 1:02d}"

def latest_month():
    conn = get_db()
    row = conn.execute("SELECT MAX(strftime('%Y-%m', txn_date)) AS m FROM transactions").fetchone()
    conn.close()
    return row["m"] if row and row["m"] else datetime.now().strftime("%Y-%m")

def resolve_month():
    return request.args.get("month") or latest_month()


# ---------- categories & months ----------
@app.get("/api/categories")
def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    conn.close()
    return jsonify(rows_to_list(rows))

@app.get("/api/months")
def get_months():
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT strftime('%Y-%m', txn_date) AS month FROM transactions ORDER BY month DESC"
    ).fetchall()
    conn.close()
    return jsonify([r["month"] for r in rows])


# ---------- transactions ----------
@app.get("/api/transactions")
def list_transactions():
    month = request.args.get("month")
    conn = get_db()
    sql = ("SELECT t.id, t.txn_date, t.description, t.amount, t.type, c.name AS category "
           "FROM transactions t LEFT JOIN categories c ON c.id = t.category_id ")
    params = ()
    if month:
        sql += "WHERE strftime('%Y-%m', t.txn_date) = ? "
        params = (month,)
    sql += "ORDER BY t.txn_date DESC, t.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify(rows_to_list(rows))

@app.post("/api/transactions")
def add_transaction():
    data = request.get_json(force=True)
    txn_date = (data.get("txn_date") or "").strip()
    description = (data.get("description") or "").strip()
    txn_type = (data.get("type") or "expense").strip()
    try:
        amount = abs(float(data.get("amount")))
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400
    if not txn_date:
        return jsonify({"error": "date is required"}), 400

    category_id = data.get("category_id") or categorize(description)

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO transactions (user_id, txn_date, description, amount, type, category_id) "
        "VALUES (1, ?, ?, ?, ?, ?)",
        (txn_date, description, amount, txn_type, category_id),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"id": new_id}), 201

@app.delete("/api/transactions/<int:txn_id>")
def delete_transaction(txn_id):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": txn_id})


# ---------- summary card ----------
@app.get("/api/summary")
def summary():
    month = resolve_month()
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END),0) AS income, "
        "       COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),0) AS expense "
        "FROM transactions WHERE strftime('%Y-%m', txn_date) = ?", (month,)).fetchone()
    conn.close()
    income, expense = round(row["income"], 2), round(row["expense"], 2)
    return jsonify({"month": month, "income": income, "expense": expense,
                    "net": round(income - expense, 2)})


# ---------- spending by category (pie) ----------
@app.get("/api/by-category")
def by_category():
    month = resolve_month()
    conn = get_db()
    rows = conn.execute(
        "SELECT COALESCE(c.name, 'Other') AS category, ROUND(SUM(t.amount), 2) AS total "
        "FROM transactions t LEFT JOIN categories c ON c.id = t.category_id "
        "WHERE t.type = 'expense' AND strftime('%Y-%m', t.txn_date) = ? "
        "GROUP BY category ORDER BY total DESC", (month,)).fetchall()
    conn.close()
    return jsonify(rows_to_list(rows))


# ---------- monthly trend (line) ----------
@app.get("/api/trend")
def trend():
    conn = get_db()
    rows = conn.execute(
        "SELECT strftime('%Y-%m', txn_date) AS month, "
        "ROUND(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END),2) AS income, "
        "ROUND(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),2) AS expense "
        "FROM transactions GROUP BY month ORDER BY month").fetchall()
    conn.close()
    return jsonify([{"month": r["month"], "income": r["income"], "expense": r["expense"],
                     "net": round(r["income"] - r["expense"], 2)} for r in rows])


# ---------- insights ----------
def category_totals(conn, month):
    rows = conn.execute(
        "SELECT COALESCE(c.name,'Other') AS category, SUM(t.amount) AS total "
        "FROM transactions t LEFT JOIN categories c ON c.id = t.category_id "
        "WHERE t.type='expense' AND strftime('%Y-%m', t.txn_date) = ? GROUP BY category",
        (month,)).fetchall()
    return {r["category"]: r["total"] for r in rows}

@app.get("/api/insights")
def insights():
    month = resolve_month()
    prev = previous_month(month)
    conn = get_db()
    this_month = category_totals(conn, month)
    last_month = category_totals(conn, prev)
    items = []

    s = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END),0) AS income, "
        "       COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),0) AS expense "
        "FROM transactions WHERE strftime('%Y-%m', txn_date) = ?", (month,)).fetchone()
    net = round(s["income"] - s["expense"], 2)
    items.append(f"You saved ${net:.2f} this month. Nice work!" if net >= 0
                 else f"You spent ${abs(net):.2f} more than you earned this month.")

    if this_month:
        top = max(this_month, key=this_month.get)
        items.append(f"Your biggest expense category was {top} (${this_month[top]:.2f}).")

    biggest = None
    for cat, total in this_month.items():
        prev_total = last_month.get(cat, 0)
        if prev_total > 0:
            change = (total - prev_total) / prev_total * 100
            if biggest is None or change > biggest[1]:
                biggest = (cat, change)
    if biggest and biggest[1] >= 15:
        items.append(f"You spent {biggest[1]:.0f}% more on {biggest[0]} than last month.")

    for b in conn.execute(
            "SELECT c.name AS category, b.monthly_limit AS limit_amt "
            "FROM budgets b JOIN categories c ON c.id = b.category_id WHERE b.user_id = 1").fetchall():
        spent = this_month.get(b["category"], 0)
        if spent > b["limit_amt"]:
            items.append(f"Over budget on {b['category']}: ${spent:.2f} of ${b['limit_amt']:.2f} limit.")

    conn.close()
    return jsonify({"month": month, "items": items})


# ---------- CSV import ----------
def normalize_date(text):
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text

@app.post("/api/import")
def import_csv():
    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file selected"}), 400

    stream = io.StringIO(request.files["file"].stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    imported, errors = 0, []
    conn = get_db()
    row_num = 1
    for row in reader:
        row_num += 1
        try:
            date = (row.get("date") or "").strip()
            description = (row.get("description") or "").strip()
            raw_amount = (row.get("amount") or "").strip()
            if not date or raw_amount == "":
                errors.append(f"Row {row_num}: missing date or amount")
                continue
            value = float(raw_amount)
            txn_type = "expense" if value < 0 else "income"   # bank style: negative = money out
            conn.execute(
                "INSERT INTO transactions (user_id, txn_date, description, amount, type, category_id) "
                "VALUES (1, ?, ?, ?, ?, ?)",
                (normalize_date(date), description, abs(value), txn_type, categorize(description)))
            imported += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {e}")
    conn.commit()
    conn.close()
    return jsonify({"imported": imported, "errors": errors})


if __name__ == "__main__":
    app.run(port=5000, debug=True)