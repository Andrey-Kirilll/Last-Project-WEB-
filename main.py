import datetime
from flask_restful import abort
from flask import Flask, make_response, jsonify, render_template, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect
from data.models import People, Works, Resources
from data.forms import RegistrationForm, LoginForm, AddWork, RadioForm, UserProfileForm, AdminProfileForm, \
    ChangePasswordForm, ButtonsForm, ItemForm, SearchForm
from werkzeug.security import generate_password_hash
from data import db_session, search, api
from data.stores import form_basket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["JSON_AS_ASCII"] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

login_manager = LoginManager()
login_manager.init_app(app)

id_ = 0


@login_manager.user_loader  # функция загрузки авторизованного пользователя
def load_user(user_email):
    db_sess = db_session.create_session()
    return db_sess.query(People).get(user_email)


@app.errorhandler(404)  # перехват ошибки о ненайденной странице
def not_found(_):
    return make_response(jsonify({'error': 'Страничка не найдена'}), 404)


@app.errorhandler(403)  # перехват ошибки о недостаточности полномочий
def no_access(_):
    return make_response(jsonify({'error': 'У вас нет прав доступа к этой странице'}))


@app.errorhandler(401)
def unauthorized(_):
    return make_response(jsonify({'error': 'Вы не авторизованы'}))


@app.route('/logout')  # выход из аккаунта
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])  # главная страница
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

        equalities = {'Аптека': ['Будь здоров!', 'Аптека-А'],  # список наименований конкретных организаций данного типа
                      'Продуктовый': ['Пятёрочка', 'Магнит']}
        organs = ['Аптека', 'Продуктовый']
        address = ' '.join([city, street, house])
        orgs_addresses = search.main(store, address, int(number))  # список адресов
        stores = form_basket(orgs_addresses)  # Создаём таблицу товаров магазинов согласно запросу
        params = {
            'address': address,
            'stores': stores,
            'equalities': equalities
        }

        return render_template('content.html', **params, title=f'{store} в {city} рядом с вами', form=form)

    return render_template('content.html', title=f'Найдите нужную организацию прямо сейчас!', form=form)


@app.route('/table')
@login_required
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


@app.route('/registration', methods=['GET', 'POST'])  # выбор роли для нового аккаунта
def registration():
    form = RadioForm()
    if form.validate_on_submit():  # проверяем нажата ли кнопка
        if form.type.data == '1':  # проверяем радио баттоны - юзер или админ
            return redirect('/user_registration')
        elif form.type.data == '2':
            return redirect('/admin_registration')
    return render_template('radio.html', title='Кто Вы?', form=form)


@app.route('/user_registration', methods=['GET', 'POST'])  # регистрация нового юзер-аккаунта
def user_registration():
    form = RegistrationForm()
    if form.validate_on_submit():  # проверяем нажата ли кнопка
        if form.password.data != form.password_again.data:  # совпадают ли пароли ?
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()  # создаём сессию
        if db_sess.query(People).filter(People.email == form.email.data).first():  # уникален ли логин ?
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже существует")
        user = People(  # собираем объект аккаунта
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            role='User'
        )
        user.set_password(form.password.data)  # устанавливаем пароль, добавляем в таблицу и комиттим
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')  # переводим на главную страничку
    return render_template('user_registration.html', title='Регистрация', form=form)  # рендерим форму регистрации


@app.route('/admin_registration', methods=['GET', 'POST'])  # регистрация для админ-аккаунта
def admin_registration():
    form = AddWork()
    if form.validate_on_submit():  # нажата ли кнопка?
        if form.password.data != form.password_again.data:  # совпадают ли пароли?
            return render_template('admin_registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()  # создаём сессию
        if db_sess.query(People).filter(People.email == form.email.data).first():  # уникален ли логин?
            return render_template('admin_registration.html', title='Регистрация', form=form,
                                   message="К этому адресу уже привязан аккаунт")
        admin = People(  # собираем объект аккаунта
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            role='Admin')
        admin.set_password(form.password.data)
        db_sess.add(admin)  # добавляем в базу и комиттим
        db_sess.commit()
        work = Works(  # привязываем к админу место его работы через айдишник
            id=int(db_sess.query(People.id).filter(People.email == form.email.data).first()[0]),
            store_name=request.form.get('business'),
            store_address=', '.join([form.city.data, form.street.data, form.house.data])
        )
        db_sess.add(work)
        db_sess.commit()

        return redirect('/')  # кидаем на главную страницу
    return render_template('admin_registration.html', title='Регистрация', form=form)  # рендерим форму регистрации


@app.route('/login', methods=['GET', 'POST'])  # вход в аккаунт
def login():
    form = LoginForm()
    if form.validate_on_submit():  # нажата ли кнопка ?
        db_sess = db_session.create_session()
        human = db_sess.query(People).filter(People.email == form.email.data).first()  # ищем аккаунт в дб
        if human and human.check_password(form.password.data):  # есть ли аккаунт и совпадают ли пароли?
            login_user(human, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неверный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)  # рендерим форму регистрации


@app.route('/profile', methods=['GET', 'POST'])  # открыть профиль
@login_required
def on_profile():
    db_sess = db_session.create_session()
    info = db_sess.query(People).filter_by(email=current_user.email)  # ищем в дб информацию о текущем аккаунте
    info = [x.serialize for x in info.all()][0]  # переведом query() запрос в нужный нам вид (список словарей)
    if info['role'] == 'User':  # ты кто - админ или юзер?
        form = UserProfileForm()
        if form.validate_on_submit():  # кнопку нажали?
            if 'save' in [i for i in request.form]:  # это была кнопка сохранить?
                db_sess.query(People).filter(People.email == current_user.email). \
                    update({"email": form.email.data,
                            "surname": form.surname.data,
                            "name": form.name.data})
                db_sess.commit()
                return redirect('/')
            else:  # если это не кнопка сохранить
                db_sess.query(People).filter(People.email == current_user.email).delete()
                db_sess.commit()
                return redirect('/')
        form.email.data = info['email']  # устанавливаем значения полей, предварительно получив их из дб
        form.surname.data = info['surname']
        form.name.data = info['name']
        return render_template('lets see user profile.html', form=form, title='Редактирование профиля')
    else:  # смысл тот же что и выше
        form = AdminProfileForm()
        if form.validate_on_submit():
            if 'save' in [i for i in request.form]:
                db_sess.query(People).filter(People.email == current_user.email).update(
                    {"email": form.email.data,
                     "surname": form.surname.data,
                     "name": form.name.data})
                db_sess.query(Works).filter(Works.id == current_user.id).update({
                    "store_name": request.form.get('business'),
                    "store_address": ', '.join([form.city.data, form.street.data,
                                                form.house.data])})
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
        address = work['store_address'].split(', ')
        form.city.data = address[0]
        form.street.data = address[1]
        form.house.data = address[2]

        return render_template('lets see admin profile.html', form=form, title='Редактирование профиля',
                               buss=work['store_name'])


@app.route('/change_password', methods=['GET', 'POST'])  # меняет пароль на новый для авторизованного аккаунта
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.new_password.data != form.new_password_again.data:  # новые пароли совпадают?
            return render_template('change_password.html', title='Смена пароля', form=form,
                                   message="Пароли не совпадают")
        db_sess.query(People).filter(People.email == current_user.email). \
            update({'hashed_password': generate_password_hash(form.new_password.data)})
        db_sess.commit()  # обновляем данные в дб и коммитим
        return redirect('/')
    return render_template('change_password.html', title='Смена пароля', form=form)


@app.route('/items', methods=['GET', 'POST'])  # показывает админу текущие товары на его месте работы в виде таблички
@login_required
def show_items():
    if current_user.role == 'Admin':
        sort_by = 'Отсортировать по id'  # значение по умолчанию для сортировки
        db_sess = db_session.create_session()
        work_info = db_sess.query(Works.store_name, Works.store_address).filter(Works.id == current_user.id).all()
        form = ButtonsForm()
        st_me = work_info[0][0]  # название магазина
        st_ad = work_info[0][1]  # адрес магазина
        info = db_sess.query(Resources).filter(Resources.store_address == st_ad, Resources.store == st_me)
        info = [x.serialize for x in info.all()]  # получим данные о товарах в удобном виде
        if form.validate_on_submit():
            if 'add_btn' in [i for i in request.form]:  # если нажали кнопку добавить
                return redirect('/add_item')  # то переводим на другую форму
            elif 'dlt_btn' in [i for i in request.form]:  # если нажали кнопку удалить
                global id_
                id_ = form.id_field.data  # достаём id из поля
                resource = db_sess.query(Resources.id).filter_by(id=id_).all()  # ищем товар с нужным id
                if resource:  # если такой товар есть
                    db_sess.query(Resources).filter_by(id=id_).delete()
                    db_sess.commit()  # то удаляем
                    return redirect('/items')
                else:  # в противном случае сообщаем что айдишним инвалидный
                    return render_template('items.html',
                                           title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}',
                                           info=info, count=len(info), form=form,
                                           message='Товара с таким ID не существует',
                                           sort=sort_by)
            elif 'ed_btn' in [i for i in request.form]:  # если нажали кнопку редактирования
                id_ = form.id_field.data
                resource = db_sess.query(Resources.id).filter_by(id=id_).all()
                if resource:  # если такой товар есть
                    return redirect('/edit_item')  # то переводим на другую форму
                else:  # иначе сообщаем об инвалидности айдишника
                    return render_template('items.html',
                                           title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}',
                                           info=info, count=len(info), form=form,
                                           message='Товара с таким ID не существует',
                                           sort=sort_by)
            else:  # похоже была нажата кнопка сортировки
                info = db_sess.query(Resources).filter(Resources.store_address == st_ad, Resources.store == st_me)
                sort_by = request.form.get('sort')  # достаём значение сортировки из формы
                if sort_by == 'Отсортировать по id':
                    info = sorted([x.serialize for x in info.all()], key=lambda x: x['id'])
                elif sort_by == 'Отсортировать по цене':
                    info = sorted([x.serialize for x in info.all()], key=lambda x: x['price'])
                elif sort_by == 'Отсортировать по количеству на складе':
                    info = sorted([x.serialize for x in info.all()], key=lambda x: x['count'])
                else:
                    info = sorted([x.serialize for x in info.all()], key=lambda x: x['appellation'].lower())
        return render_template('items.html', title=f'Список всех товаров в магазине {st_me} по адресу: {st_ad}',
                               info=info,
                               count=len(info), form=form, sort=sort_by)
    abort(403)


@app.route('/add_item', methods=['GET', 'POST'])  # добавить новый товар
@login_required
def add_item():
    if current_user.role == 'Admin':
        form = ItemForm()
        db_sess = db_session.create_session()
        if form.validate_on_submit():  # кнопку нажали?
            work_info = db_sess.query(Works.store_name, Works.store_address).filter(Works.id == current_user.id).all()
            st_me = work_info[0][0]  # нашли информацию об информации и адресе магазина
            st_ad = work_info[0][1]
            resource = Resources(  # собираем объект товара
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
    abort(403)


@app.route('/edit_item', methods=['GET', 'POST'])  # редактирование существующего товара
@login_required
def edit_item():
    if current_user.role == 'Admin':
        form = ItemForm()
        db_sess = db_session.create_session()
        global id_
        if form.validate_on_submit():  # кнопочку-то нажали?
            db_sess.query(Resources).filter_by(id=id_).update(
                {'appellation': form.appellation.data, 'type': form.type.data,
                 'price': form.price.data, 'count': form.count.data,
                 'created_datetime': datetime.datetime.now()})
            db_sess.commit()
            return redirect('/items')
        resource = db_sess.query(Resources).filter_by(id=id_)
        resource = [x.serialize for x in resource.all()][0]
        # проверяем, что заход был первый, чтобы после рендера из-за ошибки не скинулись введенные данные в поля
        if all(x is None for x in [form.appellation.data, form.type.data, form.price.data, form.count.data]):
            form.appellation.data = resource['appellation']
            form.type.data = resource['type']
            form.price.data = resource['price']
            form.count.data = resource['count']
        return render_template('item.html', form=form, title='Редактирование товара')
    abort(403)


if __name__ == '__main__':
    db_session.global_init("db/search_system.db")  # инициилизация дб
    app.register_blueprint(api.blueprint)
    app.run()
