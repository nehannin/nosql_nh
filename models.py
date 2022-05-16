import pymongo
from pymongo.server_api import ServerApi

from config import Config


client = pymongo.MongoClient(
    Config.CONNECTION_STRING, 
    server_api=ServerApi('1'))
db = client.nelli_db


class Publication:
    def __init__(self, 
    title, 
    description, 
    url, 
    owner=None, 
    likes=[],
    _id=None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.likes = likes
        if _id is not None:
            _id = str(_id)
        self._id = _id

    
    def to_json(self):
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url
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
            'url': self.url
        })

        self._id = str(result.inserted_id)
    
    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = []
        for publication in publications_list:
            publication_object = Publication(
                publication['title'], 
                publication['description'], 
                publication['url'],
                _id=publication['_id']
            )
            publications.append(publication_object)
        return publications

