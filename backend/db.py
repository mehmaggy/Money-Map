import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "moneymap.db")

# Each category has comma-separated keywords used to auto-categorize a transaction
# by looking at its description text.
DEFAULT_CATEGORIES = [
    ("Food", "starbucks,mcdonald,restaurant,cafe,coffee,pizza,grocery,groceries,chipotle,doordash,ubereats,whole foods,subway,dunkin"),
    ("Transport", "uber,lyft,shell,chevron,exxon,gas,transit,metro,bus,parking,delta,airline"),
    ("Shopping", "amazon,target,walmart,mall,nike,apple store,best buy,store"),
    ("Entertainment", "netflix,spotify,movie,cinema,steam,hulu,disney,concert,game"),
    ("Bills", "electric,water,internet,comcast,verizon,at&t,rent,insurance,phone,utility"),
    ("Income", "payroll,paycheck,deposit,salary,refund,reimburse"),
    ("Other", ""),
]

DEFAULT_BUDGETS = [("Food", 300.0), ("Shopping", 150.0), ("Entertainment", 80.0)]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # lets us read columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Create tables and seed default data the first time the app runs."""
    conn = get_db()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        conn.executescript(f.read())

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.execute("INSERT INTO users (id, name, email) VALUES (1, 'Demo Student', 'demo@example.com')")

    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        conn.executemany("INSERT INTO categories (name, keywords) VALUES (?, ?)", DEFAULT_CATEGORIES)

    if conn.execute("SELECT COUNT(*) FROM budgets").fetchone()[0] == 0:
        for cat_name, limit in DEFAULT_BUDGETS:
            row = conn.execute("SELECT id FROM categories WHERE name = ?", (cat_name,)).fetchone()
            if row:
                conn.execute("INSERT INTO budgets (user_id, category_id, monthly_limit) VALUES (1, ?, ?)",
                                (row["id"], limit))

    conn.commit()
    conn.close()

def categorize(description):
    """Pick a category id by matching keywords against the description text."""
    conn = get_db()
    rows = conn.execute("SELECT id, name, keywords FROM categories").fetchall()
    conn.close()

    other_id = None
    text = (description or "").lower()
    for row in rows:
        if row["name"] == "Other":
            other_id = row["id"]
        if not row["keywords"]:
            continue
        for kw in row["keywords"].split(","):
            kw = kw.strip()
            if kw and kw in text:
                return row["id"]
    return other_id
            