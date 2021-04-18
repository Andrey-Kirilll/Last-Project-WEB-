from flask import Flask, make_response, jsonify, render_template
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect
from data.models import User, Administrator
from data.forms import RegistrationForm, LoginForm, AddWork, RadioForm
from data import db_session
from data import search

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/profile', methods=['GET', 'POST'])
def on_profile():
    db_sess = db_session.create_session()
    try:
        user_info = db_sess.query(User).get(current_user.id)
        print(user_info.name)
    except Exception:
        user_info = None
        admin_info = db_sess.query(Administrator).get(current_user.id)
    if user_info is not None:
        return render_template('lets see user profile.html', user=user_info)
    else:
        return render_template('', admin=admin_info)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    sp = {'Аптека': ['Будь здоров!', 'Аптека-А'],  # список наименований конкретных организаций данного типа
          'Продуктовый': ['Пятёрочка', 'Магнит']}
    organs = ['Аптека', 'Продуктовый']
    names_of_organs = sp[organs[0]]  # Названия выбранного типа организации
    address = 'Псков ПТЛ'
    search.main(organs[0], address)  # Путь до изображения карты НЕ УБИРАТЬ ВЫЗОВ ФУНКЦИИ!!!
    params = {
        'organs': organs,
        'address': address,
        'names_of_organs': names_of_organs
    }
    return render_template('content.html', **params)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RadioForm()
    if form.validate_on_submit():
        if form.type.data == '1':
            return redirect('/user_registration')
        else:
            return redirect('/admin_registration')
    return render_template('radio.html', title='Who are you?', form=form)


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('user_registration.html', title='Registration', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('user_registration.html', title='Registration', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('user_registration.html', title='Регистрация', form=form)


@app.route('/admin_registration', methods=['GET', 'POST'])
def admin_registration():
    form = AddWork()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('admin_registration.html', title='Registration', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(Administrator).filter(Administrator.email == form.email.data).first():
            return render_template('admin_registration.html', title='Registration', form=form,
                                   message="This admin already exists")
        admin = Administrator(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            store_name=form.business.data[0],
            store_address=','.join([form.city.data, form.street.data, str(form.house.data)])
        )
        admin.set_password(form.password.data)
        db_sess.add(admin)
        db_sess.commit()
        return redirect('/login')
    return render_template('admin_registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        admin = db_sess.query(Administrator).filter(Administrator.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        elif admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


def main():
    db_session.global_init("db/search_system.db")
    app.run()


if __name__ == '__main__':
    main()
