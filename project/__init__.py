from flask import Flask, render_template, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_pyfile(os.environ['app'])

# this object instance, "db", will be used for all SQLAlchemy commands
db = SQLAlchemy(app)
db.app = app
db.init_app(app)

from project.users.views import user_blueprint
from project.articles.views import article_blueprint

app.register_blueprint(user_blueprint, url_prefix='/users')
app.register_blueprint(article_blueprint, url_prefix='/articles')


# Index
@app.route('/')
def root():
    return redirect(url_for('users.index'))


# About
@app.route('/about')
def about():
    return render_template('about.html')
