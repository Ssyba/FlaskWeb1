from flask import Flask, render_template, flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt
import os

# import forms
from myforms import UserForm, ArticleForm, EditForm
# import my validators
from myvalidators import is_logged_in, is_admin
# import my table pas
from table_maps import Users, Articles
# import the db instance
from table_maps import db

app = Flask(__name__)

app.config.from_pyfile(os.environ['app'])

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


# Register Get
@app.route('/register', methods=['GET'])
def register_get():
    form = UserForm(request.form)
    return render_template('register.html', form=form)


# Register Post
@app.route('/register', methods=['POST'])
def register_post():
    form = UserForm(request.form)
    if Users.query.filter_by(username=form.username.data).first() is None:
        candidate = Users(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=sha256_crypt.encrypt(str(form.password.data))
        )
        db.session.add(candidate)
        db.session.commit()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    else:
        flash('Username already taken', 'danger')
        return render_template('register.html', form=form)


# Login Get
@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')


# Login Post
@app.route('/login', methods=['Post'])
def login_post():
    candidate = Users.query.filter_by(username=request.form['username']).first()

    if (sha256_crypt.verify(request.form['password'], candidate.password)) and (candidate is not None):
        session['logged_in'] = True
        session['username'] = candidate.username
        session['admin'] = candidate.admin
        session['u_id'] = candidate.id

        flash('You are now logged in', 'success')

        return redirect(url_for('dashboard'))
    else:
        error = 'Invalid username or password'
        return render_template('login.html', error=error)


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
    return redirect(url_for('login_get'))


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


# Edit user Get
@app.route('/edit_user/<string:username>', methods=['GET'])
@is_logged_in
@is_admin
def edit_user_get(username):
    e_user = Users.query.filter_by(username=username).first()

    form = EditForm(request.form)

    form.name.data = e_user.name
    form.email.data = e_user.email
    form.username.data = e_user.username

    return render_template('edit_user.html', form=form)


# Edit user Post
@app.route('/edit_user/<string:username>', methods=['POST'])
@is_logged_in
@is_admin
def edit_user_post(username):
    e_user = Users.query.filter_by(username=username).first()

    form = EditForm(request.form)

    e_user.name = form.name.data
    e_user.email = form.email.data
    e_user.username = form.username.data

    db.session.commit()

    flash('User Updated', 'success')

    return redirect(url_for('list_db'))


# u_data Get
@app.route('/u_data/<string:username>', methods=['GET'])
@is_logged_in
def u_data_get(username):
    # Get user by id
    e_user = Users.query.filter_by(username=username).first()

    # Get form
    form = UserForm(request.form)

    # Populate user form fields
    form.name.data = e_user.name
    form.email.data = e_user.email
    form.username.data = e_user.username
    form.password.data = e_user.password

    return render_template('u_data.html', form=form)


# u_data Post
@app.route('/u_data/<string:username>', methods=['POST'])
@is_logged_in
def u_data_post(username):
    # Get user by id
    e_user = Users.query.filter_by(username=username).first()

    # Get form
    form = UserForm(request.form)

    e_user.name = form.name.data
    e_user.email = form.email.data
    e_user.username = form.username.data
    e_user.password = sha256_crypt.encrypt(str(form.password.data))

    db.session.commit()

    flash('User Updated', 'success')

    return redirect(url_for('u_data_get', username=username))


# Add Article Get
@app.route('/add_article', methods=['GET'])
@is_logged_in
def add_article_get():
    form = ArticleForm(request.form)

    return render_template('add_article.html', form=form)


# Add Article Get
@app.route('/add_article', methods=['POST'])
@is_logged_in
def add_article_post():
    form = ArticleForm(request.form)

    if form.validate():
        if form.p_checked.data:
            a_article = Articles(title=form.title.data, body=form.body.data, author=session['username'],
                                 state='private')
        else:
            a_article = Articles(title=form.title.data, body=form.body.data, author=session['username'],
                                 state='public')
        db.session.add(a_article)
        db.session.commit()

    flash('Article Created', 'success')

    return redirect(url_for('dashboard'))


# Delete Article
@app.route('/delete_article/<string:a_id>', methods=['POST'])
@is_logged_in
def delete_article(a_id):
    d_article = Articles.query.filter_by(id=a_id).first()
    db.session.delete(d_article)
    db.session.commit()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


# Edit Article Get
@app.route('/edit_article/<string:a_id>', methods=['GET'])
@is_logged_in
def edit_article_get(a_id):
    e_article = Articles.query.filter_by(id=a_id).first()

    # Get form
    form = ArticleForm(request.form)

    form.title.data = e_article.title
    form.body.data = e_article.body

    return render_template('edit_article.html', form=form)


# Edit Article Post
@app.route('/edit_article/<string:a_id>', methods=['POST'])
@is_logged_in
def edit_article_post(a_id):
    e_article = Articles.query.filter_by(id=a_id).first()

    # Get form
    form = ArticleForm(request.form)

    if form.validate():
        e_article.title = request.form['title']
        e_article.body = request.form['body']

        if session['admin'] == 1:
            if form.a_approve.data:
                e_article.approval = 'approved'
            else:
                e_article.approval = 'rejected'

        flash('Article Updated', 'success')
        db.session.commit()
        return redirect(url_for('dashboard'))


# Single Article
@app.route('/article/<string:a_id>/')
def article(a_id):
    article1 = Articles.query.filter_by(id=a_id).first()

    return render_template('article.html', article=article1)


if __name__ == '__main__':
    app.run(debug=True)
