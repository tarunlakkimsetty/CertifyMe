import secrets
from datetime import datetime, timedelta

from extensions import db
from flask_jwt_extended import create_access_token
from models.admin import Admin
from utils.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    ValidationError,
)
from utils.logger import configure_logging
from utils.validators import (
    validate_login_payload,
    validate_reset_password_payload,
    validate_signup_payload,
)

logger = configure_logging()


def register_admin(data: dict) -> Admin:
    logger.info('Signup attempt for email=%s', data.get('email'))
    try:
        full_name, email, password, confirm_password = validate_signup_payload(data)
    except ValueError as exc:
        raise ValidationError(str(exc))

    existing = Admin.query.filter_by(email=email).first()
    if existing:
        raise DuplicateEmailError('Email already exists')

    admin = Admin(full_name=full_name, email=email)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    logger.info('Signup successful for email=%s', email)
    return admin


def login_admin(data: dict):
    try:
        email, password, remember_me = validate_login_payload(data)
    except ValueError as exc:
        raise ValidationError(str(exc))

    logger.info('Login attempt for email=%s', email)
    admin = Admin.query.filter_by(email=email).first()
    if not admin or not admin.check_password(password):
        logger.warning('Login failed for email=%s', email)
        raise AuthenticationError('Invalid email or password')

    expiry = timedelta(days=7 if remember_me else 1)
    access_token = create_access_token(identity=str(admin.id), expires_delta=expiry)
    logger.info('Login successful for email=%s', email)
    return access_token, admin.to_dict()


def forgot_password(data: dict):
    email = (data.get('email') or '').strip().lower()
    if not email:
        return

    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        logger.info('Password reset requested for unknown email=%s', email)
        return

    admin.reset_token = secrets.token_urlsafe(32)
    admin.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    logger.info('Password reset token generated for email=%s', email)
    print(f"Password reset token for {email}: {admin.reset_token}")


def reset_password(data: dict):
    try:
        token, new_password, confirm_password = validate_reset_password_payload(data)
    except ValueError as exc:
        raise ValidationError(str(exc))

    admin = Admin.query.filter_by(reset_token=token).first()
    if not admin:
        raise ValidationError('Invalid token')

    expiry = admin.reset_token_expiry
    if not expiry or expiry < datetime.utcnow():
        raise ValidationError('Token expired')

    admin.set_password(new_password)
    admin.reset_token = None
    admin.reset_token_expiry = None
    db.session.commit()
    logger.info('Password reset completed for email=%s', admin.email)
