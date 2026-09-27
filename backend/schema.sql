CREATE TABLE IF NOT EXISTS users (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    keywords TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    txn_date TEXT NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    type    TEXT NOT NULL,          -- "income" or "expense"
    category_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS budgets (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL DEFAULT 1,
    category_id     INTEGER NOT NULL,
    monthly_limit     REAL NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);