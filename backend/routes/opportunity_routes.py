from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.opportunity_service import (
    create_opportunity,
    get_opportunities_for_admin,
    get_opportunity_for_admin,
    update_opportunity,
    delete_opportunity,
)

opp_bp = Blueprint('opportunities', __name__)


def _get_admin_id():
    try:
        return int(get_jwt_identity())
    except (TypeError, ValueError):
        return None


@opp_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_all():
    admin_id = _get_admin_id()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    limit = max(1, min(limit, 100))
    pagination = get_opportunities_for_admin(admin_id, page=page, limit=limit)
    return jsonify(
        {
            'page': pagination.page,
            'limit': pagination.per_page,
            'total': pagination.total,
            'data': [opp.to_summary_dict() for opp in pagination.items],
        }
    ), 200


@opp_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def create():
    admin_id = _get_admin_id()
    data = request.get_json() or {}
    opp = create_opportunity(admin_id, data)
    return jsonify({'message': 'Opportunity created successfully', 'data': opp.to_dict()}), 201


@opp_bp.route('/<int:opp_id>', methods=['GET'])
@jwt_required()
def get_one(opp_id):
    admin_id = _get_admin_id()
    opp = get_opportunity_for_admin(admin_id, opp_id)
    return jsonify({'data': opp.to_dict()}), 200


@opp_bp.route('/<int:opp_id>', methods=['PUT'])
@jwt_required()
def update(opp_id):
    admin_id = _get_admin_id()
    data = request.get_json() or {}
    opp = update_opportunity(admin_id, opp_id, data)
    return jsonify({'message': 'Opportunity updated successfully', 'data': opp.to_dict()}), 200


@opp_bp.route('/<int:opp_id>', methods=['DELETE'])
@jwt_required()
def delete(opp_id):
    admin_id = _get_admin_id()
    delete_opportunity(admin_id, opp_id)
    return jsonify({'message': 'Opportunity deleted successfully'}), 200
