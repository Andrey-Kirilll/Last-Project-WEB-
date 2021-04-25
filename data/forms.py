from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, RadioField, \
    IntegerField, validators, FloatField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RadioForm(FlaskForm):  # класс формы для выбора между юзером, админом или модератором
    type = RadioField('Кто вы?', coerce=str, choices=[('1', 'User'), ('2', 'Administrator')],
                      default='1', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class RegistrationForm(FlaskForm):  # начальная форма регистрации(полная для юзера, каркас для админа)
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class AddWork(RegistrationForm):  # форма для регистрации админов
    business = SelectField('Выберите название организации', validators=[DataRequired()], coerce=str,
                           choices=[('Пятёрочка', 'Пятёрочка'), ('Магнит', 'Магнит'),
                                    ('Будь Здоров', 'Будь Здоров')])
    city = StringField('Введите название города', validators=[DataRequired()])
    street = StringField('Введите название улицы', validators=[DataRequired()])
    house = StringField('Введите номер дома', validators=[DataRequired()])


class LoginForm(FlaskForm):  # форма входа в аккаунт
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Продолжить')


class UserProfileForm(FlaskForm):  # форма для просмота профиля юзера
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    save = SubmitField('Сохранить')
    delete = SubmitField('Удалить аккаунт')


class AdminProfileForm(FlaskForm):  # форма для просмота профиля админа
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    business = SelectField('Выберите тип организации', validators=[DataRequired()], coerce=str,
                           choices=[('Пятёрочка', 'Пятёрочка'), ('Магнит', 'Магнит'),
                                    ('Будь Здоров', 'Будь Здоров')])
    city = StringField('Введите название города', validators=[DataRequired()])
    street = StringField('Введите название улицы', validators=[DataRequired()])
    house = StringField('Введите номер дома', validators=[DataRequired()])
    save = SubmitField('Сохранить')
    delete = SubmitField('Удалить аккаунт')


class ChangePasswordForm(FlaskForm):  # форма для изменения пароля
    new_password = StringField('Введите новый пароль', validators=[DataRequired()])
    new_password_again = StringField('Повторите пароль', validators=[DataRequired()])
    button = SubmitField('Подтвердить')


class SearchForm(FlaskForm):  # форма для поиска магазинов рядом
    # business = SelectField('Тип организации', validators=[DataRequired()], coerce=str,
    #                        choices=[('Продуктовый', 'Продуктовый'), ('Аптека', 'Аптека')])
    store = SelectField('Наименование организации', validators=[DataRequired()], coerce=str,
                        choices=[('Пятёрочка', 'Пятёрочка'), ('Магнит', 'Магнит'),
                                 ('Будь здоров', 'Будь здоров'), ('Аптека-А', 'Аптека-А')])
    city = StringField('Город', validators=[DataRequired()])
    street = StringField('Улица', validators=[DataRequired()])
    house = StringField('Дом', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class ButtonsForm(FlaskForm):   # форма, которая юзается для добавления товара админом
    add_btn = SubmitField('Добавить товар')
    dlt_btn = SubmitField('Удалить товар по id')
    ed_btn = SubmitField('Редактировать товар по id')
    sort = SelectField(validators=[DataRequired()], coerce=str,
                       choices=[('Отсортировать по id', ''), ('Отсортировать по цене', ''),
                                ('Отсортировать по количеству на складе', ''),
                                ('Отсортировать по названию', '')])
    sort_btn = SubmitField('Отсортировать')
    id_field = IntegerField('Введите id товара', [validators.NumberRange(min=0)], default=0)


class ItemForm(FlaskForm):  # форма показа сведений о конкретном товаре либо его добавлении
    appellation = StringField('Название товара', validators=[DataRequired()])
    type = StringField('Тип товара', validators=[DataRequired()])
    price = FloatField('Цена товара', validators=[DataRequired()])
    count = IntegerField('Количество на складе', validators=[DataRequired()])
    save = SubmitField('Сохранить')
