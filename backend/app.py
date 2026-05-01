import os
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.extensions import db, migrate, jwt, bcrypt
from backend.routes.auth_routes import auth_bp
from backend.routes.opportunity_routes import opp_bp
from backend.utils.error_handlers import register_error_handlers
from backend.utils.logger import configure_logging

logger = configure_logging()


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config.setdefault('JWT_TOKEN_LOCATION', ['headers'])
    app.config.setdefault('JWT_HEADER_NAME', 'Authorization')
    app.config.setdefault('JWT_HEADER_TYPE', 'Bearer')
    app.config.setdefault('PROPAGATE_EXCEPTIONS', False)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    @jwt.unauthorized_loader
    def handle_missing_jwt(reason):
        return jsonify({'error': reason, 'status': 401}), 401

    @jwt.invalid_token_loader
    def handle_invalid_jwt(reason):
        return jsonify({'error': reason, 'status': 401}), 401

    @jwt.expired_token_loader
    def handle_expired_jwt(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired', 'status': 401}), 401

    @jwt.revoked_token_loader
    def handle_revoked_jwt(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has been revoked', 'status': 401}), 401

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(opp_bp, url_prefix='/opportunities')

    register_error_handlers(app)

    @app.route('/', methods=['GET'])
    def health():
        return jsonify({'message': 'API Running'}), 200

    @app.route('/docs', methods=['GET'])
    def docs():
        return jsonify({
            'endpoints': [
                {
                    'path': '/',
                    'method': 'GET',
                    'description': 'Health check endpoint',
                },
                {
                    'path': '/docs',
                    'method': 'GET',
                    'description': 'API documentation',
                },
                {
                    'path': '/auth/signup',
                    'method': 'POST',
                    'description': 'Register a new admin user',
                },
                {
                    'path': '/auth/login',
                    'method': 'POST',
                    'description': 'Authenticate and obtain JWT token',
                },
                {
                    'path': '/auth/forgot-password',
                    'method': 'POST',
                    'description': 'Start password reset workflow',
                },
                {
                    'path': '/auth/reset-password',
                    'method': 'POST',
                    'description': 'Complete password reset using a token',
                },
                {
                    'path': '/opportunities',
                    'method': 'GET',
                    'description': 'List opportunities for current admin with pagination',
                },
                {
                    'path': '/opportunities',
                    'method': 'POST',
                    'description': 'Create a new opportunity',
                },
                {
                    'path': '/opportunities/<id>',
                    'method': 'GET',
                    'description': 'Retrieve a single opportunity by ID',
                },
                {
                    'path': '/opportunities/<id>',
                    'method': 'PUT',
                    'description': 'Update an opportunity',
                },
                {
                    'path': '/opportunities/<id>',
                    'method': 'DELETE',
                    'description': 'Delete an opportunity',
                },
            ]
        }), 200

    return app


# Expose the application for WSGI servers like gunicorn used by Render.
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
