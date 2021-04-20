from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, RadioField, SelectMultipleField, FloatField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Продолжить')


class AddWork(RegistrationForm):
    business = SelectMultipleField('Выберите тип организации', validators=[DataRequired()], coerce=str,
                                   choices=[('Пятёрочка', 'Пятёрочка'), ('Магнит', 'Магнит'),
                                            ('Будь Здоров', 'Будь Здоров')])
    city = StringField('Введите название города', validators=[DataRequired()])
    street = StringField('Введите название улицы', validators=[DataRequired()])
    house = FloatField('Введите номер дома', validators=[DataRequired()])


class RadioForm(FlaskForm):
    type = RadioField('Who are u?', coerce=str, choices=[('1', 'User'), ('2', 'Administrator')], default='1',
                      validators=[DataRequired()])
    submit = SubmitField('Submit')


class Search(FlaskForm):
    city = StringField('Город', validators=[DataRequired()])
    street = StringField('Улица', validators=[DataRequired()])
    house = FloatField('Дом', validators=[DataRequired()])
    submit = SubmitField('Submit')
