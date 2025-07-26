from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Product, MarketResearch
from src.agents import agent_manager
from datetime import datetime, timedelta
import asyncio

market_bp = Blueprint('market', __name__)

def run_async(coro):
    """Helper function to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@market_bp.route('/research', methods=['POST'])
@jwt_required()
def request_market_research():
    """Request market research for a product in target country"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['target_country', 'research_query']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate product if provided
        product_id = data.get('product_id')
        product = None
        if product_id:
            product = db.session.query(Product).join(Company).filter(
                Product.id == product_id,
                Company.user_id == current_user_id,
                Product.is_active == True
            ).first()
            
            if not product:
                return jsonify({'error': 'Product not found or access denied'}), 404
        
        # Create market research request
        research = MarketResearch(
            user_id=current_user_id,
            product_id=product_id,
            target_country=data['target_country'].strip(),
            research_query=data['research_query'].strip(),
            status='processing',
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(research)
        db.session.commit()
        
        # Prepare data for AI agent processing
        research_data = {
            'research_id': research.id,
            'product_name': product.name if product else data.get('product_name', 'General Product'),
            'target_country': data['target_country'].strip(),
            'product_category': product.category if product else data.get('product_category', 'General'),
            'research_query': data['research_query'].strip()
        }
        
        # Process with AI agents
        try:
            ai_result = run_async(agent_manager.process_market_research_request(research_data))
            
            if ai_result.get('success'):
                # Update research with AI results
                research.status = 'completed'
                research.set_research_data(ai_result.get('market_analysis', {}))
                research.set_contacts(ai_result.get('contacts', {}).get('contacts', []))
                research.set_market_analysis(ai_result.get('trends', {}))
            else:
                research.status = 'failed'
                
            db.session.commit()
            
        except Exception as e:
            print(f"AI processing error: {str(e)}")
            research.status = 'failed'
            db.session.commit()
        
        return jsonify({
            'message': 'Market research request submitted successfully',
            'research': research.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Market research request failed', 'details': str(e)}), 500

@market_bp.route('/research', methods=['GET'])
@jwt_required()
def get_market_research():
    """Get user's market research requests"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        country = request.args.get('country')
        
        # Build query
        query = MarketResearch.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter(MarketResearch.status == status)
        
        if country:
            query = query.filter(MarketResearch.target_country.ilike(f'%{country}%'))
        
        # Execute paginated query
        research_requests = query.order_by(MarketResearch.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'research_requests': [research.to_dict() for research in research_requests.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': research_requests.total,
                'pages': research_requests.pages,
                'has_next': research_requests.has_next,
                'has_prev': research_requests.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get market research', 'details': str(e)}), 500

@market_bp.route('/research/<int:research_id>', methods=['GET'])
@jwt_required()
def get_research_details(research_id):
    """Get detailed market research results"""
    try:
        current_user_id = get_jwt_identity()
        
        research = MarketResearch.query.filter_by(
            id=research_id,
            user_id=current_user_id
        ).first()
        
        if not research:
            return jsonify({'error': 'Research not found or access denied'}), 404
        
        return jsonify({
            'research': research.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get research details', 'details': str(e)}), 500

@market_bp.route('/contacts', methods=['POST'])
@jwt_required()
def search_contacts():
    """Search for business contacts in target market"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['country', 'industry']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Use AI agent to discover contacts
        try:
            ai_result = run_async(agent_manager.discover_contacts(
                country=data['country'],
                industry=data['industry'],
                company_size=data.get('company_size', 'any'),
                contact_type=data.get('contact_type', 'buyer')
            ))
            
            if ai_result.get('success'):
                return jsonify({
                    'contacts': ai_result['data']['contacts'],
                    'search_criteria': data,
                    'total_found': ai_result['data']['total_found']
                }), 200
            else:
                return jsonify({
                    'error': 'Contact search failed',
                    'details': ai_result.get('error', 'Unknown error')
                }), 500
                
        except Exception as e:
            return jsonify({
                'error': 'Contact search failed',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': 'Contact search failed', 'details': str(e)}), 500

@market_bp.route('/trends', methods=['GET'])
def get_market_trends():
    """Get market trends and insights"""
    try:
        country = request.args.get('country')
        industry = request.args.get('industry')
        
        # TODO: Implement AI agent market trends analysis
        # For now, return mock data
        mock_trends = {
            'country': country or 'Global',
            'industry': industry or 'All Industries',
            'trends': [
                {
                    'title': 'Growing Demand for Specialty Coffee',
                    'description': 'Premium coffee consumption is increasing by 15% annually in Italy',
                    'impact': 'high',
                    'timeframe': '2024-2025'
                },
                {
                    'title': 'Sustainability Focus',
                    'description': 'Italian consumers increasingly prefer sustainably sourced products',
                    'impact': 'medium',
                    'timeframe': '2024-2026'
                },
                {
                    'title': 'Direct Trade Relationships',
                    'description': 'More Italian roasters seeking direct relationships with coffee farmers',
                    'impact': 'high',
                    'timeframe': '2024-2025'
                }
            ],
            'market_size': {
                'value': '2.5 billion EUR',
                'growth_rate': '8.5%',
                'year': '2024'
            },
            'key_players': [
                'Lavazza', 'Illy', 'Segafredo', 'Kimbo'
            ],
            'import_statistics': {
                'total_imports': '500,000 tons',
                'top_sources': ['Brazil', 'Vietnam', 'Colombia', 'Indonesia'],
                'growth_trend': 'increasing'
            }
        }
        
        return jsonify({
            'trends': mock_trends
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get market trends', 'details': str(e)}), 500

@market_bp.route('/opportunities', methods=['POST'])
@jwt_required()
def find_opportunities():
    """Find business opportunities based on user's products"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get user's products
        user_products = db.session.query(Product).join(Company).filter(
            Company.user_id == current_user_id,
            Product.is_active == True,
            Company.is_active == True
        ).all()
        
        if not user_products:
            return jsonify({'error': 'No active products found'}), 404
        
        # TODO: Implement AI agent opportunity matching
        # For now, return mock opportunities
        mock_opportunities = [
            {
                'id': 1,
                'title': 'Italian Coffee Market Expansion',
                'description': 'Growing demand for premium Sumatra coffee in Northern Italy',
                'market': 'Italy',
                'industry': 'Food & Beverage',
                'potential_value': '50,000 - 100,000 EUR',
                'confidence': 85,
                'matched_products': [product.to_dict() for product in user_products[:2]],
                'key_requirements': [
                    'Organic certification',
                    'Consistent supply capacity',
                    'Competitive pricing'
                ],
                'next_steps': [
                    'Contact Italian coffee importers',
                    'Prepare product samples',
                    'Obtain organic certification'
                ]
            }
        ]
        
        return jsonify({
            'opportunities': mock_opportunities,
            'total_found': len(mock_opportunities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to find opportunities', 'details': str(e)}), 500

@market_bp.route('/regulations', methods=['GET'])
def get_trade_regulations():
    """Get trade regulations and requirements"""
    try:
        origin_country = request.args.get('origin_country')
        target_country = request.args.get('target_country')
        product_category = request.args.get('product_category')
        
        if not origin_country or not target_country:
            return jsonify({'error': 'origin_country and target_country are required'}), 400
        
        # TODO: Implement AI agent regulation lookup
        # For now, return mock data
        mock_regulations = {
            'origin_country': origin_country,
            'target_country': target_country,
            'product_category': product_category,
            'requirements': [
                {
                    'type': 'Documentation',
                    'title': 'Certificate of Origin',
                    'description': 'Required for all coffee imports to Italy',
                    'mandatory': True
                },
                {
                    'type': 'Quality Standards',
                    'title': 'EU Food Safety Standards',
                    'description': 'Must comply with EU regulations on food safety',
                    'mandatory': True
                },
                {
                    'type': 'Tariffs',
                    'title': 'Import Duty',
                    'description': '7.5% duty on green coffee beans',
                    'mandatory': True
                },
                {
                    'type': 'Certification',
                    'title': 'Organic Certification',
                    'description': 'EU organic certification for premium pricing',
                    'mandatory': False
                }
            ],
            'estimated_costs': {
                'import_duty': '7.5%',
                'documentation_fees': '200-500 EUR',
                'inspection_fees': '100-300 EUR'
            },
            'processing_time': '5-10 business days',
            'useful_links': [
                'https://ec.europa.eu/food/safety_en',
                'https://www.ice.it/en/markets/italy'
            ]
        }
        
        return jsonify({
            'regulations': mock_regulations
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get trade regulations', 'details': str(e)}), 500

