import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase


class BaseModelForAdminAndUser(UserMixin, SerializerMixin, SqlAlchemyBase):
    __abstract__ = True

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class User(BaseModelForAdminAndUser):

    __tablename__ = 'users'


class Administrator(BaseModelForAdminAndUser):

    __tablename__ = 'administrators'

    #id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('all_items.administrator_id'), unique=True,
                           #primary_key=True, autoincrement=True)
    store_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    store_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    #resources = orm.relationship('all_items', back_populates='administrator')


class Resources(SqlAlchemyBase, SerializerMixin):

    __tablename__ = 'all_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # id товара
    appellation = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)  # наименование товара
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # категория товара (например, молоко)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # цена товара
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # количество товара
    in_store = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # магазин, где находится товар
    store_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # адрес товара
    #administrator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("administrators.id"), nullable=True)
    created_datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    #administrator = orm.relationship('Administrator', back_populates='resources')