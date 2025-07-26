import json
import asyncio
from datetime import datetime
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from src.models.user import db, User, Message
from src.agents import agent_manager
from .voice_handler import voice_handler

class WebSocketHandler:
    """Handles WebSocket connections and real-time communication"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected_users = {}  # user_id -> socket_id mapping
        self.user_rooms = {}  # user_id -> list of rooms
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect(auth):
            """Handle client connection"""
            try:
                # Authenticate user using JWT token
                if not auth or 'token' not in auth:
                    print("No authentication token provided")
                    disconnect()
                    return False
                
                try:
                    # Decode JWT token
                    decoded_token = decode_token(auth['token'])
                    user_id = decoded_token['sub']
                    
                    # Get user from database
                    user = User.query.get(user_id)
                    if not user or not user.is_active:
                        print(f"User {user_id} not found or inactive")
                        disconnect()
                        return False
                    
                    # Store connection
                    from flask import request
                    socket_id = request.sid
                    self.connected_users[user_id] = socket_id
                    
                    # Join user to their personal room
                    join_room(f"user_{user_id}")
                    
                    # Initialize user rooms list
                    if user_id not in self.user_rooms:
                        self.user_rooms[user_id] = []
                    
                    print(f"User {user_id} connected with socket {socket_id}")
                    
                    # Send connection confirmation
                    emit('connected', {
                        'message': 'Connected successfully',
                        'user_id': user_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    return True
                    
                except Exception as e:
                    print(f"Authentication error: {str(e)}")
                    disconnect()
                    return False
                    
            except Exception as e:
                print(f"Connection error: {str(e)}")
                disconnect()
                return False
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            try:
                from flask import request
                socket_id = request.sid
                
                # Find and remove user from connected users
                user_id = None
                for uid, sid in self.connected_users.items():
                    if sid == socket_id:
                        user_id = uid
                        break
                
                if user_id:
                    # Leave all rooms
                    if user_id in self.user_rooms:
                        for room in self.user_rooms[user_id]:
                            leave_room(room)
                        del self.user_rooms[user_id]
                    
                    # Remove from connected users
                    del self.connected_users[user_id]
                    
                    print(f"User {user_id} disconnected")
                
            except Exception as e:
                print(f"Disconnect error: {str(e)}")
        
        @self.socketio.on('join_conversation')
        def handle_join_conversation(data):
            """Handle joining a conversation room"""
            try:
                conversation_id = data.get('conversation_id')
                if not conversation_id:
                    emit('error', {'message': 'conversation_id is required'})
                    return
                
                # Get current user
                user_id = self._get_current_user_id()
                if not user_id:
                    emit('error', {'message': 'Authentication required'})
                    return
                
                # Verify user is part of this conversation
                message = Message.query.filter(
                    Message.conversation_id == conversation_id,
                    (Message.sender_id == user_id) | (Message.receiver_id == user_id)
                ).first()
                
                if not message:
                    emit('error', {'message': 'Access denied to this conversation'})
                    return
                
                # Join conversation room
                room_name = f"conversation_{conversation_id}"
                join_room(room_name)
                
                # Add to user's rooms
                if user_id not in self.user_rooms:
                    self.user_rooms[user_id] = []
                if room_name not in self.user_rooms[user_id]:
                    self.user_rooms[user_id].append(room_name)
                
                emit('joined_conversation', {
                    'conversation_id': conversation_id,
                    'message': 'Joined conversation successfully'
                })
                
                print(f"User {user_id} joined conversation {conversation_id}")
                
            except Exception as e:
                emit('error', {'message': f'Failed to join conversation: {str(e)}'})
        
        @self.socketio.on('leave_conversation')
        def handle_leave_conversation(data):
            """Handle leaving a conversation room"""
            try:
                conversation_id = data.get('conversation_id')
                if not conversation_id:
                    emit('error', {'message': 'conversation_id is required'})
                    return
                
                user_id = self._get_current_user_id()
                if not user_id:
                    return
                
                # Leave conversation room
                room_name = f"conversation_{conversation_id}"
                leave_room(room_name)
                
                # Remove from user's rooms
                if user_id in self.user_rooms and room_name in self.user_rooms[user_id]:
                    self.user_rooms[user_id].remove(room_name)
                
                emit('left_conversation', {
                    'conversation_id': conversation_id,
                    'message': 'Left conversation successfully'
                })
                
            except Exception as e:
                emit('error', {'message': f'Failed to leave conversation: {str(e)}'})
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """Handle sending a real-time message"""
            try:
                user_id = self._get_current_user_id()
                if not user_id:
                    emit('error', {'message': 'Authentication required'})
                    return
                
                # Validate required fields
                required_fields = ['conversation_id', 'receiver_id', 'content']
                for field in required_fields:
                    if not data.get(field):
                        emit('error', {'message': f'{field} is required'})
                        return
                
                conversation_id = data['conversation_id']
                receiver_id = data['receiver_id']
                content = data['content']
                message_type = data.get('message_type', 'text')
                
                # Create message in database
                message = Message(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    message_type=message_type,
                    content=content,
                    media_url=data.get('media_url', '')
                )
                
                # Handle translation if needed
                sender = User.query.get(user_id)
                receiver = User.query.get(receiver_id)
                
                if sender and receiver and sender.language != receiver.language:
                    # Translate message
                    def run_translation():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            return loop.run_until_complete(
                                agent_manager.translate_chat_message(
                                    content, sender.language, receiver.language
                                )
                            )
                        except Exception as e:
                            print(f"Translation error: {str(e)}")
                            return {'original': content, 'translated': content, 'needs_translation': False}
                    
                    translation_result = run_translation()
                    
                    if translation_result.get('needs_translation'):
                        message.set_translated_content({
                            receiver.language: translation_result.get('translated', content)
                        })
                
                db.session.add(message)
                db.session.commit()
                
                # Prepare message data
                message_data = message.to_dict()
                
                # Send to conversation room
                room_name = f"conversation_{conversation_id}"
                self.socketio.emit('new_message', message_data, room=room_name)
                
                # Send confirmation to sender
                emit('message_sent', {
                    'message_id': message.id,
                    'conversation_id': conversation_id,
                    'timestamp': message.created_at.isoformat()
                })
                
                print(f"Message sent from user {user_id} to conversation {conversation_id}")
                
            except Exception as e:
                db.session.rollback()
                emit('error', {'message': f'Failed to send message: {str(e)}'})
        
        @self.socketio.on('start_voice_session')
        def handle_start_voice_session(data):
            """Handle starting a voice session"""
            try:
                user_id = self._get_current_user_id()
                if not user_id:
                    emit('error', {'message': 'Authentication required'})
                    return
                
                session_id = data.get('session_id', f"voice_{user_id}_{datetime.utcnow().timestamp()}")
                config = data.get('config', {})
                
                # Start voice session
                def run_voice_start():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        return loop.run_until_complete(
                            voice_handler.start_voice_session(session_id, user_id, config)
                        )
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                result = run_voice_start()
                
                if result.get('success'):
                    emit('voice_session_started', {
                        'session_id': session_id,
                        'config': result.get('config', {}),
                        'message': 'Voice session started successfully'
                    })
                else:
                    emit('error', {'message': result.get('error', 'Failed to start voice session')})
                
            except Exception as e:
                emit('error', {'message': f'Voice session error: {str(e)}'})
        
        @self.socketio.on('voice_audio_data')
        def handle_voice_audio_data(data):
            """Handle incoming voice audio data"""
            try:
                user_id = self._get_current_user_id()
                if not user_id:
                    emit('error', {'message': 'Authentication required'})
                    return
                
                session_id = data.get('session_id')
                audio_data = data.get('audio_data')  # Base64 encoded audio
                
                if not session_id or not audio_data:
                    emit('error', {'message': 'session_id and audio_data are required'})
                    return
                
                # Decode audio data
                import base64
                try:
                    audio_bytes = base64.b64decode(audio_data)
                except Exception as e:
                    emit('error', {'message': 'Invalid audio data format'})
                    return
                
                # Process audio with voice handler
                def run_voice_processing():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        return loop.run_until_complete(
                            voice_handler.process_audio_input(session_id, audio_bytes)
                        )
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                result = run_voice_processing()
                
                if result.get('success'):
                    emit('voice_response', {
                        'session_id': session_id,
                        'transcription': result.get('transcription'),
                        'translated_text': result.get('translated_text'),
                        'response_text': result.get('response_text'),
                        'response_audio': result.get('response_audio'),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    emit('error', {'message': result.get('error', 'Voice processing failed')})
                
            except Exception as e:
                emit('error', {'message': f'Voice processing error: {str(e)}'})
        
        @self.socketio.on('end_voice_session')
        def handle_end_voice_session(data):
            """Handle ending a voice session"""
            try:
                session_id = data.get('session_id')
                if not session_id:
                    emit('error', {'message': 'session_id is required'})
                    return
                
                # End voice session
                def run_voice_end():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        return loop.run_until_complete(
                            voice_handler.end_voice_session(session_id)
                        )
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                result = run_voice_end()
                
                if result.get('success'):
                    emit('voice_session_ended', {
                        'session_id': session_id,
                        'message': 'Voice session ended successfully'
                    })
                else:
                    emit('error', {'message': result.get('error', 'Failed to end voice session')})
                
            except Exception as e:
                emit('error', {'message': f'Voice session error: {str(e)}'})
        
        @self.socketio.on('typing')
        def handle_typing(data):
            """Handle typing indicator"""
            try:
                user_id = self._get_current_user_id()
                if not user_id:
                    return
                
                conversation_id = data.get('conversation_id')
                is_typing = data.get('is_typing', False)
                
                if not conversation_id:
                    return
                
                # Send typing indicator to conversation room
                room_name = f"conversation_{conversation_id}"
                self.socketio.emit('user_typing', {
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'is_typing': is_typing,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room_name, include_self=False)
                
            except Exception as e:
                print(f"Typing indicator error: {str(e)}")
    
    def _get_current_user_id(self):
        """Get current user ID from socket session"""
        try:
            from flask import request
            socket_id = request.sid
            
            for user_id, sid in self.connected_users.items():
                if sid == socket_id:
                    return user_id
            return None
        except:
            return None
    
    def send_notification_to_user(self, user_id: int, notification: dict):
        """Send notification to a specific user"""
        try:
            if user_id in self.connected_users:
                self.socketio.emit('notification', notification, room=f"user_{user_id}")
                return True
            return False
        except Exception as e:
            print(f"Notification error: {str(e)}")
            return False
    
    def get_connected_users(self):
        """Get list of connected users"""
        return {
            'total_connected': len(self.connected_users),
            'users': list(self.connected_users.keys())
        }


def initialize_websocket_handlers(socketio):
    """Initialize WebSocket handlers"""
    return WebSocketHandler(socketio)

