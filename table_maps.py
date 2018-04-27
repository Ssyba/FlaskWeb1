from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    email = db.Column('email', db.String(120), unique=True, nullable=False)
    username = db.Column('username', db.String(100), unique=True, nullable=False)
    password = db.Column('password', db.String(100), nullable=False)
    admin = db.Column('admin', db.Boolean)

    def __repr__(self):
        return '<User %r>' % self.username


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('name', db.String(255), nullable=False)
    author = db.Column('author', db.String(100), nullable=False)
    body = db.Column('body', db.Text, nullable=False)
    create_date = db.Column('create_date', db.DateTime, default=db.func.current_timestamp())
    state = db.Column('state', db.String(9), nullable=False)
    approval = db.Column('approval', db.String(9))
