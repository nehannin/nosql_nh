from flask.views import MethodView
from flask import jsonify, request
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from models import User
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import jwt_required, get_jwt, create_access_token

from validators.auth import validate_logged_in_user

class AccountPasswordRouteHanlder(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body and 'password' in request_body:
            account.password = sha256.hash(request_body['password'])
            account.update_password()
            return ""
        raise ValidationError(message='password is required')

class AccountRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def get(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        return jsonify(account=account.to_json())
    
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self):
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body and 'username' in request_body:
            account.username = request_body['username']
            account.update()
            return jsonify(account=account.to_json())
        raise ValidationError(message='username is required')

class RegisterRouteHandler(MethodView):
    def post(self):
        request_body = request.get_json()
        username = request_body['username']
        password = request_body['password']
        hashed_password = sha256.hash(password)
        user = User(username, password=hashed_password)
        user.create()
        return jsonify(user=user.to_json())
    
class LoginRouteHandler(MethodView):
    def post(self):
        request_body = request.get_json()
        # 1. Haetaan käyttäjä käyttäjänimellä
        user = User.get_by_username(request_body['username'])
        # 2. Tarkistetaan onko salasana oikein
        if sha256.verify(request_body['password'], user.password):
            access_token = create_access_token(user._id, additional_claims={'username': user.username, 'role': user.role})
            return jsonify(access_token=access_token)
        raise NotFound(message='user not found')

