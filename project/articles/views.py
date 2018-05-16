from flask import render_template, flash, session, redirect, url_for, request, Blueprint
from project.articles.forms import ArticleForm
from project.models import Articles, is_logged_in
from project import db

article_blueprint = Blueprint(
    'articles',
    __name__,
    template_folder='templates'
)


# Dashboard
@article_blueprint.route('/dashboard')
@is_logged_in
def dashboard():
    # Get articles
    result = Articles.query.all()

    if result:
        return render_template('articles/dashboard.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('articles/dashboard.html', msg=msg)


# Articles
@article_blueprint.route('/')
def articles():
    result = Articles.query.all()

    if result is not None:
        return render_template('articles/articles.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('articles/articles.html', msg=msg)


# Add Article Get
@article_blueprint.route('/add_article', methods=['GET'])
@is_logged_in
def add_article_get():
    form = ArticleForm(request.form)

    return render_template('articles/add_article.html', form=form)


# Add Article Get
@article_blueprint.route('/add_article', methods=['POST'])
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

    return redirect(url_for('articles.dashboard'))


# Delete Article
@article_blueprint.route('/delete_article/<string:a_id>', methods=['POST'])
@is_logged_in
def delete_article(a_id):
    d_article = Articles.query.filter_by(id=a_id).first()
    db.session.delete(d_article)
    db.session.commit()

    flash('Article Deleted', 'success')

    return redirect(url_for('articles.dashboard'))


# Edit Article Get
@article_blueprint.route('/edit_article/<string:a_id>', methods=['GET'])
@is_logged_in
def edit_article_get(a_id):
    e_article = Articles.query.filter_by(id=a_id).first()

    # Get form
    form = ArticleForm(request.form)

    form.title.data = e_article.title
    form.body.data = e_article.body

    return render_template('articles/edit_article.html', form=form)


# Edit Article Post
@article_blueprint.route('/edit_article/<string:a_id>', methods=['POST'])
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
        return redirect(url_for('articles.dashboard'))


# Single Article
@article_blueprint.route('/article/<string:a_id>/')
def article(a_id):
    article1 = Articles.query.filter_by(id=a_id).first()

    return render_template('articles/article.html', article=article1)
