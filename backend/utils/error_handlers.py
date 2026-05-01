import logging
from flask import jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from .exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger('backend')
error_logger = logging.getLogger('backend.error')


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning('Validation error: %s', error)
        return jsonify({'error': str(error), 'status': 400}), 400

    @app.errorhandler(DuplicateEmailError)
    def handle_duplicate_email(error):
        logger.warning('Duplicate email: %s', error)
        return jsonify({'error': str(error), 'status': 409}), 409

    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        logger.warning('Authentication failure: %s', error)
        return jsonify({'error': str(error), 'status': 401}), 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        logger.warning('Forbidden access: %s', error)
        return jsonify({'error': str(error), 'status': 403}), 403

    @app.errorhandler(NotFoundError)
    def handle_custom_not_found(error):
        logger.warning('Not found: %s', error)
        return jsonify({'error': str(error), 'status': 404}), 404

    @app.errorhandler(404)
    def handle_404(error):
        logger.warning('Route not found: %s', error)
        return jsonify({'error': 'Resource not found', 'status': 404}), 404

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        error_logger.error('Database error: %s', error, exc_info=True)
        return jsonify({'error': 'A database error occurred', 'status': 500}), 500

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(error):
        logger.warning('JWT error: %s', error)
        return jsonify({'error': str(error), 'status': 401}), 401

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        if isinstance(error, HTTPException):
            status_code = error.code or 500
            message = error.description or 'An error occurred'
        else:
            status_code = 500
            message = 'An unexpected error occurred'
        error_logger.error('Unhandled exception: %s', error, exc_info=True)
        return jsonify({'error': message, 'status': status_code}), status_code
