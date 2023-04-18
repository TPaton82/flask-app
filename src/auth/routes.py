from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from src import db
from src.auth import bp
from src.auth.forms import LoginForm, RegistrationForm
from src.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        this_user = User.query.filter_by(username=form.username.data).first()

        if this_user is None or not this_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(this_user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        this_user = User(username=form.username.data, email=form.email.data)
        this_user.set_password(form.password.data)
        db.session.add(this_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/user/<username>')
@login_required
def user(username):
    this_user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': this_user, 'body': 'Test post #1'},
        {'author': this_user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=this_user, posts=posts)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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
