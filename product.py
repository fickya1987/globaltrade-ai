from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Company, Product
from sqlalchemy import or_

product_bp = Blueprint('product', __name__)

@product_bp.route('', methods=['GET'])
def get_products():
    """Get list of products with optional filters"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        country = request.args.get('country')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        company_id = request.args.get('company_id', type=int)
        
        # Build query with joins
        query = db.session.query(Product).join(Company).filter(
            Product.is_active == True,
            Company.is_active == True
        )
        
        if category:
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        if country:
            query = query.filter(Company.country.ilike(f'%{country}%'))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%'),
                    Company.name.ilike(f'%{search}%')
                )
            )
        
        if company_id:
            query = query.filter(Product.company_id == company_id)
        
        # Execute paginated query
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get products', 'details': str(e)}), 500

@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_id', 'name', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify user owns the company
        company = Company.query.filter_by(
            id=data['company_id'],
            user_id=current_user_id,
            is_active=True
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found or access denied'}), 404
        
        # Create new product
        product = Product(
            company_id=data['company_id'],
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            category=data['category'].strip(),
            price=data.get('price'),
            currency=data.get('currency', 'USD'),
            unit=data.get('unit', '').strip(),
            minimum_order=data.get('minimum_order')
        )
        
        # Handle images
        if data.get('images'):
            product.set_images(data['images'])
        
        # Handle specifications
        if data.get('specifications'):
            product.set_specifications(data['specifications'])
        
        # Handle certifications
        if data.get('certifications'):
            product.set_certifications(data['certifications'])
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Product creation failed', 'details': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details by ID"""
    try:
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        
        if not product or not product.company.is_active:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get product', 'details': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product details"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get product and verify ownership through company
        product = db.session.query(Product).join(Company).filter(
            Product.id == product_id,
            Company.user_id == current_user_id,
            Product.is_active == True
        ).first()
        
        if not product:
            return jsonify({'error': 'Product not found or access denied'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'category', 'price', 'currency',
            'unit', 'minimum_order'
        ]
        
        for field in allowed_fields:
            if field in data:
                if field in ['name', 'description', 'category', 'unit']:
                    setattr(product, field, data[field].strip() if data[field] else '')
                else:
                    setattr(product, field, data[field])
        
        # Handle images
        if 'images' in data:
            product.set_images(data['images'])
        
        # Handle specifications
        if 'specifications' in data:
            product.set_specifications(data['specifications'])
        
        # Handle certifications
        if 'certifications' in data:
            product.set_certifications(data['certifications'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Product update failed', 'details': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete (deactivate) product"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get product and verify ownership through company
        product = db.session.query(Product).join(Company).filter(
            Product.id == product_id,
            Company.user_id == current_user_id
        ).first()
        
        if not product:
            return jsonify({'error': 'Product not found or access denied'}), 404
        
        # Soft delete - just mark as inactive
        product.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Product deletion failed', 'details': str(e)}), 500

@product_bp.route('/my-products', methods=['GET'])
@jwt_required()
def get_my_products():
    """Get current user's products across all companies"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get products from all user's companies
        products = db.session.query(Product).join(Company).filter(
            Company.user_id == current_user_id,
            Product.is_active == True,
            Company.is_active == True
        ).order_by(Product.created_at.desc()).all()
        
        return jsonify({
            'products': [product.to_dict() for product in products]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your products', 'details': str(e)}), 500

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of available product categories"""
    try:
        # Get distinct categories from database
        categories = db.session.query(Product.category).filter(
            Product.category.isnot(None),
            Product.category != '',
            Product.is_active == True
        ).distinct().all()
        
        category_list = [category[0] for category in categories if category[0]]
        
        # Add common categories if not in database
        common_categories = [
            'Agriculture & Food', 'Automotive & Transportation', 'Chemicals & Materials',
            'Construction & Building', 'Electronics & Technology', 'Energy & Environment',
            'Fashion & Textiles', 'Health & Beauty', 'Home & Garden', 'Industrial Equipment',
            'Machinery & Tools', 'Metals & Mining', 'Packaging & Printing', 'Sports & Recreation',
            'Toys & Games'
        ]
        
        for category in common_categories:
            if category not in category_list:
                category_list.append(category)
        
        return jsonify({
            'categories': sorted(category_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500

@product_bp.route('/search', methods=['POST'])
def search_products():
    """Advanced product search with multiple criteria"""
    try:
        data = request.get_json()
        
        # Get search parameters
        query_text = data.get('query', '')
        categories = data.get('categories', [])
        countries = data.get('countries', [])
        price_range = data.get('price_range', {})
        page = data.get('page', 1)
        per_page = min(data.get('per_page', 20), 100)
        
        # Build query
        query = db.session.query(Product).join(Company).filter(
            Product.is_active == True,
            Company.is_active == True
        )
        
        # Text search
        if query_text:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{query_text}%'),
                    Product.description.ilike(f'%{query_text}%'),
                    Company.name.ilike(f'%{query_text}%')
                )
            )
        
        # Category filter
        if categories:
            query = query.filter(Product.category.in_(categories))
        
        # Country filter
        if countries:
            query = query.filter(Company.country.in_(countries))
        
        # Price range filter
        if price_range.get('min') is not None:
            query = query.filter(Product.price >= price_range['min'])
        if price_range.get('max') is not None:
            query = query.filter(Product.price <= price_range['max'])
        
        # Execute paginated query
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            },
            'search_query': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Product search failed', 'details': str(e)}), 500

