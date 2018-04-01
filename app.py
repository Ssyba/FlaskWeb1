from functools import wraps

from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test1234'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# users
@app.route('/users')
def users():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get users
    result = cur.execute("SELECT * FROM users")

    users = cur.fetchall()

    # Close connection
    cur.close()

    if result > 0:
        return render_template('users.html', users=users)
    else:
        msg = 'No users Found'
        return render_template('users.html', msg=msg)


# Single user
@app.route('/user/<string:id>/')
def user(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user
    cur.execute("SELECT * FROM users WHERE id = %s", [id])

    user = cur.fetchone()

    return render_template('user.html', user=user)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    admin = StringField('Admin')


# Edit Form Class
class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password')
    admin = StringField('Admin')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Close connection
            cur.close()

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('listdb'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# listdb
@app.route('/listdb')
@is_logged_in
def listdb():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get users
    result = cur.execute("SELECT * FROM users")

    users = cur.fetchall()

    # Close connection
    cur.close()

    if result > 0:
        return render_template('listdb.html', users=users)
    else:
        msg = 'No users Found'
        return render_template('listdb.html', msg=msg)


# Edit user
@app.route('/edit_user/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_user(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by id
    cur.execute("SELECT * FROM users WHERE id = %s", [id])

    # get the firt user with the id
    user = cur.fetchone()

    # close connection
    cur.close()

    # Get form
    form = EditForm(request.form)

    # Populate user form fields
    form.name.data = user['name']
    form.email.data = user['email']
    form.username.data = user['username']
    form.password.data = user['password']
    form.admin.data = user['admin']

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(name)
        # Execute
        cur.execute("UPDATE users SET name=%s, email=%s, username=%s, password=%s WHERE id=%s",
                    (name, email, username, password, id))
        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('user Updated', 'success')

        return redirect(url_for('listdb'))

    return render_template('edit_user.html', form=form)


# Delete user
@app.route('/delete_user/<string:id>', methods=['POST'])
@is_logged_in
def delete_user(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM users WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('user Deleted', 'success')

    return redirect(url_for('listdb'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
app.run(debug=True)
