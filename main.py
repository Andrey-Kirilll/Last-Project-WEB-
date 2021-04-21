from flask import Flask, make_response, jsonify, render_template, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect
from data.models import People, Works
from data.forms import RegistrationForm, LoginForm, AddWork, RadioForm, UserProfileForm, AdminProfileForm,\
    DeleteButton, ChangePasswordForm, SearchForm
from werkzeug.security import generate_password_hash
from data import db_session
from data import search
from data.stores import form_basket


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_email):
    db_sess = db_session.create_session()
    return db_sess.query(People).get(user_email)


@app.route('/profile', methods=['GET', 'POST', 'DELETE'])
def on_profile():
    db_sess = db_session.create_session()
    info = db_sess.query(People).filter_by(email=current_user.email)
    info = [x.serialize for x in info.all()][0]
    form_ = DeleteButton()
    if info['role'] == 'User':
        form = UserProfileForm()

        if form.validate_on_submit():
            db_sess.query(People).filter(People.email == current_user.email).update({"email": form.email.data,
                                                                                     "surname": form.surname.data,
                                                                                     "name": form.name.data})
            db_sess.commit()
            return redirect('/')
        if form_.validate_on_submit():
            db_sess.query(People).filter(People.email == current_user.email).delete()
            db_sess.commit()
            return redirect('/')
        form.email.data = info['email']
        form.surname.data = info['surname']
        form.name.data = info['name']
        return render_template('lets see user profile.html', form=form, form1=form_, title='Редактирование профиля')
    else:
        form = AdminProfileForm()

        if form.validate_on_submit():
            try:
                house = int(form.house.data)
            except ValueError:
                return render_template('lets see admin profile.html', form=form, form1=form_,
                                       title='Редактирование профиля', message='Номер дома должен быть целым числом')
            db_sess.query(People).filter(People.email == current_user.email).update(
                {"email": form.email.data,
                 "surname": form.surname.data,
                 "name": form.name.data})
            db_sess.query(Works).filter(Works.id == current_user.id).update({
                "store_name": form.business.data[0],
                "store_address": ','.join([form.city.data, form.street.data, str(form.house.data).split('.')[0]])})
            db_sess.commit()
            return redirect('/')
        if form_.validate_on_submit():
            db_sess.query(Works).filter(Works.id == current_user.id).delete()
            db_sess.query(People).filter(People.email == current_user.email).delete()
            db_sess.commit()
            return redirect('/')

        work = db_sess.query(Works).filter_by(id=current_user.id)
        work = [x.serialize for x in work.all()][0]
        form.email.data = info['email']
        form.surname.data = info['surname']
        form.name.data = info['name']
        form.business.data = work['store_name']
        address = work['store_address'].split(',')
        form.city.data = address[0]
        form.street.data = address[1]
        form.house.data = address[2]

        return render_template('lets see admin profile.html', form=form, form1=form_, title='Редактирование профиля')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['POST', 'GET'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        city = form.city.data
        street = form.street.data
        house = form.house.data
        business = form.business.data
        store = form.store.data
        number = request.form.get('number')

        print(number)

        # db_sess = db_session.create_session()

        stores = form_basket()  # Создаём таблицу товаров магазинов согласно запросу
        equalities = {'Аптека': ['Будь здоров!', 'Аптека-А'],  # список наименований конкретных организаций данного типа
                      'Продуктовый': ['Пятёрочка', 'Магнит']}
        organs = ['Аптека', 'Продуктовый']
        address = ' '.join([city, street, house])
        search.main(store, address, int(number))  # Путь до изображения карты НЕ УБИРАТЬ ВЫЗОВ ФУНКЦИИ!!!
        params = {
            'address': address,
            'stores': stores,
            'equalities': equalities
        }

        return render_template('content.html', **params, title=f'{store} в {city} рядом с вами', form=form)

    return render_template('content.html', title=f'Найдите нужную организацию прямо сейчас!', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RadioForm()
    if form.validate_on_submit():
        if form.type.data == '1':
            return redirect('/user_registration')
        else:
            return redirect('/admin_registration')
    return render_template('radio.html', title='Кто Вы?', form=form)


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(People).filter(People.email == form.email.data).first():
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже существует")
        user = People(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            role='User'
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
            return render_template('admin_registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(People).filter(People.email == form.email.data).first():
            return render_template('admin_registration.html', title='Регистрация', form=form,
                                   message="К этому адресу уже привязан аккаунт")
        try:
            house = int(form.house.data)
        except ValueError:
            return render_template('admin_registration.html', form=form,
                                   title='Редактирование профиля', message='Номер дома должен быть целым числом')
        admin = People(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            role='Admin')
        admin.set_password(form.password.data)
        db_sess.add(admin)
        db_sess.commit()
        work = Works(
            id=int(db_sess.query(People.id).filter(People.email == form.email.data).first()[0]),
            store_name=form.business.data[0],
            store_address=','.join([form.city.data, form.street.data, str(form.house.data).split('.')[0]])
        )
        db_sess.add(work)
        db_sess.commit()

        return redirect('/login')
    return render_template('admin_registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        human = db_sess.query(People).filter(People.email == form.email.data).first()
        if human and human.check_password(form.password.data):
            login_user(human, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неверный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.new_password.data != form.new_password_again.data:
            return render_template('change_password.html', title='Смена пароля', form=form,
                                   message="Пароли не совпадают")
        db_sess.query(People).filter(People.email == current_user.email).\
            update({'hashed_password': generate_password_hash(form.new_password.data)})
        db_sess.commit()
        return redirect('/')
    return render_template('change_password.html', title='Смена пароля', form=form)


def main():
    db_session.global_init("db/search_system.db")
    app.run()


if __name__ == '__main__':
    main()
