from flask import Flask, make_response, jsonify, render_template
from werkzeug.utils import redirect
from data.models import User
from data.forms import RegisterForm
from data import db_session
from data import search

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Registration', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Registration', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('registration.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/example.db")
    app.run()


if __name__ == '__main__':
    main()
