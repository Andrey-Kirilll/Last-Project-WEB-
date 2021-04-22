import datetime
from flask import Flask, make_response, jsonify, render_template, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect
from data.models import People, Works, Resources
from data.forms import RegistrationForm, LoginForm, AddWork, RadioForm, UserProfileForm, AdminProfileForm, \
    ChangePasswordForm, ButtonsForm, ItemForm
from werkzeug.security import generate_password_hash
from data import db_session
from data import search

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

id_ = 0


@login_manager.user_loader
def load_user(user_email):
    db_sess = db_session.create_session()
    return db_sess.query(People).get(user_email)


@app.route('/profile', methods=['GET', 'POST', 'DELETE'])
def on_profile():
    db_sess = db_session.create_session()
    info = db_sess.query(People).filter_by(email=current_user.email)
    info = [x.serialize for x in info.all()][0]
    if info['role'] == 'User':
        form = UserProfileForm()

        if form.validate_on_submit():
            if 'save' in [i for i in request.form]:
                db_sess.query(People).filter(People.email == current_user.email).update({"email": form.email.data,
                                                                                         "surname": form.surname.data,
                                                                                         "name": form.name.data})
                db_sess.commit()
                return redirect('/')
            else:
                db_sess.query(People).filter(People.email == current_user.email).delete()
                db_sess.commit()
                return redirect('/')
        form.email.data = info['email']
        form.surname.data = info['surname']
        form.name.data = info['name']
        return render_template('lets see user profile.html', form=form, title='Редактирование профиля')
    else:
        form = AdminProfileForm()

        if form.validate_on_submit():
            if 'save' in [i for i in request.form]:
                db_sess.query(People).filter(People.email == current_user.email).update(
                    {"email": form.email.data,
                     "surname": form.surname.data,
                     "name": form.name.data})
                db_sess.query(Works).filter(Works.id == current_user.id).update({
                    "store_name": request.form.get('business'),
                    "store_address": ','.join([form.city.data, form.street.data, str(form.house.data).split('.')[0]])})
                db_sess.commit()
                return redirect('/')
            else:
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

        return render_template('lets see admin profile.html', form=form, title='Редактирование профиля',
                               buss=work['store_name'])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
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


@app.route('/table')
def load_table():
    store1 = {'name': 'Пятёрочка', 'address': 'Псков, Рокоссовского, 32',
              'items': [['напитки', ['Coca-Cola', '120', '86'], ['Pepsi', '98', '34'], ['Ряженка', '45', '23']],
                        ['выпечка', ['Хлеб Бородино', '39', '15'], ['Ватрушка', '42', '40'],
                         ['Булка сдобная', '26', '7'], ['Багет французский', '64', '3']]]}
    store2 = {'name': 'Пятёрочка', 'address': 'Псков, Рокоссовского, 15',
              'items': [['напитки', ['Coca-Cola', '120', '86'], ['Pepsi', '98', '34'], ['Ряженка', '45', '23']],
                        ['выпечка', ['Хлеб Бородино', '39', '15'], ['Ватрушка', '42', '40'],
                         ['Булка сдобная', '26', '7'], ['Багет французский', '64', '3']]]}
    stores = [store1, store2]

    sp = {'Аптека': ['Будь здоров!', 'Аптека-А'],  # список наименований конкретных организаций данного типа
          'Продуктовый': ['Пятёрочка', 'Магнит']}
    organs = ['Аптека', 'Продуктовый']
    names_of_organs = sp[organs[0]]  # Названия выбранного типа организации
    address = 'Псков ПТЛ'
    search.main(organs[0], address)  # Путь до изображения карты НЕ УБИРАТЬ ВЫЗОВ ФУНКЦИИ!!!
    params = {
        'organs': organs,
        'address': address,
        'names_of_organs': names_of_organs,
        "stores": stores
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
        return redirect('/')
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
            store_name=request.form.get('business'),
            store_address=','.join([form.city.data, form.street.data, str(form.house.data).split('.')[0]])
        )
        db_sess.add(work)
        db_sess.commit()

        return redirect('/')
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
        db_sess.query(People).filter(People.email == current_user.email). \
            update({'hashed_password': generate_password_hash(form.new_password.data)})
        db_sess.commit()
        return redirect('/')
    return render_template('change_password.html', title='Смена пароля', form=form)


@app.route('/items', methods=['GET', 'POST', 'DELETE'])
def show_items():
    sort_by = 'Отсортировать по id'
    db_sess = db_session.create_session()
    work_info = db_sess.query(Works.store_name, Works.store_address).filter(Works.id == current_user.id).all()
    form = ButtonsForm()
    st_me = work_info[0][0]
    st_ad = work_info[0][1]
    info = db_sess.query(Resources).filter(Resources.store_address == st_ad, Resources.store == st_me)
    info = [x.serialize for x in info.all()]
    if form.validate_on_submit():
        if 'add_btn' in [i for i in request.form]:
            return redirect('/add_item')
        elif 'dlt_btn' in [i for i in request.form]:
            global id_
            id_ = form.id_field.data
            resource = db_sess.query(Resources.id).filter_by(id=id_).all()
            if resource:
                db_sess.query(Resources).filter_by(id=id_).delete()
                db_sess.commit()
                return redirect('/items')
            else:
                return render_template('items.html', title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}',
                                       info=info, count=len(info), form=form, message='Товара с таким ID не существует',
                                       sort=sort_by)
        elif 'ed_btn' in [i for i in request.form]:
            id_ = form.id_field.data
            resource = db_sess.query(Resources.id).filter_by(id=id_).all()
            if resource:
                return redirect('/edit_item')
            else:
                return render_template('items.html', title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}',
                                       info=info, count=len(info), form=form, message='Товара с таким ID не существует',
                                       sort=sort_by)
        else:
            info = db_sess.query(Resources).filter(Resources.store_address == st_ad, Resources.store == st_me)
            sort_by = request.form.get('sort')
            if sort_by == 'Отсортировать по id':
                info = sorted([x.serialize for x in info.all()], key=lambda x: x['id'])
            elif sort_by == 'Отсортировать по цене':
                info = sorted([x.serialize for x in info.all()], key=lambda x: x['price'])
            elif sort_by == 'Отсортировать по количеству на складе':
                info = sorted([x.serialize for x in info.all()], key=lambda x: x['count'])
            else:
                info = sorted([x.serialize for x in info.all()], key=lambda x: x['appellation'].lower())
    return render_template('items.html', title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}', info=info,
                           count=len(info), form=form, sort=sort_by)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        work_info = db_sess.query(Works.store_name, Works.store_address).filter(Works.id == current_user.id).all()
        st_me = work_info[0][0]
        st_ad = work_info[0][1]
        resource = Resources(
            appellation=form.appellation.data,
            type=form.type.data,
            price=form.price.data,
            count=form.count.data,
            store=st_me,
            store_address=st_ad
        )
        db_sess.add(resource)
        db_sess.commit()
        return redirect('/items')
    return render_template('item.html', form=form, title='Добавление товара')


@app.route('/edit_item', methods=['GET', 'POST'])
def edit_item():
    form = ItemForm()
    db_sess = db_session.create_session()
    global id_
    if form.validate_on_submit():
        db_sess.query(Resources).filter_by(id=id_).update({'appellation': form.appellation.data, 'type': form.type.data,
                                                           'price': form.price.data, 'count': form.count.data,
                                                           'created_datetime': datetime.datetime.now()})
        db_sess.commit()
        return redirect('/items')
    resource = db_sess.query(Resources).filter_by(id=id_)
    resource = [x.serialize for x in resource.all()][0]
    print(form.appellation.data)
    if all(x is None for x in [form.appellation.data, form.type.data, form.price.data, form.count.data]):
        form.appellation.data = resource['appellation']
        form.type.data = resource['type']
        form.price.data = resource['price']
        form.count.data = resource['count']
    return render_template('item.html', form=form, title='Редактирование товара')


def main():
    db_session.global_init("db/search_system.db")
    app.run()


if __name__ == '__main__':
    main()
