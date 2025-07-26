import asyncio
from typing import Dict, Any, Optional
from .base_agent import orchestrator
from .market_research_agent import MarketResearchAgent
from .translation_agent import TranslationAgent
from .business_intelligence_agent import BusinessIntelligenceAgent

class AgentManager:
    """Manages all AI agents and provides a unified interface"""
    
    def __init__(self):
        self.orchestrator = orchestrator
        self.agents_initialized = False
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize and register all agents"""
        try:
            # Create agent instances
            market_agent = MarketResearchAgent()
            translation_agent = TranslationAgent()
            business_agent = BusinessIntelligenceAgent()
            
            # Register agents with orchestrator
            self.orchestrator.register_agent(market_agent)
            self.orchestrator.register_agent(translation_agent)
            self.orchestrator.register_agent(business_agent)
            
            self.agents_initialized = True
            print("[AgentManager] All agents initialized successfully")
            
        except Exception as e:
            print(f"[AgentManager] Error initializing agents: {str(e)}")
            self.agents_initialized = False
    
    async def start_agents(self):
        """Start the agent orchestrator"""
        if not self.agents_initialized:
            self._initialize_agents()
        
        await self.orchestrator.start()
        print("[AgentManager] Agent system started")
    
    async def stop_agents(self):
        """Stop the agent orchestrator"""
        await self.orchestrator.stop()
        print("[AgentManager] Agent system stopped")
    
    # Market Research Methods
    async def analyze_market(self, product_name: str, target_country: str, product_category: str = None) -> Dict[str, Any]:
        """Analyze market for a product in target country"""
        request_data = {
            'type': 'market_analysis',
            'product_name': product_name,
            'target_country': target_country,
            'product_category': product_category or 'General'
        }
        return await self.orchestrator.route_request('MarketResearchAgent', request_data)
    
    async def discover_contacts(self, country: str, industry: str, company_size: str = 'any', contact_type: str = 'buyer') -> Dict[str, Any]:
        """Discover business contacts in target market"""
        request_data = {
            'type': 'contact_discovery',
            'country': country,
            'industry': industry,
            'company_size': company_size,
            'contact_type': contact_type
        }
        return await self.orchestrator.route_request('MarketResearchAgent', request_data)
    
    async def analyze_trends(self, country: str, industry: str = 'General', timeframe: str = '2024-2025') -> Dict[str, Any]:
        """Analyze market trends"""
        request_data = {
            'type': 'trend_analysis',
            'country': country,
            'industry': industry,
            'timeframe': timeframe
        }
        return await self.orchestrator.route_request('MarketResearchAgent', request_data)
    
    async def match_opportunities(self, products: list, target_countries: list = None) -> Dict[str, Any]:
        """Match business opportunities with products"""
        request_data = {
            'type': 'opportunity_matching',
            'products': products,
            'target_countries': target_countries or []
        }
        return await self.orchestrator.route_request('MarketResearchAgent', request_data)
    
    # Translation Methods
    async def translate_text(self, text: str, target_language: str, source_language: str = 'auto', context: str = 'general') -> Dict[str, Any]:
        """Translate text"""
        request_data = {
            'type': 'text_translation',
            'text': text,
            'target_language': target_language,
            'source_language': source_language,
            'context': context
        }
        return await self.orchestrator.route_request('TranslationAgent', request_data)
    
    async def batch_translate(self, texts: list, target_language: str, source_language: str = 'auto') -> Dict[str, Any]:
        """Batch translate multiple texts"""
        request_data = {
            'type': 'batch_translation',
            'texts': texts,
            'target_language': target_language,
            'source_language': source_language
        }
        return await self.orchestrator.route_request('TranslationAgent', request_data)
    
    async def get_cultural_context(self, country: str, business_context: str = 'general', communication_type: str = 'email') -> Dict[str, Any]:
        """Get cultural context for business communication"""
        request_data = {
            'type': 'cultural_context',
            'country': country,
            'business_context': business_context,
            'communication_type': communication_type
        }
        return await self.orchestrator.route_request('TranslationAgent', request_data)
    
    async def get_business_etiquette(self, country: str, situation: str) -> Dict[str, Any]:
        """Get business etiquette guidelines"""
        request_data = {
            'type': 'business_etiquette',
            'country': country,
            'situation': situation
        }
        return await self.orchestrator.route_request('TranslationAgent', request_data)
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        request_data = {
            'type': 'language_detection',
            'text': text
        }
        return await self.orchestrator.route_request('TranslationAgent', request_data)
    
    # Business Intelligence Methods
    async def analyze_user_performance(self, user_id: int, time_period: str = '30_days') -> Dict[str, Any]:
        """Analyze user performance"""
        request_data = {
            'type': 'user_analytics',
            'user_id': user_id,
            'time_period': time_period
        }
        return await self.orchestrator.route_request('BusinessIntelligenceAgent', request_data)
    
    async def analyze_product_performance(self, products: list) -> Dict[str, Any]:
        """Analyze product performance"""
        request_data = {
            'type': 'product_insights',
            'products': products
        }
        return await self.orchestrator.route_request('BusinessIntelligenceAgent', request_data)
    
    async def generate_market_recommendations(self, user_profile: dict, industry: str = 'General') -> Dict[str, Any]:
        """Generate market recommendations"""
        request_data = {
            'type': 'market_recommendations',
            'user_profile': user_profile,
            'industry': industry
        }
        return await self.orchestrator.route_request('BusinessIntelligenceAgent', request_data)
    
    async def analyze_competition(self, industry: str, target_market: str) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        request_data = {
            'type': 'competitive_analysis',
            'industry': industry,
            'target_market': target_market
        }
        return await self.orchestrator.route_request('BusinessIntelligenceAgent', request_data)
    
    async def identify_growth_opportunities(self, user_data: dict) -> Dict[str, Any]:
        """Identify growth opportunities"""
        request_data = {
            'type': 'growth_opportunities',
            'user_data': user_data
        }
        return await self.orchestrator.route_request('BusinessIntelligenceAgent', request_data)
    
    # Chat-specific methods
    async def translate_chat_message(self, message: str, sender_language: str, receiver_language: str) -> Dict[str, Any]:
        """Translate chat message with special handling"""
        translation_agent = self.orchestrator.get_agent('TranslationAgent')
        if translation_agent:
            return await translation_agent.translate_message_for_chat(message, sender_language, receiver_language)
        else:
            return {
                'original': message,
                'translated': message,
                'needs_translation': False,
                'error': 'Translation agent not available'
            }
    
    # System methods
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return self.orchestrator.get_system_status()
    
    def get_agent_capabilities(self) -> Dict[str, list]:
        """Get capabilities of all agents"""
        capabilities = {}
        for name, agent in self.orchestrator.agents.items():
            capabilities[name] = agent.capabilities
        return capabilities
    
    async def process_market_research_request(self, research_data: dict) -> Dict[str, Any]:
        """Process a comprehensive market research request"""
        try:
            product_name = research_data.get('product_name', 'Unknown Product')
            target_country = research_data.get('target_country', 'Global')
            product_category = research_data.get('product_category', 'General')
            
            # Run multiple analyses in parallel
            market_analysis_task = self.analyze_market(product_name, target_country, product_category)
            contacts_task = self.discover_contacts(target_country, product_category)
            trends_task = self.analyze_trends(target_country, product_category)
            
            # Wait for all analyses to complete
            market_result, contacts_result, trends_result = await asyncio.gather(
                market_analysis_task,
                contacts_task,
                trends_task,
                return_exceptions=True
            )
            
            # Compile comprehensive results
            comprehensive_result = {
                'success': True,
                'research_id': research_data.get('research_id'),
                'product_name': product_name,
                'target_country': target_country,
                'market_analysis': market_result.get('data') if isinstance(market_result, dict) and market_result.get('success') else None,
                'contacts': contacts_result.get('data') if isinstance(contacts_result, dict) and contacts_result.get('success') else None,
                'trends': trends_result.get('data') if isinstance(trends_result, dict) and trends_result.get('success') else None,
                'errors': []
            }
            
            # Collect any errors
            if isinstance(market_result, Exception) or (isinstance(market_result, dict) and not market_result.get('success')):
                comprehensive_result['errors'].append('Market analysis failed')
            
            if isinstance(contacts_result, Exception) or (isinstance(contacts_result, dict) and not contacts_result.get('success')):
                comprehensive_result['errors'].append('Contact discovery failed')
            
            if isinstance(trends_result, Exception) or (isinstance(trends_result, dict) and not trends_result.get('success')):
                comprehensive_result['errors'].append('Trend analysis failed')
            
            return comprehensive_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Comprehensive market research failed: {str(e)}',
                'research_id': research_data.get('research_id')
            }


# Global agent manager instance
agent_manager = AgentManager()

