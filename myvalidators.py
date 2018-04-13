from functools import wraps
from flask import flash, redirect, url_for, session


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
    return wrap
