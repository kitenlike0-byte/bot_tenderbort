import sqlite3

DB_NAME = "finance.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # таблица транзакций
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        type TEXT,
        category TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    import sqlite3

DB_NAME = "finance.db"


def add_transaction(user_id, amount, tx_type, category, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, category, description)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, tx_type, category, description))

    conn.commit()
    conn.close()

    conn.commit()
    conn.close()

   def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount, type
        FROM transactions
        WHERE user_id = ?
    """, (user_id,))

    transactions = cursor.fetchall()

    conn.close()

    balance = 0

    for amount, tx_type in transactions:
        if tx_type == "income":
            balance += amount
        else:
            balance -= amount

    return balance

    def get_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # доходы
    cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ? AND type = 'income'
    """, (user_id,))

    income = cursor.fetchone()[0] or 0

    # расходы
    cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
    """, (user_id,))

    expense = cursor.fetchone()[0] or 0

    conn.close()

    balance = income - expense

    return {
        "income": income,
        "expense": expense,
        "balance": balance
    }
    def get_last_transactions(user_id, limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount, type, category
        FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))

    transactions = cursor.fetchall()

    conn.close()

    return transactions

    def get_category_stats(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, (user_id,))

    stats = cursor.fetchall()

    conn.close()

    return stats