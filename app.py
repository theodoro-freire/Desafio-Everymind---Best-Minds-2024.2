from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '12345'

def init_db():
    with sqlite3.connect('products.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL
            )
        ''')
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            error = 'As senhas não coincidem!'
            return render_template('cadastro.html', error=error)

        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)',
                      (name, email, username, password))
            conn.commit()

        return redirect(url_for('login'))

    return render_template('cadastro.html')

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
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Credenciais inválidas!'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'add' in request.form:
            nome = request.form['nome']
            codigo = request.form['codigo']
            descricao = request.form['descricao']
            preco = request.form['preco']

            conn = get_db_connection()
            conn.execute('INSERT INTO products (nome, codigo, descricao, preco) VALUES (?, ?, ?, ?)',
                         (nome, codigo, descricao, preco))
            conn.commit()
            conn.close()
            return redirect(url_for('produtos'))

        elif 'edit' in request.form:
            produto_id = request.form['id']
            nome = request.form['nome']
            codigo = request.form['codigo']
            descricao = request.form['descricao']
            preco = request.form['preco']

            conn = get_db_connection()
            conn.execute('UPDATE products SET nome=?, codigo=?, descricao=?, preco=? WHERE id=?',
                         (nome, codigo, descricao, preco, produto_id))
            conn.commit()
            conn.close()
            return redirect(url_for('produtos'))

        elif 'delete' in request.form:
            produto_id = request.form['id']

            conn = get_db_connection()
            conn.execute('DELETE FROM products WHERE id=?', (produto_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('produtos'))

    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/criar', methods=['GET', 'POST'])
def criar_produto():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        codigo = request.form['codigo']
        descricao = request.form['descricao']
        preco = request.form['preco']

        conn = get_db_connection()
        conn.execute('INSERT INTO products (nome, codigo, descricao, preco) VALUES (?, ?, ?, ?)',
                     (nome, codigo, descricao, preco))
        conn.commit()
        conn.close()
        return redirect(url_for('produtos'))

    return render_template('criar_produto.html')

@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        codigo = request.form['codigo']
        descricao = request.form['descricao']
        preco = request.form['preco']

        conn.execute('UPDATE products SET nome = ?, codigo = ?, descricao = ?, preco = ? WHERE id = ?',
                     (nome, codigo, descricao, preco, id))
        conn.commit()
        conn.close()
        return redirect(url_for('produtos'))

    conn.close()
    return render_template('editar_produto.html', product=product)

@app.route('/produtos/deletar/<int:id>')
def deletar_produto(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('produtos'))

if __name__ == '__main__':
    init_db()  
    app.run(debug=True)
