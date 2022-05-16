from flask import jsonify, request
from bson import ObjectId
from models import db
from flask.views import MethodView


def update_user(request_body, _id):
    username = request_body['username']
        # username = request_body.get['username']

    _filter = {'_id': ObjectId(_id)}
    _update = {
        '$set': {'username': username}
    }

    db.users.update_one(_filter, _update)


class UsersRouteHandler(MethodView):
    def get(self):
        users_cursor = db.users.find()
        users_list = list(users_cursor)
        for user in users_list:
            user['_id'] = str(user['_id'])
        return jsonify(users=users_list)

    def post(self):
        request_body = request.get_json()

        # Lisätään uusi käyttäjä
        username = request_body['username']
        db.users.insert_one({'username': username })
        return ""


class UserRouteHandler(MethodView):
    def get(self, _id):
        user = db.users.find_one({'_id': ObjectId(_id)})
        user['_id'] = str(user['_id'])
        return jsonify(user=user)

    def delete(self, _id):
        db.users.delete_one({'_id': ObjectId(_id)})
        return ""
    
    def patch(self, _id):
        request_body = request.get_json()
        update_user(request_body, _id)
        return ""
    
    def put(self, _id):
        request_body = request.get_json()
        update_user(request_body, _id)
        return ""

