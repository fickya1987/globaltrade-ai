import asyncio
import json
import base64
from typing import Dict, Any, Optional
from openai import OpenAI
from src.agents import agent_manager

class VoiceHandler:
    """Handles voice communication using OpenAI Realtime API"""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.active_sessions = {}  # Store active voice sessions
        
    async def start_voice_session(self, session_id: str, user_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new voice session"""
        try:
            # Configuration for OpenAI Realtime API
            session_config = {
                'model': 'gpt-4o-realtime-preview',
                'voice': config.get('voice', 'alloy'),
                'input_audio_format': 'pcm16',
                'output_audio_format': 'pcm16',
                'input_audio_transcription': {
                    'model': 'whisper-1'
                },
                'turn_detection': {
                    'type': 'server_vad',
                    'threshold': 0.5,
                    'prefix_padding_ms': 300,
                    'silence_duration_ms': 200
                },
                'tools': [],
                'temperature': 0.8,
                'max_response_output_tokens': 4096
            }
            
            # Store session info
            self.active_sessions[session_id] = {
                'user_id': user_id,
                'config': session_config,
                'status': 'active',
                'created_at': asyncio.get_event_loop().time(),
                'translation_enabled': config.get('translation_enabled', False),
                'target_language': config.get('target_language', 'en'),
                'source_language': config.get('source_language', 'auto')
            }
            
            return {
                'success': True,
                'session_id': session_id,
                'config': session_config,
                'message': 'Voice session started successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start voice session: {str(e)}'
            }
    
    async def process_audio_input(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Process incoming audio data"""
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
            
            session = self.active_sessions[session_id]
            
            # Convert audio to base64 for OpenAI API
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # In a real implementation, this would use the OpenAI Realtime API
            # For now, we'll simulate the process with Whisper for transcription
            
            # Transcribe audio using Whisper
            transcription = await self._transcribe_audio(audio_data)
            
            if not transcription:
                return {
                    'success': False,
                    'error': 'Failed to transcribe audio'
                }
            
            # Process with translation if enabled
            if session['translation_enabled']:
                translation_result = await agent_manager.translate_text(
                    text=transcription,
                    target_language=session['target_language'],
                    source_language=session['source_language'],
                    context='voice_chat'
                )
                
                if translation_result.get('success'):
                    translated_text = translation_result['data']['translated_text']
                else:
                    translated_text = transcription
            else:
                translated_text = transcription
            
            # Generate response using GPT
            response_text = await self._generate_voice_response(translated_text, session)
            
            # Convert response to speech
            response_audio = await self._text_to_speech(response_text, session['config']['voice'])
            
            return {
                'success': True,
                'transcription': transcription,
                'translated_text': translated_text if session['translation_enabled'] else None,
                'response_text': response_text,
                'response_audio': base64.b64encode(response_audio).decode('utf-8') if response_audio else None,
                'session_id': session_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process audio: {str(e)}'
            }
    
    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Save audio data to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Use OpenAI Whisper API
                with open(temp_file_path, 'rb') as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                return transcript
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return None
    
    async def _generate_voice_response(self, text: str, session: Dict[str, Any]) -> str:
        """Generate response text using GPT"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant for international business communication. Provide clear, concise, and professional responses suitable for voice conversation. Keep responses conversational and under 100 words."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Response generation error: {str(e)}")
            return "I'm sorry, I couldn't process your request at the moment."
    
    async def _text_to_speech(self, text: str, voice: str = 'alloy') -> Optional[bytes]:
        """Convert text to speech using OpenAI TTS"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="wav"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Text-to-speech error: {str(e)}")
            return None
    
    async def end_voice_session(self, session_id: str) -> Dict[str, Any]:
        """End a voice session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return {
                    'success': True,
                    'message': 'Voice session ended successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to end session: {str(e)}'
            }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a voice session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                'session_id': session_id,
                'status': session['status'],
                'user_id': session['user_id'],
                'translation_enabled': session['translation_enabled'],
                'target_language': session['target_language'],
                'created_at': session['created_at']
            }
        else:
            return {
                'session_id': session_id,
                'status': 'not_found'
            }
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active voice sessions"""
        return {
            'total_sessions': len(self.active_sessions),
            'sessions': [
                self.get_session_status(session_id) 
                for session_id in self.active_sessions.keys()
            ]
        }


# Global voice handler instance
voice_handler = VoiceHandler()

