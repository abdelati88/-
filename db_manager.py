import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('office_analytics.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs
                 (employee_name TEXT, date TEXT, desk_seconds REAL, focus_seconds REAL,
                 PRIMARY KEY(employee_name, date))''')
    conn.commit()
    conn.close()

def update_db(stats):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('office_analytics.db')
    c = conn.cursor()
    
    for name, data in stats.items():
        c.execute('''INSERT OR REPLACE INTO activity_logs 
                     (employee_name, date, desk_seconds, focus_seconds)
                     VALUES (?, ?, 
                        COALESCE((SELECT desk_seconds FROM activity_logs WHERE employee_name=? AND date=?), 0) + ?,
                        COALESCE((SELECT focus_seconds FROM activity_logs WHERE employee_name=? AND date=?), 0) + ?
                     )''', 
                  (name, today, name, today, data['desk_inc'], name, today, data['focus_inc']))
    
    conn.commit()
    conn.close()