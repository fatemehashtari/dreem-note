from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get('SECRET_KEY', 'dreamsecret$$$###@@!!')

def get_db_path():
    return os.environ.get('DATABASE_URL', 'notes.db')

def init_db():
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            content TEXT,
                            category TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id))""")

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        if search:
            cursor.execute("SELECT * FROM notes WHERE user_id=? AND content LIKE ?", (session['user_id'], f"%{search}%"))
        else:
            cursor.execute("SELECT * FROM notes WHERE user_id=?", (session['user_id'],))
        notes = cursor.fetchall()
    return render_template('index.html', notes=notes, search=search)

@app.route('/add', methods=['POST'])
def add_note():
    if 'user_id' in session:
        content = request.form['content']
        category = request.form.get('category', 'عمومی')
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (user_id, content, category) VALUES (?, ?, ?)", (session['user_id'], content, category))
        return redirect('/')
    return redirect('/login')

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            content = request.form['content']
            category = request.form.get('category', 'عمومی')
            cursor.execute("UPDATE notes SET content=?, category=? WHERE id=? AND user_id=?", (content, category, note_id, session['user_id']))
            return redirect('/')
        elif request.method == 'GET':
            cursor.execute("SELECT content, category FROM notes WHERE id=? AND user_id=?", (note_id, session['user_id']))
            note = cursor.fetchone()
    return render_template('edit.html', content=note[0], category=note[1])

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' in session:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, session['user_id']))
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect('/login')
            except :
                pass


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/test')
def test():
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error: {str(e)}", 500
init_db()
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
