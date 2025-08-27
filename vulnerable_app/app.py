import sqlite3
from flask import Flask, request, g, render_template, redirect, url_for, send_from_directory, abort, session

APP_DB = 'vuln.db'
FILES_DIR = 'vulnerable_app/files'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret'

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(APP_DB)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT);
    CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, username TEXT, comment TEXT);
    CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, user_id INTEGER, balance INTEGER);
    """ )
    db.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1,'alice','password123')")
    db.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2,'bob','password123')")
    db.execute("INSERT OR IGNORE INTO accounts (id, user_id, balance) VALUES (1,1,1000)")
    db.execute("INSERT OR IGNORE INTO accounts (id, user_id, balance) VALUES (2,2,1000)")
    db.commit()

@app.before_first_request
def setup():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username','')
        pwd = request.form.get('password','')
        db = get_db()
        query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{pwd}'"
        cur = db.execute(query)
        row = cur.fetchone()
        if row:
            session['user_id'] = row['id']
            session['username'] = row['username']
            return f"Welcome {row['username']}!"
        return "Login failed"
    return render_template('login.html')

@app.route('/comments', methods=['GET','POST'])
def comments():
    db = get_db()
    if request.method == 'POST':
        username = request.form.get('username','anon')
        comment = request.form.get('comment','')
        db.execute("INSERT INTO comments (username, comment) VALUES (?,?)", (username, comment))
        db.commit()
        return redirect(url_for('comments'))
    cur = db.execute("SELECT username, comment FROM comments ORDER BY id DESC LIMIT 20")
    entries = cur.fetchall()
    return render_template('comments.html', entries=entries)


@app.route('/download')
def download():
    fname = request.args.get('file','safe.txt')
    try:
        return send_from_directory(FILES_DIR, fname, as_attachment=True)
    except Exception:
        abort(404)

@app.route('/account')
def account():
    user_id = request.args.get('user_id', type=int, default=None)
    if user_id is None:
        return "Missing user_id", 400
    db = get_db()
    row = db.execute("SELECT a.id, a.balance, u.username FROM accounts a JOIN users u ON a.user_id=u.id WHERE u.id = ?", (user_id,)).fetchone()
    if not row:
        return "Not found", 404
    return f"Account for {row['username']}: balance={row['balance']}"

@app.route('/transfer', methods=['POST'])
def transfer():
    from_user_id = request.form.get('from_user_id', type=int)
    to_user_id = request.form.get('to_user_id', type=int)
    amount = request.form.get('amount', type=int)
    if None in (from_user_id, to_user_id, amount):
        return "Missing fields", 400
    db = get_db()
    db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, from_user_id))
    db.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", (amount, to_user_id))
    db.commit()
    return "Transferred"

if __name__ == '__main__':
    app.run(port=5001, debug=True)
