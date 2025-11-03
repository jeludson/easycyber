from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "database.db"

# ---------- Ensure DB & Table Exist ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Call it at startup
init_db()


# ---------- Page Routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# ---------- API Route for Contact Form ----------
@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not (name and email and message):
            return jsonify({'success': False, 'error': 'All fields required'}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        import traceback
        print("❌ ERROR:", traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
