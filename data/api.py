from flask import jsonify, Blueprint, request
from flask_restful import abort
from . import db_session
from .models import People, Works

blueprint = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/get_all_accounts&login=<string:lg>&token=<string:key>', methods=['GET'])
def get_accounts(lg, key):
    if lg == 'x@a' and key == 'yandex_lyceum_project':
        db_sess = db_session.create_session()
        admins = db_sess.query(People).filter(People.role == 'Admin').all()
        users = db_sess.query(People).filter(People.role == 'User').all()
        return jsonify(
            {'Administrators': [item.to_dict(only=('id', 'email')) for item in admins]},
            {'Users': [item.to_dict(only=('id', 'email')) for item in users]}
        )
    abort(403)


@blueprint.route('/api/get_one_account/<int:acc_id>&login=<string:lg>&token=<string:key>', methods=['GET'])
def get_one_account(acc_id, lg, key):
    if lg == 'x@a' and key == 'yandex_lyceum_project':
        db_sess = db_session.create_session()
        acc = db_sess.query(People).get(acc_id)
        if acc:
            role = db_sess.query(People.role).filter_by(id=acc_id).all()[0][0]
            if 'Admin' == role:
                work = db_sess.query(Works).get(acc_id)
                return jsonify({'Administrator': acc.to_dict(only=('id', 'surname', 'name', 'email', 'created_date'))},
                               {'Work': work.to_dict(only=('store_name', 'store_address'))})
            elif 'User' == role:
                return jsonify({'User': acc.to_dict(only=('id', 'surname', 'name', 'email', 'created_date'))})
        else:
            return jsonify({'error': 'Инвалидный id'})
    abort(403)


@blueprint.route('/api/add_account/<string:role>&login=<string:lg>&token=<string:key>', methods=['POST'])
def add_account(role, lg, key):
    if lg == 'x@a' and key == 'yandex_lyceum_project':
        if not request.json:
            return jsonify({'error': 'json не передан или он пуст'})
        if role.lower() == 'admin':
            if not all(key in request.json for key in ['surname', 'name', 'email', 'password', 'store_address',
                                                       'store_name']):
                return jsonify({'error': 'Недостаточно данных в json для добавления администратора'})
            db_sess = db_session.create_session()
            if db_sess.query(People).filter(People.email == request.json['email']).first():  # уникален ли логин ?
                return jsonify({'error': 'к данному логину уже привязан аккаунт'})
            admin = People(
                surname=request.json['surname'],
                name=request.json['name'],
                email=request.json['email'],
                role='Admin'
            )
            admin.set_password(request.json['password'])
            db_sess.add(admin)
            db_sess.commit()
            work = Works(
                id=int(db_sess.query(People.id).filter(People.email == request.json['email']).first()[0]),
                store_name=request.json['store_name'],
                store_address=request.json['store_address']
            )
            db_sess.add(work)
            db_sess.commit()
            db_sess.close()
            return jsonify({'success': 'Успешно'})
        elif role.lower() == 'user':
            if not all(key in request.json for key in ['surname', 'name', 'email', 'password']):
                return jsonify({'error': 'Недостаточно данных в json для добавления юзера'})
            db_sess = db_session.create_session()
            if db_sess.query(People).filter(People.email == request.json['email']).first():  # уникален ли логин ?
                return jsonify({'error': 'к данному логину уже привязан аккаунт'})
            user = People(
                surname=request.json['surname'],
                name=request.json['name'],
                email=request.json['email'],
                role='User'
            )
            user.set_password(request.json['password'])
            db_sess.add(user)
            db_sess.commit()
            db_sess.close()
            return jsonify({'success': 'Успешно'})
    abort(403)


@blueprint.route('/api/del_account/<int:acc_id>&login=<string:lg>&token=<string:key>', methods=['DELETE', 'GET'])
def delete_account(acc_id, lg, key):
    if lg == 'x@a' and key == 'yandex_lyceum_project':
        db_sess = db_session.create_session()
        acc = db_sess.query(People).get(acc_id)
        if acc:
            db_sess.delete(acc)
            db_sess.commit()
            return jsonify({'success': 'Успешно'})
        return jsonify({'error': 'Аккаунта с таким id нет в базе. Попробуй добавить, потом можешь и удалить'})
    abort(403)


@blueprint.route('/api/upt_account/<int:acc_id>&login=<string:lg>&token=<string:key>', methods=['GET', 'PUT'])
def update_account(acc_id, lg, key):
    if lg == 'x@a' and key == 'yandex_lyceum_project':
        if not request.json:
            return jsonify({'error': 'json не передан или пуст'})
        if not all(key in ['email', 'name', 'surname', 'password', 'store_address', 'store_name']
                   for key in request.json.keys()):
            return jsonify({'error': 'Такого поля нет в таблице'})
        db_sess = db_session.create_session()
        acc = [x.serialize for x in db_sess.query(People).filter_by(id=acc_id).all()]
        if acc:
            if acc[0]['role'] == 'User' and\
                    ('store_address' in request.json.keys() or 'store_name' in request.json.keys()):
                return jsonify({'error': 'Инвалидное поле для юзера'})
            elif 'store_address' in request.json.keys():
                db_sess.query(Works).filter(Works.id == acc_id).update({'store_address': request.json["store_address"]})
                db_sess.commit()
                if 'store_name' in request.json.keys():
                    db_sess.query(Works).filter(Works.id == acc_id).update({'store_name': request.json["store_name"]})
                    db_sess.commit()
                for i in request.json.keys():
                    if i != 'store_address' and i != 'store_name':
                        db_sess.query(People).filter(People.id == acc_id).update({i: request.json[i]})
                        db_sess.commit()
            elif acc[0]['role'] == 'User' and not\
                    ('store_address' in request.json.keys() or 'store_name' in request.json.keys()):
                db_sess.query(People).filter(People.id == acc_id).update(request.json)
                db_sess.commit()
            return jsonify({'success': 'Успешно'})
        return jsonify({'error': 'Аккаунта с таким id нет в базе. Попробуйте добавить его'})
    abort(403)
