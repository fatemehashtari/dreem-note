from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

DATABASE_URL = "postgresql://notes_x32h_user:lkqnuwrhbGaUTq1p00PN44FIngJViDXu@dpg-d0tm7nmmcj7s73dmq740-a.oregon-postgres.render.com/notes_x32h"

# DATABASE_URL = os.environ.get(DATABASE_URL)  # Render اینو می‌سازه




template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"{DATABASE_URL}?sslmode=require"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
print('connceted')


app.secret_key = os.environ.get('SECRET_KEY', 'dreamsecret$$$###@@!!')

# def get_db_path():
#     return os.environ.get('DATABASE_URL', 'notes.db')

def init_db():
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    """))
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            content TEXT,
            category TEXT
        )
    """))
    db.session.commit()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    # with sqlite3.connect(get_db_path()) as conn:
    #     cursor = conn.cursor()
    if search:
        res = db.session.execute(
                text("SELECT * FROM notes WHERE user_id=:user_id AND content LIKE :search"),
                {"user_id": session['user_id'], "search": f"%{search}%"}
            )
    else:
        res = db.session.execute(
                text("SELECT * FROM notes WHERE user_id = :user_id"),
                {"user_id": session['user_id']}
            )
    notes = res.fetchall()
    return render_template('index.html', notes=notes, search=search)

@app.route('/add', methods=['POST'])
def add_note():
    if 'user_id' in session:
        content = request.form['content']
        category = request.form.get('category', 'عمومی')
     
        db.session.execute(

            text("INSERT INTO notes (user_id, content, category) VALUES (:user_id, :content, :category)"),
            {"user_id": session['user_id'], "content": content, "category": category}
        )
        db.session.commit()

        return redirect('/')
    return redirect('/login')

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    # with sqlite3.connect(get_db_path()) as conn:
    #     cursor = conn.cursor()
    if request.method == 'POST':
        content = request.form['content']
        category = request.form.get('category', 'عمومی')
        db.session.execute(
            text("UPDATE notes SET content=:content, category=:category WHERE id=:id AND user_id=:user_id"),
            {"content": content, "category": category, "id": note_id, "user_id": session['user_id']}
        )
        return redirect('/')
    elif request.method == 'GET':
        res = db.session.execute(
        text("SELECT content, category FROM notes WHERE id=:id AND user_id=:user_id"),
        {"id": note_id, "user_id": session['user_id']}
        )
        note = res.fetchone()
    return render_template('edit.html', content=note[0], category=note[1])

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' in session:
        # with sqlite3.connect(get_db_path()) as conn:
        #     cursor = conn.cursor()
            db.session.execute(
                text("DELETE FROM notes WHERE id=:id AND user_id=:user_id"),
                {"id": note_id, "user_id": session['user_id']}
            )
            db.session.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # with sqlite3.connect(get_db_path()) as conn:
        #     cursor = conn.cursor()
        res = db.session.execute(
            text("SELECT id, password FROM users WHERE username=:username"),
            {"username": username}
        )
        user = res.fetchone()
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
        # with sqlite3.connect(get_db_path()) as conn:
        #     cursor = conn.cursor()
        try:
            db.session.execute(
                text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                {"username": username, "password": password}
            )
            db.session.commit()
            # conn.commit()
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
# init_db()
port = int(os.environ.get('PORT', 5000))


if __name__ == '__main__':

    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=port)
