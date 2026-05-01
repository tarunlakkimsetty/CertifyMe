from datetime import date

from backend.extensions import db
from backend.models.opportunity import Opportunity
from backend.models.admin import Admin
from backend.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from backend.utils.logger import configure_logging
from backend.utils.validators import validate_opportunity_payload

logger = configure_logging()


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except Exception:
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')


def get_opportunities_for_admin(admin_id: int, page: int = 1, limit: int = 10):
    query = Opportunity.query.filter_by(admin_id=admin_id).order_by(Opportunity.created_at.desc())
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return pagination


def create_opportunity(admin_id: int, data: dict) -> Opportunity:
    admin = db.session.get(Admin, admin_id)
    if not admin:
        raise ValidationError('Admin not found')

    payload = validate_opportunity_payload(data)
    opp = Opportunity(
        admin_id=admin.id,
        name=payload['name'],
        duration=payload['duration'],
        start_date=payload['start_date'],
        description=payload['description'],
        skills=payload['skills'],
        category=payload['category'],
        future_opportunities=payload['future_opportunities'],
        max_applicants=payload['max_applicants'],
    )
    db.session.add(opp)
    db.session.commit()
    logger.info('Opportunity created admin_id=%s opportunity_id=%s', admin_id, opp.id)
    return opp


def _get_opportunity_by_id(opp_id: int):
    return db.session.get(Opportunity, opp_id)


def get_opportunity_for_admin(admin_id: int, opp_id: int) -> Opportunity:
    opp = _get_opportunity_by_id(opp_id)
    if not opp:
        raise NotFoundError('Opportunity not found')
    if opp.admin_id != admin_id:
        raise ForbiddenError('Access denied')
    return opp


def update_opportunity(admin_id: int, opp_id: int, data: dict) -> Opportunity:
    opp = _get_opportunity_by_id(opp_id)
    if not opp:
        raise NotFoundError('Opportunity not found')
    if opp.admin_id != admin_id:
        raise ForbiddenError('Access denied')

    payload = validate_opportunity_payload(data)
    opp.name = payload['name']
    opp.duration = payload['duration']
    opp.start_date = payload['start_date']
    opp.description = payload['description']
    opp.skills = payload['skills']
    opp.category = payload['category']
    opp.future_opportunities = payload['future_opportunities']
    opp.max_applicants = payload['max_applicants']
    db.session.commit()
    logger.info('Opportunity updated admin_id=%s opportunity_id=%s', admin_id, opp_id)
    return opp


def delete_opportunity(admin_id: int, opp_id: int):
    opp = _get_opportunity_by_id(opp_id)
    if not opp:
        raise NotFoundError('Opportunity not found')
    if opp.admin_id != admin_id:
        raise ForbiddenError('Access denied')
    db.session.delete(opp)
    db.session.commit()
    logger.info('Opportunity deleted admin_id=%s opportunity_id=%s', admin_id, opp_id)
