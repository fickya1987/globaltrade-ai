from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db, User, Message
from agents import agent_manager
from datetime import datetime
import asyncio

chat_bp = Blueprint('chat', __name__)

def run_async(coro):
    """Helper function to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def generate_conversation_id(user1_id, user2_id):
    """Generate consistent conversation ID for two users"""
    sorted_ids = sorted([user1_id, user2_id])
    return f"conv_{sorted_ids[0]}_{sorted_ids[1]}"

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get user's conversations"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all conversations where user is sender or receiver
        conversations = db.session.query(Message.conversation_id).filter(
            or_(
                Message.sender_id == current_user_id,
                Message.receiver_id == current_user_id
            )
        ).distinct().all()
        
        conversation_list = []
        for conv in conversations:
            conv_id = conv[0]
            
            # Get the latest message in this conversation
            latest_message = Message.query.filter_by(
                conversation_id=conv_id
            ).order_by(Message.created_at.desc()).first()
            
            if latest_message:
                # Get the other user in the conversation
                other_user_id = (
                    latest_message.receiver_id 
                    if latest_message.sender_id == current_user_id 
                    else latest_message.sender_id
                )
                other_user = User.query.get(other_user_id)
                
                # Count unread messages
                unread_count = Message.query.filter_by(
                    conversation_id=conv_id,
                    receiver_id=current_user_id,
                    is_read=False
                ).count()
                
                conversation_list.append({
                    'conversation_id': conv_id,
                    'other_user': other_user.to_dict() if other_user else None,
                    'latest_message': latest_message.to_dict(),
                    'unread_count': unread_count
                })
        
        # Sort by latest message time
        conversation_list.sort(
            key=lambda x: x['latest_message']['created_at'], 
            reverse=True
        )
        
        return jsonify({
            'conversations': conversation_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get conversations', 'details': str(e)}), 500

@chat_bp.route('/conversations', methods=['POST'])
@jwt_required()
def start_conversation():
    """Start a new conversation or get existing one"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('receiver_id'):
            return jsonify({'error': 'receiver_id is required'}), 400
        
        receiver_id = data['receiver_id']
        
        # Check if receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        if receiver_id == current_user_id:
            return jsonify({'error': 'Cannot start conversation with yourself'}), 400
        
        # Generate conversation ID
        conversation_id = generate_conversation_id(current_user_id, receiver_id)
        
        # Check if conversation already exists
        existing_message = Message.query.filter_by(
            conversation_id=conversation_id
        ).first()
        
        return jsonify({
            'conversation_id': conversation_id,
            'receiver': receiver.to_dict(),
            'exists': existing_message is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to start conversation', 'details': str(e)}), 500

@chat_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get messages in a conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Verify user is part of this conversation
        user_in_conversation = Message.query.filter(
            Message.conversation_id == conversation_id,
            or_(
                Message.sender_id == current_user_id,
                Message.receiver_id == current_user_id
            )
        ).first()
        
        if not user_in_conversation:
            return jsonify({'error': 'Conversation not found or access denied'}), 404
        
        # Get messages
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Mark messages as read
        Message.query.filter_by(
            conversation_id=conversation_id,
            receiver_id=current_user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'messages': [message.to_dict() for message in reversed(messages.items)],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': messages.total,
                'pages': messages.pages,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get messages', 'details': str(e)}), 500

@chat_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send a message in a conversation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('receiver_id'):
            return jsonify({'error': 'receiver_id is required'}), 400
        
        if not data.get('content') and not data.get('media_url'):
            return jsonify({'error': 'Either content or media_url is required'}), 400
        
        receiver_id = data['receiver_id']
        
        # Verify conversation ID matches users
        expected_conv_id = generate_conversation_id(current_user_id, receiver_id)
        if conversation_id != expected_conv_id:
            return jsonify({'error': 'Invalid conversation ID'}), 400
        
        # Check if receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            receiver_id=receiver_id,
            message_type=data.get('message_type', 'text'),
            content=data.get('content', '').strip(),
            media_url=data.get('media_url', '').strip()
        )
        
        # Handle translations if provided
        if data.get('translated_content'):
            message.set_translated_content(data['translated_content'])
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

@chat_bp.route('/translate', methods=['POST'])
@jwt_required()
def translate_message():
    """Translate a message to target language"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['text', 'target_language']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        text = data['text']
        target_language = data['target_language']
        source_language = data.get('source_language', 'auto')
        context = data.get('context', 'chat')
        
        # Use AI agent for translation
        try:
            result = run_async(agent_manager.translate_text(
                text=text,
                target_language=target_language,
                source_language=source_language,
                context=context
            ))
            
            if result.get('success'):
                return jsonify({
                    'original_text': text,
                    'translated_text': result['data']['translated_text'],
                    'source_language': result['data']['source_language'],
                    'target_language': target_language,
                    'confidence': result['data'].get('confidence', 0.95)
                }), 200
            else:
                return jsonify({
                    'error': 'Translation failed',
                    'details': result.get('error', 'Unknown error')
                }), 500
                
        except Exception as e:
            return jsonify({
                'error': 'Translation service error',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': 'Translation request failed', 'details': str(e)}), 500

@chat_bp.route('/cultural-context', methods=['POST'])
@jwt_required()
def get_cultural_context():
    """Get cultural context for business communication"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('country'):
            return jsonify({'error': 'country is required'}), 400
        
        country = data['country']
        business_context = data.get('business_context', 'general')
        communication_type = data.get('communication_type', 'chat')
        
        # Use AI agent for cultural context
        try:
            result = run_async(agent_manager.get_cultural_context(
                country=country,
                business_context=business_context,
                communication_type=communication_type
            ))
            
            if result.get('success'):
                return jsonify({
                    'cultural_context': result['data']['cultural_context'],
                    'country': country,
                    'business_context': business_context
                }), 200
            else:
                return jsonify({
                    'error': 'Cultural context analysis failed',
                    'details': result.get('error', 'Unknown error')
                }), 500
                
        except Exception as e:
            return jsonify({
                'error': 'Cultural context service error',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': 'Cultural context request failed', 'details': str(e)}), 500

@chat_bp.route('/voice/session', methods=['POST'])
@jwt_required()
def create_voice_session():
    """Create a new voice session for real-time communication"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        session_id = data.get('session_id', f"voice_{current_user_id}_{datetime.utcnow().timestamp()}")
        config = data.get('config', {})
        
        # Default voice configuration
        default_config = {
            'voice': 'alloy',
            'translation_enabled': False,
            'target_language': 'en',
            'source_language': 'auto'
        }
        
        # Merge with user config
        voice_config = {**default_config, **config}
        
        # Store session info (this would typically be handled by WebSocket)
        return jsonify({
            'session_id': session_id,
            'config': voice_config,
            'message': 'Voice session configuration created. Connect via WebSocket to start.',
            'websocket_events': {
                'start_session': 'start_voice_session',
                'send_audio': 'voice_audio_data',
                'end_session': 'end_voice_session'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Voice session creation failed', 'details': str(e)}), 500

@chat_bp.route('/websocket/info', methods=['GET'])
@jwt_required()
def get_websocket_info():
    """Get WebSocket connection information"""
    try:
        # Get WebSocket handler from app context
        ws_handler = getattr(current_app, 'ws_handler', None)
        
        if ws_handler:
            connected_users = ws_handler.get_connected_users()
            return jsonify({
                'websocket_url': '/socket.io/',
                'connected_users': connected_users,
                'events': {
                    'connect': 'Authenticate and connect to WebSocket',
                    'join_conversation': 'Join a conversation room',
                    'send_message': 'Send real-time message',
                    'start_voice_session': 'Start voice communication',
                    'voice_audio_data': 'Send voice audio data',
                    'typing': 'Send typing indicator'
                }
            }), 200
        else:
            return jsonify({
                'error': 'WebSocket handler not available'
            }), 503
        
    except Exception as e:
        return jsonify({'error': 'WebSocket info failed', 'details': str(e)}), 500

@chat_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get message and verify user is the receiver
        message = Message.query.filter_by(
            id=message_id,
            receiver_id=current_user_id
        ).first()
        
        if not message:
            return jsonify({'error': 'Message not found or access denied'}), 404
        
        message.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Message marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark message as read', 'details': str(e)}), 500

@chat_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get total unread message count for user"""
    try:
        current_user_id = get_jwt_identity()
        
        unread_count = Message.query.filter_by(
            receiver_id=current_user_id,
            is_read=False
        ).count()
        
        return jsonify({
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get unread count', 'details': str(e)}), 500

@chat_bp.route('/search', methods=['POST'])
@jwt_required()
def search_messages():
    """Search messages in user's conversations"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        query_text = data.get('query', '').strip()
        if not query_text:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Search in messages where user is sender or receiver
        messages = Message.query.filter(
            and_(
                or_(
                    Message.sender_id == current_user_id,
                    Message.receiver_id == current_user_id
                ),
                Message.content.ilike(f'%{query_text}%')
            )
        ).order_by(Message.created_at.desc()).limit(50).all()
        
        return jsonify({
            'messages': [message.to_dict() for message in messages],
            'query': query_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Message search failed', 'details': str(e)}), 500

