from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from _mysql_exceptions import IntegrityError
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators, IntegerField



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


# Single user
@app.route('/user/<string:u_id>/')
def user(u_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user
    cur.execute("SELECT * FROM users WHERE id = %s", [u_id])

    f_user = cur.fetchone()

    return render_template('user.html', user=f_user)


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
    admin = IntegerField('Admin')


class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    admin = IntegerField('Admin')


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
        try:
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                        (name, email, username, password))

            # Commit to DB
            mysql.connection.commit()
        # else:
        except IntegrityError:
            flash('Sorry , This user is already registered ', 'danger')
            return render_template('register.html', form=form)

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
        username_c = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username_c])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            admin = data['admin']
            u_id = data['id']

            # Close connection
            cur.close()

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username_c
                session['admin'] = admin
                session['u_id'] = u_id

                flash('You are now logged in', 'success')
                return redirect(url_for('list_db'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Check if admin
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['admin'] == 1 and 'logged_in' in session:
            return f(*args, **kwargs)
        elif session['u_id'] is not None:
            return redirect(url_for('u_data', u_id=session['u_id']))
        else:
            flash('id is None,wtf?', 'danger')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# list_db
@app.route('/list_db')
@is_logged_in
@is_admin
def list_db():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get users
    result = cur.execute("SELECT * FROM users")

    f_users = cur.fetchall()

    # Close connection
    cur.close()

    if result > 0:
        return render_template('list_db.html', users=f_users)
    else:
        msg = 'No users Found'
        return render_template('list_db.html', msg=msg)


# u_data
@app.route('/u_data/<string:u_id>', methods=['GET', 'POST'])
@is_logged_in
def u_data(u_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by id
    cur.execute("SELECT * FROM users WHERE id = %s", [u_id])

    # get the first user with the id
    user1 = cur.fetchone()

    # close connection
    cur.close()

    # Get form
    form = RegisterForm(request.form)

    if request.method == 'GET':
        # Populate user form fields
        form.name.data = user1['name']
        form.email.data = user1['email']
        form.username.data = user1['username']
        form.password.data = user1['password']

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("UPDATE users SET name=%s, email=%s, username=%s, password=%s WHERE id=%s",
                    (name, email, username, password, u_id))
        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('User Updated', 'success')

        return redirect(url_for('u_data', u_id=u_id))
    return render_template('u_data.html', form=form)


# Edit users
@app.route('/edit_user/<string:u_id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_user(u_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by id
    cur.execute("SELECT * FROM users WHERE id = %s", [u_id])

    # get the first user with the id
    user1 = cur.fetchone()

    # close connection
    cur.close()

    # Get form
    form = EditForm(request.form)

    if request.method == 'GET':
        # Populate user form fields
        form.name.data = user1['name']
        form.email.data = user1['email']
        form.username.data = user1['username']

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("UPDATE users SET name=%s, email=%s, username=%s WHERE id=%s",
                    (name, email, username, u_id))
        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('User Updated', 'success')

        return redirect(url_for('list_db'))

    return render_template('edit_user.html', form=form)


# Delete user
@app.route('/delete_user/<string:u_id>', methods=['POST'])
@is_logged_in
def delete_user(u_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM users WHERE id = %s", u_id)

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('User Deleted', 'success')

    return redirect(url_for('list_db'))


if __name__ == '__main__':
    app.secret_key = 'secret1234'
    app.run(debug=True)