import random
import string
from flask import jsonify, request
from flask.views import MethodView
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from models import Publication, Comment
from validators.auth import validate_logged_in_user
from validators.validate_publications import validate_add_publication
from flask_jwt_extended import jwt_required, get_jwt
from bson import ObjectId


class PublicationsRouteHandler(MethodView):
    # Tämä vastaa post request methodiin osoiteessa /api/publications
    @validate_add_publication
    @jwt_required(optional=True)
    def post(self):
        logged_in_user = get_jwt()
        owner = None
        visibility = 2
        request_body = request.get_json()
        if logged_in_user:
            owner = logged_in_user['sub']
            visibility = request_body.get('visibility', 2)

        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url, owner=owner, visibility=visibility)
        publication.create()
        
        return jsonify(publication=publication.to_json())

        
    # Tämä vastaa get request methodiin osoitteessa /api/publications
    @jwt_required(optional=True)
    def get(self):
        publications = []
        logged_in_user = get_jwt()
        if not logged_in_user:
            # Käyttäjä ei ole kirjautunut sisään
            # Tässä haetaan vain ne publicationit, joiden visibility = 2
            publications = Publication.get_by_visibility()
        else: 
            if logged_in_user['role'] == 'admin':
                publications = Publication.get_all()
            elif logged_in_user['role'] == 'user':
                # Tässä haetaan käyttäjän omat julkaisut ja ne joissa visibility on 1 tai 2
                publications = Publication.get_logged_in_users_and_public_publications(logged_in_user)
        
        return jsonify(publications=Publication.list_to_json(publications))

class PublicationRouteHandler(MethodView):
    @jwt_required(optional=True)
    def get(self, _id):
        publication = None
        logged_in_user = get_jwt()
        if logged_in_user:
            if logged_in_user['role'] == 'admin':
                publication = Publication.get_by_id(_id)
            elif logged_in_user['role'] == 'user':
                publication = Publication.get_logged_in_users_and_public_publication(_id, logged_in_user)
        else: # Käyttäjä ei ole kirjautunut sisään
            publication = Publication.get_one_by_id_and_visibility(_id)
        return jsonify(publication=publication.to_json())
    
    @jwt_required(optional=False) # @jwt_required() oletusarvo on False
    @validate_logged_in_user
    def delete(self, _id):
        logged_in_user = get_jwt()
        if logged_in_user['role'] == 'admin':
            Publication.delete_by_id(_id)
        elif logged_in_user['role'] == 'user':
            Publication.delete_by_id_and_owner(_id, logged_in_user)

        return ""
    
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        if logged_in_user['role'] == 'user':
            if publication.owner is None or str(publication.owner) != logged_in_user['sub']:
                raise NotFound(message='publication not found')
        request_body = request.get_json()
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.visibility = request_body.get('visibility', publication.visibility)

        publication.update()
        return jsonify(publication=publication.to_json())

class LikePublicationRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self, _id):
        logged_in_user = get_jwt()

        publication = Publication.get_by_id(_id)
        found_index = -1 # Oletusarvo = -1, koska arrayt / listat alkavat 0:sta
        
        for index, user_object_id in enumerate(publication.likes):
            if str(user_object_id) == logged_in_user['sub']: # Jos tullaan tänne, sisäänkirjautuneen käyttäjän _id on likes -listassa
                found_index = index
                break

        if found_index != -1: # Mennään tänne, jos sisäänkirjautuneen käyttäjän _id on löytynyt likes -listasta
            del publication.likes[found_index]
        else: # Tänne mennään, jos käyttäjää ei löydy listasta
            publication.likes.append(ObjectId(logged_in_user['sub']))
        
        publication.like()
        return jsonify(publication=publication.to_json())

class SharePublicationRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self, _id):

        publication = Publication.get_by_id(_id)
        letters = string.ascii_lowercase

        if publication.share_link is None:
            publication.share_link = ''.join(random.choice(letters) for _ in range(8))
        
        publication.shares += 1 # publication.shares = publication.shares + 1
        publication.share()

        return jsonify(publication=publication.to_json())

class PublicationCommentsRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def post(self, _id):
        # 1. Ota request_body vastaan
        request_body = request.get_json()
        if request_body and 'body' in request_body:
            logged_in_user = get_jwt()
            comment = Comment(request_body['body'], logged_in_user['sub'], _id)
            comment.create()
            return jsonify(comment=comment.to_json())
        raise ValidationError(message='body is required')
