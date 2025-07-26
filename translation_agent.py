import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class TranslationAgent(BaseAgent):
    """Agent responsible for language translation and cultural communication assistance"""
    
    def __init__(self):
        super().__init__(
            name="TranslationAgent",
            capabilities=["text_translation", "voice_translation", "cultural_context", "business_etiquette"]
        )
        
        # Language codes and names mapping
        self.supported_languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
            'id': 'Indonesian', 'th': 'Thai', 'vi': 'Vietnamese', 'tr': 'Turkish',
            'pl': 'Polish', 'nl': 'Dutch', 'sv': 'Swedish', 'da': 'Danish'
        }
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process translation and communication requests"""
        self.log_request("translation", request_data)
        
        request_type = request_data.get('type')
        
        if request_type == 'text_translation':
            result = await self._translate_text(request_data)
        elif request_type == 'batch_translation':
            result = await self._batch_translate(request_data)
        elif request_type == 'cultural_context':
            result = await self._provide_cultural_context(request_data)
        elif request_type == 'business_etiquette':
            result = await self._provide_business_etiquette(request_data)
        elif request_type == 'language_detection':
            result = await self._detect_language(request_data)
        else:
            result = self.format_error_response(f"Unknown request type: {request_type}")
        
        self.log_response(result)
        return result
    
    async def _translate_text(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text from source to target language"""
        required_fields = ['text', 'target_language']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for text translation")
        
        text = request_data['text']
        target_language = request_data['target_language']
        source_language = request_data.get('source_language', 'auto')
        context = request_data.get('context', 'general')
        
        # Validate target language
        if target_language not in self.supported_languages:
            return self.format_error_response(f"Unsupported target language: {target_language}")
        
        try:
            # Create translation prompt with context
            translation_prompt = f"""
            Translate the following text to {self.supported_languages[target_language]}.
            
            Context: {context} (This helps determine the appropriate tone and terminology)
            Source language: {source_language if source_language != 'auto' else 'auto-detect'}
            
            Text to translate: "{text}"
            
            Requirements:
            1. Maintain the original meaning and tone
            2. Use appropriate business/professional language if context is business
            3. Consider cultural nuances
            4. Preserve any technical terms appropriately
            5. Only return the translated text, no explanations
            
            Translation:
            """
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are a professional translator with expertise in business and cultural communication. Provide accurate, contextually appropriate translations."
                },
                {"role": "user", "content": translation_prompt}
            ]
            
            translated_text = await self.call_openai_gpt(messages)
            
            # Detect source language if not specified
            if source_language == 'auto':
                detected_language = await self._detect_language_internal(text)
            else:
                detected_language = source_language
            
            return self.format_success_response({
                "original_text": text,
                "translated_text": translated_text,
                "source_language": detected_language,
                "target_language": target_language,
                "context": context,
                "confidence": 0.95  # Mock confidence score
            })
            
        except Exception as e:
            return self.format_error_response(f"Translation failed: {str(e)}")
    
    async def _batch_translate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate multiple texts in batch"""
        required_fields = ['texts', 'target_language']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for batch translation")
        
        texts = request_data['texts']
        target_language = request_data['target_language']
        source_language = request_data.get('source_language', 'auto')
        
        if not isinstance(texts, list):
            return self.format_error_response("Texts must be a list")
        
        translations = []
        
        for i, text in enumerate(texts):
            try:
                translation_request = {
                    'text': text,
                    'target_language': target_language,
                    'source_language': source_language,
                    'context': request_data.get('context', 'general')
                }
                
                result = await self._translate_text(translation_request)
                
                if result['success']:
                    translations.append({
                        'index': i,
                        'original': text,
                        'translated': result['data']['translated_text'],
                        'success': True
                    })
                else:
                    translations.append({
                        'index': i,
                        'original': text,
                        'translated': text,  # Keep original on failure
                        'success': False,
                        'error': result['error']
                    })
                    
            except Exception as e:
                translations.append({
                    'index': i,
                    'original': text,
                    'translated': text,
                    'success': False,
                    'error': str(e)
                })
        
        successful_translations = sum(1 for t in translations if t['success'])
        
        return self.format_success_response({
            "translations": translations,
            "total_texts": len(texts),
            "successful_translations": successful_translations,
            "target_language": target_language
        })
    
    async def _provide_cultural_context(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide cultural context for business communication"""
        required_fields = ['country']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for cultural context")
        
        country = request_data['country']
        business_context = request_data.get('business_context', 'general')
        communication_type = request_data.get('communication_type', 'email')
        
        context_prompt = f"""
        Provide cultural context and communication guidelines for doing business in {country}.
        
        Business context: {business_context}
        Communication type: {communication_type}
        
        Include information about:
        1. Communication style (direct vs indirect)
        2. Business hierarchy and respect
        3. Time and punctuality expectations
        4. Gift-giving customs
        5. Dining and entertainment etiquette
        6. Negotiation style
        7. Common greetings and phrases
        8. Taboos and things to avoid
        9. Preferred communication channels
        10. Business card etiquette
        
        Return as JSON:
        {{
            "communication_style": "description",
            "hierarchy_respect": "guidelines",
            "time_expectations": "punctuality norms",
            "gift_customs": "gift-giving guidelines",
            "dining_etiquette": "business dining norms",
            "negotiation_style": "negotiation approach",
            "greetings": ["common greeting phrases"],
            "taboos": ["things to avoid"],
            "preferred_channels": ["communication preferences"],
            "business_card_etiquette": "business card guidelines",
            "key_phrases": {{
                "hello": "local greeting",
                "thank_you": "local thank you",
                "please": "local please",
                "excuse_me": "local excuse me"
            }},
            "tips": ["practical business tips"]
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a cultural business consultant with deep knowledge of international business practices and cultural norms."
            },
            {"role": "user", "content": context_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                cultural_data = json.loads(ai_response)
            except json.JSONDecodeError:
                cultural_data = {
                    "cultural_advice": ai_response,
                    "country": country,
                    "tips": ["Research local customs", "Be respectful of cultural differences"]
                }
            
            return self.format_success_response({
                "cultural_context": cultural_data,
                "country": country,
                "business_context": business_context,
                "communication_type": communication_type
            })
            
        except Exception as e:
            return self.format_error_response(f"Cultural context analysis failed: {str(e)}")
    
    async def _provide_business_etiquette(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide specific business etiquette guidelines"""
        required_fields = ['country', 'situation']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for business etiquette")
        
        country = request_data['country']
        situation = request_data['situation']  # e.g., 'first_meeting', 'negotiation', 'contract_signing'
        
        etiquette_prompt = f"""
        Provide specific business etiquette guidelines for {situation} in {country}.
        
        Include:
        1. Appropriate dress code
        2. Meeting preparation
        3. Greeting protocols
        4. Conversation topics (appropriate and inappropriate)
        5. Body language considerations
        6. Gift-giving if applicable
        7. Follow-up expectations
        8. Common mistakes to avoid
        
        Return as JSON:
        {{
            "dress_code": "appropriate attire",
            "preparation": ["preparation steps"],
            "greeting_protocol": "how to greet properly",
            "appropriate_topics": ["good conversation topics"],
            "topics_to_avoid": ["topics to avoid"],
            "body_language": ["body language tips"],
            "gift_giving": "gift guidelines if applicable",
            "follow_up": "follow-up expectations",
            "common_mistakes": ["mistakes to avoid"],
            "success_tips": ["tips for success"]
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a business etiquette expert with extensive knowledge of international business protocols."
            },
            {"role": "user", "content": etiquette_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                etiquette_data = json.loads(ai_response)
            except json.JSONDecodeError:
                etiquette_data = {
                    "etiquette_advice": ai_response,
                    "general_tips": ["Be respectful", "Research local customs", "Be punctual"]
                }
            
            return self.format_success_response({
                "business_etiquette": etiquette_data,
                "country": country,
                "situation": situation
            })
            
        except Exception as e:
            return self.format_error_response(f"Business etiquette analysis failed: {str(e)}")
    
    async def _detect_language(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect the language of given text"""
        required_fields = ['text']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for language detection")
        
        text = request_data['text']
        detected_language = await self._detect_language_internal(text)
        
        return self.format_success_response({
            "text": text,
            "detected_language": detected_language,
            "language_name": self.supported_languages.get(detected_language, "Unknown"),
            "confidence": 0.9  # Mock confidence score
        })
    
    async def _detect_language_internal(self, text: str) -> str:
        """Internal method to detect language"""
        detection_prompt = f"""
        Detect the language of the following text and return only the ISO 639-1 language code (e.g., 'en' for English, 'es' for Spanish, 'fr' for French, etc.).
        
        Text: "{text}"
        
        Language code:
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a language detection expert. Return only the ISO 639-1 language code, nothing else."
            },
            {"role": "user", "content": detection_prompt}
        ]
        
        try:
            detected = await self.call_openai_gpt(messages)
            detected_code = detected.strip().lower()
            
            # Validate the detected code
            if detected_code in self.supported_languages:
                return detected_code
            else:
                return 'en'  # Default to English if detection fails
                
        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return 'en'  # Default to English on error
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages
    
    async def translate_message_for_chat(self, message: str, sender_language: str, receiver_language: str) -> Dict[str, Any]:
        """Specialized method for chat message translation"""
        if sender_language == receiver_language:
            return {
                'original': message,
                'translated': message,
                'needs_translation': False
            }
        
        translation_request = {
            'type': 'text_translation',
            'text': message,
            'source_language': sender_language,
            'target_language': receiver_language,
            'context': 'business_chat'
        }
        
        result = await self.process_request(translation_request)
        
        if result['success']:
            return {
                'original': message,
                'translated': result['data']['translated_text'],
                'needs_translation': True,
                'source_language': sender_language,
                'target_language': receiver_language
            }
        else:
            return {
                'original': message,
                'translated': message,  # Keep original on failure
                'needs_translation': True,
                'error': result['error']
            }

