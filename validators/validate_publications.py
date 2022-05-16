from xml.dom import ValidationErr
from flask import request
from errors.validation_error import ValidationError

def validate_add_publication(publications_route_handler):
    def validate_add_publication_wrapper(*args, **kwargs):
        request_body = request.get_json()
        if 'title' in request_body and 'description' in request_body and 'url' in request_body:
            return publications_route_handler(*args, **kwargs)
        raise ValidationError(message='Title, description and url are required.')
    return validate_add_publication_wrapper
