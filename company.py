from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Company
from sqlalchemy import or_

company_bp = Blueprint('company', __name__)

@company_bp.route('', methods=['GET'])
def get_companies():
    """Get list of companies with optional filters"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        country = request.args.get('country')
        industry = request.args.get('industry')
        search = request.args.get('search')
        verified_only = request.args.get('verified_only', 'false').lower() == 'true'
        
        # Build query
        query = Company.query.filter_by(is_active=True)
        
        if country:
            query = query.filter(Company.country.ilike(f'%{country}%'))
        
        if industry:
            query = query.filter(Company.industry.ilike(f'%{industry}%'))
        
        if search:
            query = query.filter(
                or_(
                    Company.name.ilike(f'%{search}%'),
                    Company.description.ilike(f'%{search}%')
                )
            )
        
        if verified_only:
            query = query.filter(Company.verification_status == 'verified')
        
        # Execute paginated query
        companies = query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'companies': [company.to_dict() for company in companies.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': companies.total,
                'pages': companies.pages,
                'has_next': companies.has_next,
                'has_prev': companies.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get companies', 'details': str(e)}), 500

@company_bp.route('', methods=['POST'])
@jwt_required()
def create_company():
    """Create a new company"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'country']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already has a company with this name
        existing_company = Company.query.filter_by(
            user_id=current_user_id,
            name=data['name'].strip()
        ).first()
        
        if existing_company:
            return jsonify({'error': 'You already have a company with this name'}), 409
        
        # Create new company
        company = Company(
            user_id=current_user_id,
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            industry=data.get('industry', '').strip(),
            country=data['country'].strip(),
            city=data.get('city', '').strip(),
            address=data.get('address', '').strip(),
            phone=data.get('phone', '').strip(),
            website=data.get('website', '').strip(),
            logo_url=data.get('logo_url', '').strip()
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company created successfully',
            'company': company.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Company creation failed', 'details': str(e)}), 500

@company_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get company details by ID"""
    try:
        company = Company.query.filter_by(id=company_id, is_active=True).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        return jsonify({
            'company': company.to_dict(include_products=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get company', 'details': str(e)}), 500

@company_bp.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    """Update company details"""
    try:
        current_user_id = get_jwt_identity()
        company = Company.query.filter_by(id=company_id, user_id=current_user_id).first()
        
        if not company:
            return jsonify({'error': 'Company not found or access denied'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'industry', 'country', 'city', 
            'address', 'phone', 'website', 'logo_url'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(company, field, data[field].strip() if data[field] else '')
        
        # Reset verification status if critical info changed
        critical_fields = ['name', 'country', 'address', 'phone']
        if any(field in data for field in critical_fields):
            company.verification_status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company updated successfully',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Company update failed', 'details': str(e)}), 500

@company_bp.route('/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    """Delete (deactivate) company"""
    try:
        current_user_id = get_jwt_identity()
        company = Company.query.filter_by(id=company_id, user_id=current_user_id).first()
        
        if not company:
            return jsonify({'error': 'Company not found or access denied'}), 404
        
        # Soft delete - just mark as inactive
        company.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Company deletion failed', 'details': str(e)}), 500

@company_bp.route('/my-companies', methods=['GET'])
@jwt_required()
def get_my_companies():
    """Get current user's companies"""
    try:
        current_user_id = get_jwt_identity()
        companies = Company.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(Company.created_at.desc()).all()
        
        return jsonify({
            'companies': [company.to_dict(include_products=True) for company in companies]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your companies', 'details': str(e)}), 500

@company_bp.route('/industries', methods=['GET'])
def get_industries():
    """Get list of available industries"""
    try:
        # Get distinct industries from database
        industries = db.session.query(Company.industry).filter(
            Company.industry.isnot(None),
            Company.industry != '',
            Company.is_active == True
        ).distinct().all()
        
        industry_list = [industry[0] for industry in industries if industry[0]]
        
        # Add common industries if not in database
        common_industries = [
            'Agriculture', 'Automotive', 'Chemicals', 'Construction', 'Electronics',
            'Energy', 'Fashion', 'Food & Beverage', 'Healthcare', 'Manufacturing',
            'Mining', 'Retail', 'Technology', 'Textiles', 'Transportation'
        ]
        
        for industry in common_industries:
            if industry not in industry_list:
                industry_list.append(industry)
        
        return jsonify({
            'industries': sorted(industry_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get industries', 'details': str(e)}), 500

@company_bp.route('/countries', methods=['GET'])
def get_countries():
    """Get list of countries with companies"""
    try:
        # Get distinct countries from database
        countries = db.session.query(Company.country).filter(
            Company.country.isnot(None),
            Company.country != '',
            Company.is_active == True
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

