import sqlite3, os
from flask import Flask, request, g, render_template, redirect, url_for, send_from_directory, abort, session
from werkzeug.utils import safe_join
from secure_app.forms import LoginForm, CommentForm
import bleach

APP_DB = 'secure.db'
FILES_DIR = 'secure_app/files'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secure-secret'  # Use env in real apps

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
    db.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1,?,?)", ('alice','password123'))
    db.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2,?,?)", ('bob','password123'))
    db.execute("INSERT OR IGNORE INTO accounts (id, user_id, balance) VALUES (1,1,1000)")
    db.execute("INSERT OR IGNORE INTO accounts (id, user_id, balance) VALUES (2,2,1000)")
    db.commit()

@app.before_first_request
def setup():
    init_db()

@app.after_request
def set_headers(resp):
    resp.headers['Content-Security-Policy'] = "default-src 'self'"
    return resp

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        pwd = form.password.data
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user, pwd))
        row = cur.fetchone()
        if row:
            session['user_id'] = row['id']
            session['username'] = row['username']
            return f"Welcome {row['username']}!"
        return "Login failed"
    return render_template('login.html', form=form)

@app.route('/comments', methods=['GET','POST'])
def comments():
    form = CommentForm()
    db = get_db()
    if form.validate_on_submit():
        username = bleach.clean(form.username.data, strip=True)
        comment = bleach.clean(form.comment.data)
        db.execute("INSERT INTO comments (username, comment) VALUES (?,?)", (username, comment))
        db.commit()
        return redirect(url_for('comments'))
    cur = db.execute("SELECT username, comment FROM comments ORDER BY id DESC LIMIT 20")
    entries = cur.fetchall()
    return render_template('comments.html', entries=entries, form=form)

# SECURE: require resource owner for account
@app.route('/account')
def account():
    if 'user_id' not in session:
        return "Unauthorized", 401
    user_id = session['user_id']
    db = get_db()
    row = db.execute("SELECT a.id, a.balance, u.username FROM accounts a JOIN users u ON a.user_id=u.id WHERE u.id = ?", (user_id,)).fetchone()
    if not row:
        return "Not found", 404
    return f"Account for {row['username']}: balance={row['balance']}"

# SECURE: only allow transfer from own account
@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session:
        return "Unauthorized", 401
    from_user_id = session['user_id']
    to_user_id = request.form.get('to_user_id', type=int)
    amount = request.form.get('amount', type=int)
    if None in (to_user_id, amount):
        return "Missing fields", 400
    db = get_db()
    bal = db.execute("SELECT balance FROM accounts WHERE user_id = ?", (from_user_id,)).fetchone()
    if not bal or bal['balance'] < amount:
        return "Insufficient funds", 400
    db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, from_user_id))
    db.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", (amount, to_user_id))
    db.commit()
    return "Transferred"

@app.route('/download')
def download():
    fname = request.args.get('file','safe.txt')
    safe_path = safe_join(FILES_DIR, fname)
    if safe_path is None or not os.path.isfile(safe_path):
        abort(404)
    return send_from_directory(FILES_DIR, fname, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5002, debug=False)
