from flask import jsonify, request
from flask.views import MethodView
from errors.validation_error import ValidationError
from models import Publication
from validators.validate_publications import validate_add_publication


class PublicationsRouteHandler(MethodView):
    # Tämä vastaa post request methodiin osoiteessa /api/publications
    @validate_add_publication
    def post(self):
        request_body = request.get_json()
        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url)
        publication.create()
        
        return jsonify(publication=publication.to_json())

        
    # Tämä vastaa get request methodiin osoitteessa /api/publications
    def get(self):
        publications = Publication.get_all()
        return jsonify(publications=Publication.list_to_json(publications))

