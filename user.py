from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('', methods=['GET'])
def get_users():
    """Get list of users (public profiles only)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        country = request.args.get('country')
        search = request.args.get('search')
        
        # Build query for active users only
        query = User.query.filter_by(is_active=True)
        
        if country:
            query = query.filter(User.country.ilike(f'%{country}%'))
        
        if search:
            query = query.filter(
                (User.first_name.ilike(f'%{search}%')) |
                (User.last_name.ilike(f'%{search}%'))
            )
        
        # Execute paginated query
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile by ID"""
    try:
        user = User.query.filter_by(id=user_id, is_active=True).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500

@user_bp.route('/search', methods=['POST'])
def search_users():
    """Search users with advanced criteria"""
    try:
        data = request.get_json()
        
        # Get search parameters
        query_text = data.get('query', '')
        countries = data.get('countries', [])
        languages = data.get('languages', [])
        verified_only = data.get('verified_only', False)
        page = data.get('page', 1)
        per_page = min(data.get('per_page', 20), 100)
        
        # Build query
        query = User.query.filter_by(is_active=True)
        
        # Text search
        if query_text:
            query = query.filter(
                (User.first_name.ilike(f'%{query_text}%')) |
                (User.last_name.ilike(f'%{query_text}%'))
            )
        
        # Country filter
        if countries:
            query = query.filter(User.country.in_(countries))
        
        # Language filter
        if languages:
            query = query.filter(User.language.in_(languages))
        
        # Verified filter
        if verified_only:
            query = query.filter(User.is_verified == True)
        
        # Execute paginated query
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            },
            'search_query': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'User search failed', 'details': str(e)}), 500

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get current user', 'details': str(e)}), 500

@user_bp.route('/me/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get current user's statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Calculate statistics
        stats = {
            'companies_count': len([c for c in user.companies if c.is_active]),
            'products_count': sum(len([p for p in c.products if p.is_active]) for c in user.companies if c.is_active),
            'messages_sent': len(user.sent_messages),
            'messages_received': len(user.received_messages),
            'research_requests': len(user.market_research),
            'verified_companies': len([c for c in user.companies if c.is_active and c.verification_status == 'verified']),
            'member_since': user.created_at.isoformat() if user.created_at else None
        }
        
        return jsonify({
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user stats', 'details': str(e)}), 500

@user_bp.route('/countries', methods=['GET'])
def get_user_countries():
    """Get list of countries with users"""
    try:
        # Get distinct countries from database
        countries = db.session.query(User.country).filter(
            User.country.isnot(None),
            User.country != '',
            User.is_active == True
        ).distinct().all()
        
        country_list = [country[0] for country in countries if country[0]]
        
        # Add common countries if not in database
        common_countries = [
            'United States', 'China', 'Germany', 'Japan', 'United Kingdom',
            'France', 'India', 'Italy', 'Brazil', 'Canada', 'Russia',
            'South Korea', 'Australia', 'Spain', 'Mexico', 'Indonesia',
            'Netherlands', 'Saudi Arabia', 'Turkey', 'Taiwan'
        ]
        
        for country in common_countries:
            if country not in country_list:
                country_list.append(country)
        
        return jsonify({
            'countries': sorted(country_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get countries', 'details': str(e)}), 500

@user_bp.route('/languages', methods=['GET'])
def get_user_languages():
    """Get list of supported languages"""
    try:
        # Common languages with their codes
        languages = [
            {'code': 'en', 'name': 'English'},
            {'code': 'es', 'name': 'Spanish'},
            {'code': 'fr', 'name': 'French'},
            {'code': 'de', 'name': 'German'},
            {'code': 'it', 'name': 'Italian'},
            {'code': 'pt', 'name': 'Portuguese'},
            {'code': 'ru', 'name': 'Russian'},
            {'code': 'zh', 'name': 'Chinese'},
            {'code': 'ja', 'name': 'Japanese'},
            {'code': 'ko', 'name': 'Korean'},
            {'code': 'ar', 'name': 'Arabic'},
            {'code': 'hi', 'name': 'Hindi'},
            {'code': 'id', 'name': 'Indonesian'},
            {'code': 'th', 'name': 'Thai'},
            {'code': 'vi', 'name': 'Vietnamese'},
            {'code': 'tr', 'name': 'Turkish'},
            {'code': 'pl', 'name': 'Polish'},
            {'code': 'nl', 'name': 'Dutch'},
            {'code': 'sv', 'name': 'Swedish'},
            {'code': 'da', 'name': 'Danish'}
        ]
        
        return jsonify({
            'languages': languages
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get languages', 'details': str(e)}), 500

