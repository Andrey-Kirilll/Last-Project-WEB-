from flask import jsonify, Blueprint
from flask_login import login_required
from flask_restful import abort
from . import db_session
from .models import People
from .permissions_checker import who_are_you

blueprint = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/json/all_accounts')
@login_required
def get_accounts():
    if who_are_you() == 'mdr':
        db_sess = db_session.create_session()
        admins = db_sess.query(People).filter(People.role == 'Admin').all()
        users = db_sess.query(People).filter(People.role == 'User').all()
        return jsonify(
            {'Administrators': [item.to_dict(only=('id', 'email')) for item in admins]},
            {'Users': [item.to_dict(only=('id', 'email')) for item in users]}
        )
    abort(403)


@blueprint.route('/api/json/get_one_account/<int:acc_id>')
@login_required
def get_one_account():
    if who_are_you() == 'mdr':
        pass
    abort(403)
