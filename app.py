from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            user = c.fetchone()

        if user:
            return redirect(url_for('index'))
        else:
            error = 'Credenciais inválidas!'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm-password'].strip()

        if password != confirm_password:
            error = 'As senhas não coincidem!'
            return render_template('cadastro.html', error=error)

        try:
            with sqlite3.connect('users.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)', 
                          (name, email, username, password))
                conn.commit()
                return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            error = f'Erro de integridade: {e}'
            return render_template('cadastro.html', error=error)
        except sqlite3.Error as e:
            error = f'Erro ao cadastrar usuário: {e}'
            return render_template('cadastro.html', error=error)

    return render_template('cadastro.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
