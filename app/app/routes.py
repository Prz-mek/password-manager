from operator import xor
from flask import render_template, flash, redirect, url_for, request, make_response
from app.forms import RegistarionFrom, LoginFrom, NewPasswordForm
from app import app, db, bcrypt
from app.db_models import User, SavedPassword, SecretPart
from flask_login import login_user, current_user, logout_user, login_required
from app.pass_crypt import encrypt, decrypt, prepare_password, break_secret, bind_secret


def login_response(name, value, location, max_age=None):
    response = make_response('', 303)
    response.headers['Location'] = location
    response.set_cookie(name, value, max_age, httponly=True, secure=True, samesite='Strict')
    return response

def logout_response(name, location):
    response = make_response('', 303)
    response.headers['Location'] = location
    response.set_cookie(name, '', expires=0)
    return response

def get_cookie(name):
    cookies = request.cookies
    if name in cookies:
        return cookies.get(name)
    else:
        return None

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistarionFrom()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created {form.username.data}.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=False)

            password = prepare_password(form.password.data)
            l1, l2 = break_secret(password)
            part = SecretPart(secret=l1, user=current_user)
            db.session.add(part)
            db.session.commit()
            next_page = request.args.get('next')
            next_page = next_page if next_page else url_for('home')
            response = login_response('hello', l2, next_page)
            return response
        else:
            flash('Check login or password', 'error')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    user=current_user
    part = SecretPart.query.filter_by(user=user).first()
    if part:
        db.session.delete(part)
        db.session.commit()
    logout_user()
    return logout_response('hello', url_for('home'))


@app.route('/savedpasswords')
@login_required
def saved_passwords():
    saved_passwords = SavedPassword.query.filter_by(user=current_user).all()
    return render_template('saved_passwords.html', saved_passwords=saved_passwords)

@app.route('/getpassword/<int:password_id>')
@login_required
def get_password(password_id):
    l2 = get_cookie('hello')
    if l2 is None:
         return redirect(url_for('logout'))
    l1 = SecretPart.query.filter_by(user=current_user).first().secret
    key = bind_secret(l1, l2)
    crypt_password = SavedPassword.query.filter_by(id=password_id, user=current_user).first()
    if crypt_password is None:
        flash('You have no access.', 'error')
        return f'{"{"}"password": ""{"}"}'
    password = decrypt(key, crypt_password.password.encode('utf-8'), crypt_password.iv).decode('utf-8')
    return f'{"{"}"password": "{password}"{"}"}'

@app.route('/savedpasswords/new', methods=['GET', 'POST'])
@login_required
def new_password():
    form = NewPasswordForm()
    if form.validate_on_submit():
        l2 = get_cookie('hello').encode('utf-8')
        if l2 is None:
            return redirect(url_for('logout'))
        l1 = SecretPart.query.filter_by(user=current_user).first().secret
        if l1 is None:
            return redirect(url_for('logout'))
        key = bind_secret(l1, l2) # .decode('utf-8')
        password, iv = encrypt(key, form.password.data.encode('utf-8'))
        password_to_save = SavedPassword(site_name=form.site_name.data, password=password, iv=iv, user=current_user)
        db.session.add(password_to_save)
        db.session.commit()
        flash('New password has been added.', 'success')
        return redirect(url_for('saved_passwords'))
    return render_template('new_password.html', form=form)