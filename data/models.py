import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class People(UserMixin, SerializerMixin, SqlAlchemyBase):
    __tablename__ = 'people'  # имя таблицы

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, primary_key=True, autoincrement=True)  # id аккаунта
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # фамилия
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # имя
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)  # адрес эл.почты
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # хэшированный пароль
    role = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # роль - админ или юзер
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # дата и время регистрации

    def set_password(self, password):  # функция добавления пароля
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # функция хэширования пароля
        return check_password_hash(self.hashed_password, password)

    @property  # функция со спец.декоратором для удобного представления данных об объекте модели из query() запроса
    def serialize(self):
        return {
            'id': self.id,
            'surname': self.surname,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_date': self.created_date
        }


class Works(SqlAlchemyBase):
    __tablename__ = 'works'  # имя таблицы

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)  # id админа
    store_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # адрес работы
    store_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # название места работы

    @property  # функция со спец.декоратором для удобного представления данных об объекте модели из query() запроса
    def serialize(self):
        return {
            'id': self.id,
            'store_address': self.store_address,
            'store_name': self.store_name
        }


class Resources(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'all_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # id товара
    appellation = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)  # наименование товара
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # категория товара
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # цена товара
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # количество товара
    store = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # магазин, где находится товар
    store_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # адрес магазина
    created_datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # дата и время последнего
    # редактирования

    @property  # функция со спец.декоратором для удобного представления данных об объекте модели из query() запроса
    def serialize(self):
        return {
            'id': self.id,
            'appellation': self.appellation,
            'type': self.type,
            'price': self.price,
            'count': self.count,
            'date': self.created_datetime
        }

    @property  # функция со спец.декоратором для удобного представления данных об объекте модели из query() запроса
    def store_basket(self):
        return {
            'id': self.id,
            'appellation': self.appellation,
            'type': self.type,
            'price': self.price,
            'count': self.count,
            'date': self.created_datetime
        }
