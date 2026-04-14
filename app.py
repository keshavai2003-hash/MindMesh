from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import MySQLdb.cursors
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'itt')

mysql = MySQL(app)

def is_admin():
    return session.get('role') == 'admin'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# GUEST
@app.route('/guest', methods=['GET', 'POST'])
def guest():
    if request.method == 'POST':
        guest_name = request.form.get('guest_name', '').strip()
        if guest_name:
            session['guest_name'] = guest_name
            return redirect('/home')
        return render_template('guest.html', msg="Please enter a name")
    return render_template('guest.html')

# FIX : hashed password, input validation, guest session cleared
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    session.clear()

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # FIX : basic input validation
        if len(name) < 2:
            return render_template('sign_up.html', msg="Name must be at least 2 characters.")
        if len(password) < 6:
            return render_template('sign_up.html', msg="Password must be at least 6 characters.")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            return render_template('sign_up.html', msg="User already exists. Try a different email.")

       
        hashed_pw = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw, 'member')
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('sign_in', success="Account created successfully! Please login."))

    return render_template('sign_up.html', msg='')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        session.clear()  # only clear session when page first loads, not after login
    success = request.args.get('success')

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        cursor = mysql.connection.cursor()
       
        cursor.execute(
            "SELECT id, name, role, password FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[3], password):
            session['user_id']   = user[0]
            session['user_name'] = user[1]
            session['role']      = user[2]
            session.pop('guest_name', None)  # FIX 4: clear guest session
            return redirect('/home')

        return render_template('sign_in.html', msg="Invalid email or password.", success=success)

    return render_template('sign_in.html', msg='', success=success)

# ADMIN LOGIN — separate page with secret word
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    session.clear()

    if request.method == 'POST':
        email       = request.form.get('email', '').strip()
        password    = request.form.get('password', '').strip()
        secret_word = request.form.get('secret_word', '').strip()

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, name, role, password, secret_word FROM users WHERE email=%s AND role='admin'",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[3], password) and user[4] == secret_word:
            session['user_id']   = user[0]
            session['user_name'] = user[1]
            session['role']      = user[2]
            session.pop('guest_name', None)
            return redirect('/home')

        return render_template('admin_login.html', msg="Invalid credentials. All 3 fields must be correct.")

    return render_template('admin_login.html', msg='')

@app.route('/home')
def home():
    guest_name = session.get('guest_name')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.id, p.title,
               u.name AS author,
               c.name AS category
        FROM posts p
        JOIN users u ON p.author_id = u.id
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
    """)
    posts = cursor.fetchall()
    cursor.close()

    return render_template('home.html', guest_name=guest_name, posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT p.id, p.title, p.content,
               u.name AS author,
               c.name AS category,
               (SELECT COUNT(*) FROM likes WHERE post_id=p.id) AS likes,
               (SELECT COUNT(*) FROM dislikes WHERE post_id=p.id) AS dislikes
        FROM posts p
        JOIN users u ON p.author_id = u.id
        JOIN categories c ON p.category_id = c.id
        WHERE p.id=%s
    """, (post_id,))
    post = cursor.fetchone()

    if not post:
        cursor.close()
        return "Post not found", 404

    cursor.execute("""
        SELECT c.id, c.comment, u.name AS author
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id=%s
        ORDER BY c.id DESC
    """, (post_id,))
    comments = cursor.fetchall()
    cursor.close()

    return render_template('post_detail.html', post=post, comments=comments)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('sign_in'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        title        = request.form.get('title', '').strip()
        content      = request.form.get('content', '').strip()
        category     = request.form.get('category')
        new_category = request.form.get('new_category', '').strip()

        
        if len(title) < 3:
            cursor.close()
            return render_template('post_create.html', categories=categories,
                                   msg="Title must be at least 3 characters.")
        if len(content) < 10:
            cursor.close()
            return render_template('post_create.html', categories=categories,
                                   msg="Content must be at least 10 characters.")

        if new_category:
            cursor.execute(
                "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s)",
                (new_category,)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                return render_template('post_create.html', categories=categories,
                                       msg="Category already exists. Please select it from the list.")
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (new_category,))
            mysql.connection.commit()
            category_id = cursor.lastrowid
        else:
            cursor.execute("SELECT id FROM categories WHERE name=%s", (category,))
            cat = cursor.fetchone()
            if not cat:
                cursor.close()
                return render_template('post_create.html', categories=categories,
                                       msg="Please select a valid category.")
            category_id = cat[0]

        cursor.execute(
            "INSERT INTO posts (title, content, author_id, category_id) VALUES (%s, %s, %s, %s)",
            (title, content, session['user_id'], category_id)
        )
        mysql.connection.commit()
        cursor.close()
        return redirect('/home')

    cursor.close()
    return render_template('post_create.html', categories=categories)

# ADMIN
@app.route('/admin/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not is_admin():
        return "Unauthorized", 403

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        cursor.execute(
            "UPDATE posts SET title=%s, content=%s WHERE id=%s",
            (request.form['title'], request.form['content'], post_id)
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('view_post', post_id=post_id))

    cursor.execute("SELECT id, title, content FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    cursor.close()
    return render_template('edit_post.html', post=post)

@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not is_admin():
        return "Unauthorized", 403

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM comments WHERE post_id=%s", (post_id,))
    cursor.execute("DELETE FROM likes WHERE post_id=%s", (post_id,))
    cursor.execute("DELETE FROM dislikes WHERE post_id=%s", (post_id,))
    cursor.execute("DELETE FROM posts WHERE id=%s", (post_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/home')

# FIX 5: safe redirect using post_id instead of request.referrer
@app.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not is_admin():
        return "Unauthorized", 403

    cursor = mysql.connection.cursor()
    # FIX 5: get post_id before deleting so we can redirect properly
    cursor.execute("SELECT post_id FROM comments WHERE id=%s", (comment_id,))
    row = cursor.fetchone()
    cursor.execute("DELETE FROM comments WHERE id=%s", (comment_id,))
    mysql.connection.commit()
    cursor.close()

    if row:
        return redirect(url_for('view_post', post_id=row[0]))
    return redirect('/home')

@app.route('/admin/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if not is_admin():
        return "Unauthorized", 403

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        new_comment = request.form.get('comment', '').strip()
        cursor.execute(
            "UPDATE comments SET comment=%s WHERE id=%s",
            (new_comment, comment_id)
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(request.form.get('redirect_to', '/home'))

    cursor.execute("""
        SELECT c.id, c.comment, c.post_id
        FROM comments c
        WHERE c.id=%s
    """, (comment_id,))
    comment = cursor.fetchone()
    cursor.close()

    if not comment:
        return "Comment not found", 404

    return render_template('edit_comment.html', comment=comment)

# USER
@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect('/home')

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM dislikes WHERE post_id=%s AND user_id=%s", (post_id, session['user_id']))
    cursor.execute("INSERT IGNORE INTO likes (post_id,user_id) VALUES (%s,%s)", (post_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/dislike/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    if 'user_id' not in session:
        return redirect('/home')

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM likes WHERE post_id=%s AND user_id=%s", (post_id, session['user_id']))
    cursor.execute("INSERT IGNORE INTO dislikes (post_id,user_id) VALUES (%s,%s)", (post_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_post', post_id=post_id))

# FIX : validate comment not empty
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        return redirect('/home')

    comment = request.form.get('comment', '').strip()
    if len(comment) < 1:
        return redirect(url_for('view_post', post_id=post_id))

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO comments (post_id,user_id,comment) VALUES (%s,%s,%s)",
        (post_id, session['user_id'], comment)
    )
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_post', post_id=post_id))

# FIX : contact form now has a route
@app.route('/contact', methods=['POST'])
def contact():
    # Future: save to DB or send email
    return redirect(url_for('index', contacted=1))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/index')

# FIX 8: debug mode loaded from .env, defaults to False
if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true')
