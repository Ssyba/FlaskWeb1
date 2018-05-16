from flask import render_template, flash, session, redirect, url_for, request, Blueprint
from project.users.forms import UserForm, EditForm
from project.models import Users, is_logged_in, is_admin
from passlib.hash import sha256_crypt
from project import db

user_blueprint = Blueprint(
    'users',
    __name__,
    template_folder='templates'
)


# Index
@user_blueprint.route('/', methods=['GET'])
def index():
    return render_template('users/home.html')


# Register Get
@user_blueprint.route('/register', methods=['GET'])
def register_get():
    form = UserForm(request.form)
    return render_template('users/register.html', form=form)


# Register Post
@user_blueprint.route('/register', methods=['POST'])
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
        return redirect(url_for('users.login'))
    else:
        flash('Username already taken', 'danger')
        return render_template('users/register.html', form=form)


# Login Get
@user_blueprint.route('/login', methods=['GET'])
def login_get():
    return render_template('users/login.html')


# Login Post
@user_blueprint.route('/login', methods=['Post'])
def login_post():
    candidate = Users.query.filter_by(username=request.form['username']).first()

    if (sha256_crypt.verify(request.form['password'], candidate.password)) and (candidate is not None):
        session['logged_in'] = True
        session['username'] = candidate.username
        session['admin'] = candidate.admin
        session['u_id'] = candidate.id

        flash('You are now logged in', 'success')

        return redirect(url_for('articles.dashboard'))
    else:
        error = 'Invalid username or password'
        return render_template('users/login.html', error=error)


# Logout
@user_blueprint.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('users.login_get'))


# list_db
@user_blueprint.route('/list_db')
@is_logged_in
@is_admin
def list_db():
    result = Users.query.all()

    if result:
        return render_template('users/list_db.html', users=result)
    else:
        msg = 'No users Found'
        return render_template('users/list_db.html', msg=msg)


# Delete user
@user_blueprint.route('/delete_user/<string:u_id>', methods=['POST'])
@is_logged_in
def delete_user(u_id):
    d_user = Users.query.filter_by(id=u_id).first()
    db.session.delete(d_user)
    db.session.commit()

    flash('User Deleted', 'success')

    return redirect(url_for('users.list_db'))


# Edit user Get
@user_blueprint.route('/edit_user/<string:username>', methods=['GET'])
@is_logged_in
@is_admin
def edit_user_get(username):
    e_user = Users.query.filter_by(username=username).first()

    form = EditForm(request.form)

    form.name.data = e_user.name
    form.email.data = e_user.email
    form.username.data = e_user.username

    return render_template('users/edit_user.html', form=form)


# Edit user Post
@user_blueprint.route('/edit_user/<string:username>', methods=['POST'])
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

    return redirect(url_for('users.list_db'))


# u_data Get
@user_blueprint.route('/u_data/<string:username>', methods=['GET'])
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

    return render_template('users/u_data.html', form=form)


# u_data Post
@user_blueprint.route('/u_data/<string:username>', methods=['POST'])
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

    return redirect(url_for('users.u_data_get', username=username))
