import pymongo
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from config import Config
from errors.not_found import NotFound
from errors.validation_error import ValidationError


client = pymongo.MongoClient(
    Config.CONNECTION_STRING, 
    server_api=ServerApi('1'))
db = client.nelli_db


class User:
    def __init__(self, username, password=None, role='user', _id=None):
        self.username = username
        self.password = password
        self.role = role
        if _id is not None:
            _id = str(_id)
        self._id = _id
    
    def to_json(self):
        return {
            '_id': str(self._id),
            'username': self.username,
            'role': self.role,
        }
    
    def update_password(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'password': self.password}
        }
        db.users.update_one(_filter, _update)
    
    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'username': self.username}
        }
        user = db.users.find_one({'username': self.username, '_id': {'$ne': ObjectId(self._id)}})
        if user is not None:
            raise ValidationError(message='username must be unique')
        db.users.update_one(_filter, _update)
    
    @staticmethod
    def list_to_json(user_list):
        users = []
        for user in user_list:
            users.append(user.to_json())
        return users
    
    @staticmethod
    def delete_by_id(_id):
        db.users.delete_one({'_id': ObjectId(_id)})

    @staticmethod
    def get_all():
        users_cursor = db.users.find()
        users_list = list(users_cursor)
        users = []
        for user_dictionary in users_list:
            users.append(User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id']))
        return users
    
    @staticmethod
    def get_by_id(_id):
        user_dictionary = db.users.find_one({'_id': ObjectId(_id)})
        if user_dictionary is None:
            raise NotFound(message='user not found')
        user = User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id'])
        return user
    
    @staticmethod
    def get_by_username(username):
        user_dictionary = db.users.find_one({'username': username})
        if user_dictionary is None:
            raise NotFound(message='user not found')
        user = User(user_dictionary['username'], role=user_dictionary['role'], _id=user_dictionary['_id'], password=user_dictionary['password'])
        return user

    def create(self):
        user = db.users.find_one({'username': self.username})
        if user is not None:
            raise ValidationError(message='username must be unique')
        result = db.users.insert_one({'username': self.username, 'role': self.role, 'password': self.password})
        self._id = str(result.inserted_id)


class Publication:
    def __init__(self, 
                title, 
                description, 
                url, 
                owner=None, 
                visibility=2,
                likes=[], # Tähän tallennetaan publicationista tykänneiden käyttäjien _id (ObjectId)
                _id=None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.visibility = visibility
        self.likes = likes
        if _id is not None:
            _id = str(_id)
        self._id = _id

    
    
    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
            '$set': {'title': self.title, 'description': self.description, 'visibility': self.visibility}
        }
        db.publications.update_one(_filter, _update)

    @staticmethod
    def delete_by_id_and_owner(_id, owner):
        result = db.publications.delete_one({'_id': ObjectId(_id), 'owner': ObjectId(owner['sub'])})
        if result.deleted_count == 0:
            raise NotFound(message='publication not found')
    
    @staticmethod
    def delete_by_id(_id):
        result = db.publications.delete_one({'_id': ObjectId(_id)})
        if result.deleted_count == 0:
            raise NotFound(message='publication not found')
    
    @staticmethod
    def get_by_id(_id):
        publication_dictionary = db.publications.find_one({'_id': ObjectId(_id)})
        if publication_dictionary is None:
            raise NotFound(message='publication not found')
        publication = Publication._from_json(publication_dictionary)
        return publication

    @staticmethod
    def get_by_visibility(visibility=2):
        publications_cursor = db.publications.find({'visibility':visibility})
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications
    
    @staticmethod
    def get_one_by_id_and_visibility(_id, visibility=2):
        publication = db.publications.find_one({'_id': ObjectId(_id), 'visibility':visibility})
        if publication is None:
            raise NotFound(message='publication not found')
        return Publication._from_json(publication)
    
    @staticmethod
    def get_logged_in_users_and_public_publications(logged_in_user):
        _filter = {
            '$or': [
                {'owner': ObjectId(logged_in_user['sub'])},
                {'visibility': {'$in': [1,2]}}
            ]
        }
        publications_cursor = db.publications.find(_filter)
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications
    
    @staticmethod
    def get_logged_in_users_and_public_publication(_id, logged_in_user):
        _filter = {
            # Hae ensimmäinen, jossa _id = _id ja (owner = sisäänkirjautunut käyttäjä tai visibility on 1 tai visibility on 2)
            '_id': ObjectId(_id),
            '$or': [
                {'owner': ObjectId(logged_in_user['sub'])},
                {'visibility': {'$in': [1,2]}}
            ]
        }
        publication = db.publications.find_one(_filter)
        if publication is None:
            raise NotFound(message='publication not found')
        publication_object = Publication._from_json(publication)
        return publication_object

    def to_json(self):
        owner = self.owner
        if owner is not None:
            owner = str(owner)
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': owner,
            'visibility': self.visibility
        }
    
    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications

    
    # CRUD:n C (Create)
    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': ObjectId(self.owner),
            'visibility': self.visibility
        })

        self._id = str(result.inserted_id)
    
    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = Publication._list_from_json(publications_list)
        return publications
    
    @staticmethod
    def _from_json(publication):
        publication_object = Publication(
                publication['title'], 
                publication['description'], 
                publication['url'],
                _id=publication['_id'],
                owner=publication.get('owner', None),
                visibility=publication.get('visibility', 2)
            )
        return publication_object
    
    @staticmethod
    def _list_from_json(list_of_dictionaries):
        publications = []
        for publication in list_of_dictionaries:
            publication_object = Publication._from_json(publication)
            publications.append(publication_object)
        return publications

