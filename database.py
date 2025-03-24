import sqlite3
from datetime import datetime

DB_FILE = "donations.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT,
        amount INTEGER NOT NULL,
        method TEXT NOT NULL,
        donation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def add_donation(donation):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    full_name = donation.get("full_name", "").strip() or "—"
    username = donation.get("username", "").strip() or None
    amount = int(donation.get("amount", 0))
    method = donation.get("method", "Unknown")
    donation_time = donation.get("donation_time")
    if donation_time is None:
        donation_time = datetime.now()
    elif isinstance(donation_time, str):
        try:
            donation_time = datetime.strptime(donation_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            donation_time = datetime.now()
    c.execute("""
    INSERT INTO donations (full_name, username, amount, method, donation_time)
    VALUES (?, ?, ?, ?, ?)
    """, (full_name, username, amount, method, donation_time))
    conn.commit()
    conn.close()

def get_summary():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM donations WHERE amount > 0")
    total = c.fetchone()[0] or 0
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    c.execute("""
    SELECT SUM(amount) FROM donations 
    WHERE donation_time >= ? AND amount > 0
    """, (today_start,))
    today_total = c.fetchone()[0] or 0
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    c.execute("""
    SELECT SUM(amount) FROM donations 
    WHERE donation_time >= ? AND amount > 0
    """, (month_start,))
    month_total = c.fetchone()[0] or 0
    c.execute("""
    SELECT full_name, username, SUM(amount) as total 
    FROM donations 
    WHERE amount > 0
    GROUP BY full_name, username 
    ORDER BY total DESC 
    LIMIT 1
    """)
    top_row = c.fetchone()
    top_donor = {
        "full_name": top_row[0] if top_row else "N/A",
        "username": top_row[1] if top_row and top_row[1] else "—",
        "amount": top_row[2] if top_row else 0
    }
    c.execute("""
    SELECT method, SUM(amount), COUNT(*) 
    FROM donations 
    WHERE amount > 0
    GROUP BY method
    """)
    sum_methods = {"Cryptobot": 0, "YooMoney": 0, "Stars": 0}
    count_methods = {"Cryptobot": 0, "YooMoney": 0, "Stars": 0}
    for method, sum_amount, count in c.fetchall():
        if method in sum_methods:
            sum_methods[method] = sum_amount or 0
            count_methods[method] = count or 0
    total_count = sum(count_methods.values())
    most_used = max(count_methods, key=count_methods.get) if total_count > 0 else "N/A"
    conn.close()
    return {
        "total": total,
        "today": today_total,
        "month": month_total,
        "top_donor": top_donor,
        "sum_methods": sum_methods,
        "most_used": most_used,
        "percentages": {m: round((c / total_count * 100), 2) if total_count > 0 else 0 
                       for m, c in count_methods.items()}
    }

def get_donations():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    SELECT full_name, username, amount, method, 
           strftime('%Y-%m-%d %H:%M:%S', donation_time) as donation_time
    FROM donations 
    ORDER BY donation_time DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

init_db()