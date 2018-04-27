from flask import Flask, render_template, flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt

# import forms
from myforms import UserForm, ArticleForm, EditForm
# import my validators
from myvalidators import is_logged_in, is_admin
# impot my table pas
from table_maps import Users, Articles
# import the db instance
from table_maps import db

app = Flask(__name__)

app.config.from_pyfile('app.cfg')

# this object instance, "db", will be used for all SQLAlchemy commands
db.app = app
db.init_app(app)


# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        candidate = Users(name=name, email=email, username=username, password=password)
        query = Users.query.filter_by(username='username_c').first()

        # Execute query
        if query is None:
            db.session.add(candidate)
            db.session.commit()
        # else
        else:
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)

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

        # Get user by username
        candidate = Users.query.filter_by(username=username_c).first()

        if candidate is not None:
            password = candidate.password
            admin = candidate.admin
            u_id = candidate.id

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username_c
                session['admin'] = admin
                session['u_id'] = u_id

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Get articles
    result = Articles.query.all()

    if result:
        return render_template('dashboard.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Articles
@app.route('/articles')
def articles():
    result = Articles.query.all()

    if result is not None:
        return render_template('articles.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)


# list_db
@app.route('/list_db')
@is_logged_in
@is_admin
def list_db():
    result = Users.query.all()

    if result:
        return render_template('list_db.html', users=result)
    else:
        msg = 'No users Found'
        return render_template('list_db.html', msg=msg)


# Delete user
@app.route('/delete_user/<string:u_id>', methods=['POST'])
@is_logged_in
def delete_user(u_id):
    d_user = Users.query.filter_by(id=u_id).first()
    db.session.delete(d_user)
    db.session.commit()

    flash('User Deleted', 'success')

    return redirect(url_for('list_db'))


# Edit user
@app.route('/edit_user/<string:username>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_user(username):
    e_user = Users.query.filter_by(username=username).first()

    # Get form
    form = EditForm(request.form)

    if request.method == 'GET':
        # Populate user form fields
        form.name.data = e_user.name
        form.email.data = e_user.email
        form.username.data = e_user.username

    if request.method == 'POST' and form.validate():
        e_user.name = form.name.data
        e_user.email = form.email.data
        e_user.username = form.username.data

        db.session.commit()

        flash('User Updated', 'success')

        return redirect(url_for('list_db'))

    return render_template('edit_user.html', form=form)


# u_data
@app.route('/u_data/<string:username>', methods=['GET', 'POST'])
@is_logged_in
def u_data(username):
    # Get user by id
    e_user = Users.query.filter_by(username=username).first()

    # Get form
    form = UserForm(request.form)

    if request.method == 'GET':
        # Populate user form fields
        form.name.data = e_user.name
        form.email.data = e_user.email
        form.username.data = e_user.username
        form.password.data = e_user.password

    if request.method == 'POST' and form.validate():
        e_user.name = form.name.data
        e_user.email = form.email.data
        e_user.username = form.username.data
        e_user.password = sha256_crypt.encrypt(str(form.password.data))

        db.session.commit()

        flash('User Updated', 'success')

        return redirect(url_for('u_data', username=username))
    return render_template('u_data.html', form=form)


# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        p_checked = form.p_checked.data

        # Check if private
        if p_checked:
            # Execute for private
            a_article = Articles(title=title, body=body, author=session['username'], state='private')
            db.session.add(a_article)
            db.session.commit()
        else:
            # Execute public
            a_article = Articles(title=title, body=body, author=session['username'], state='public')
            db.session.add(a_article)
            db.session.commit()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


# Delete Article
@app.route('/delete_article/<string:a_id>', methods=['POST'])
@is_logged_in
def delete_article(a_id):
    d_article = Articles.query.filter_by(id=a_id).first()
    db.session.delete(d_article)
    db.session.commit()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


# Edit Article
@app.route('/edit_article/<string:a_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(a_id):
    e_article = Articles.query.filter_by(id=a_id).first()

    # Get form
    form = ArticleForm(request.form)

    if request.method == 'GET':
        # Populate article form fields
        form.title.data = e_article.title
        form.body.data = e_article.body

    if request.method == 'POST' and form.validate():
        e_article.title = request.form['title']
        e_article.body = request.form['body']
        approval = form.a_approve.data

        if session['admin'] == 1:
            if approval:
                e_article.approval = 'approved'
                db.session.commit()

                flash('Article Updated', 'success')

                return redirect(url_for('dashboard'))
            else:
                e_article.approval = 'rejected'
                db.session.commit()

                flash('Article Updated', 'success')

                return redirect(url_for('dashboard'))
        flash('Article Updated', 'success')
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


# Single Article
@app.route('/article/<string:a_id>/')
def article(a_id):
    article1 = Articles.query.filter_by(id=a_id).first()

    return render_template('article.html', article=article1)


if __name__ == '__main__':
    app.run(debug=True)
