from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from models.user import db
import os
from datetime import timedelta

# Import routes
from routes.auth import auth_bp
from routes.user import user_bp
from routes.company import company_bp
from routes.product import product_bp
from routes.chat import chat_bp
from routes.market import market_bp
from routes.media import media_bp

# Import WebSocket handlers
from realtime.websocket_handlers import initialize_websocket_handlers

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///globaltrade.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    CORS(app, origins="*", supports_credentials=True)
    jwt = JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(market_bp, url_prefix='/api/market')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize WebSocket handlers
    ws_handler = initialize_websocket_handlers(socketio)
    
    # Store WebSocket handler in app context for access in routes
    app.ws_handler = ws_handler
    
    # Initialize AI agents
    try:
        from agents import agent_manager
        agent_manager.start()
        print("[Flask] AI agents initialized successfully")
    except Exception as e:
        print(f"[Flask] Failed to initialize AI agents: {e}")
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'GlobalTrade AI API is running',
            'features': {
                'ai_agents': True,
                'real_time_chat': True,
                'media_upload': True,
                'social_sharing': True,
                'market_research': True
            }
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app, socketio

# Create app instance
app, socketio = create_app()

if __name__ == '__main__':
    print("Starting GlobalTrade AI API server...")
    print("Features enabled:")
    print("- AI Multi-Agent System")
    print("- Real-time Communication")
    print("- Media Upload & Sharing")
    print("- Social Media Integration")
    print("- Market Research Tools")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

