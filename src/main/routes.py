from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from src import db
from src.main import bp
from src.main.forms import EditProfileForm
from src.models import User


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title='Home', posts=posts)


@bp.route('/user/<username>')
@login_required
def user(username):
    this_user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': this_user, 'body': 'Test post #1'},
        {'author': this_user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=this_user, posts=posts)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)
