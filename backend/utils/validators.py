import re
from datetime import date

ALLOWED_CATEGORIES = {
    'Technology',
    'Business',
    'Design',
    'Marketing',
    'Data Science',
    'Other',
}

PASSWORD_POLICY = {
    'min_length': 8,
    'uppercase': 1,
    'lowercase': 1,
    'digits': 1,
    'special': 1,
}


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str):
    if len(password) < PASSWORD_POLICY['min_length']:
        raise ValueError(f'Password must be at least {PASSWORD_POLICY["min_length"]} characters')
    if sum(1 for c in password if c.isupper()) < PASSWORD_POLICY['uppercase']:
        raise ValueError('Password must contain at least one uppercase letter')
    if sum(1 for c in password if c.islower()) < PASSWORD_POLICY['lowercase']:
        raise ValueError('Password must contain at least one lowercase letter')
    if sum(1 for c in password if c.isdigit()) < PASSWORD_POLICY['digits']:
        raise ValueError('Password must contain at least one digit')
    if sum(1 for c in password if not c.isalnum()) < PASSWORD_POLICY['special']:
        raise ValueError('Password must contain at least one special character')


def validate_date_format(value: str, field_name: str = 'date') -> date:
    if not value or not isinstance(value, str):
        raise ValueError(f'{field_name} is required')
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f'Invalid {field_name} format. Use YYYY-MM-DD')


def validate_category(category: str) -> str:
    if not category or not isinstance(category, str):
        raise ValueError('Category is required')
    category = category.strip()
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")
    return category


def validate_signup_payload(data: dict):
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not full_name:
        raise ValueError('Full name is required')
    if not email:
        raise ValueError('Email is required')
    if not is_valid_email(email):
        raise ValueError('Invalid email format')
    if not password:
        raise ValueError('Password is required')
    validate_password_strength(password)
    if password != confirm_password:
        raise ValueError('Password and confirm password do not match')

    return full_name, email, password, confirm_password


def validate_login_payload(data: dict):
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    remember_me = data.get('remember_me', False)

    if not email:
        raise ValueError('Email is required')
    if not password:
        raise ValueError('Password is required')

    return email, password, bool(remember_me)


def validate_reset_password_payload(data: dict):
    token = (data.get('token') or '').strip()
    new_password = data.get('new_password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not token:
        raise ValueError('Token is required')
    if not new_password:
        raise ValueError('New password is required')
    validate_password_strength(new_password)
    if new_password != confirm_password:
        raise ValueError('Password and confirm password do not match')

    return token, new_password, confirm_password


def validate_opportunity_payload(data: dict):
    name = (data.get('name') or '').strip()
    duration = (data.get('duration') or '').strip()
    start_date = (data.get('start_date') or '').strip()
    description = (data.get('description') or '').strip()
    skills = (data.get('skills') or '').strip()
    category = validate_category(data.get('category') or '')
    future_opportunities = (data.get('future_opportunities') or '').strip()
    max_applicants = data.get('max_applicants')

    if not name:
        raise ValueError('Name is required')
    if not duration:
        raise ValueError('Duration is required')
    parsed_date = validate_date_format(start_date, 'start_date')
    if not description:
        raise ValueError('Description is required')
    if not skills:
        raise ValueError('Skills are required')
    if not future_opportunities:
        raise ValueError('Future opportunities is required')

    if max_applicants is not None:
        if isinstance(max_applicants, str) and max_applicants.strip() == '':
            max_applicants = None
        else:
            try:
                max_applicants = int(max_applicants)
            except Exception:
                raise ValueError('max_applicants must be a number')

    return {
        'name': name,
        'duration': duration,
        'start_date': parsed_date,
        'description': description,
        'skills': skills,
        'category': category,
        'future_opportunities': future_opportunities,
        'max_applicants': max_applicants,
    }
