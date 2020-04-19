"ICECREAM"
from bottle_jwt import jwt_auth_required

from ICECREAM.baseapp import BaseApp
from app_user.controller import get_users, create_user, get_user, delete_user
from ICECREAM.wrappers import db_handler, pass_data, jsonify


class USERApp(BaseApp):
    def call_router(self, core):
        core.route('/api/users/<pk>', 'GET', get_user, apply=[db_handler, jsonify, jwt_auth_required])
        core.route('/api/users', 'GET', get_users, apply=[db_handler, jsonify, jwt_auth_required])
        core.route('/api/user/<pk>', 'DELETE', delete_user, apply=[db_handler, jsonify, jwt_auth_required])
        core.route('/api/user', 'POST', create_user, apply=[pass_data, db_handler, jsonify, jwt_auth_required])
