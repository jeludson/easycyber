import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import urllib.parse
import psycopg2

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # in production restrict origins for safety

# ---------- Database helper ----------
DATABASE_URL = os.environ.get("DATABASE_URL")  # Render will provide this (Postgres)
LOCAL_DB = "database.db"

def init_sqlite():
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      email TEXT,
                      message TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )''')
    conn.commit()
    conn.close()

def save_message_sqlite(name, email, message):
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

def save_message_postgres(name, email, message):
    # psycopg2 accepts a DATABASE_URL string
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
    conn.commit()
    cur.close()
    conn.close()

# Initialize local DB on start (if using sqlite)
if not DATABASE_URL:
    init_sqlite()

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET'])
def contact_get():
    return render_template('contact.html')

# API endpoint for POST (AJAX from frontend)
@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or request.form
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400

    try:
        if DATABASE_URL:
            save_message_postgres(name, email, message)
        else:
            save_message_sqlite(name, email, message)
        return jsonify({'success': True, 'message': 'Saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# simple health check
@app.route('/health')
def health():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    # dev mode: load .env if present
    from dotenv import load_dotenv
    load_dotenv()
    app.run(host='0.0.0.0', port=5000, debug=True)
