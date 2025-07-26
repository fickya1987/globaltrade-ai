import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from openai import OpenAI
import requests
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all AI agents in the system"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.openai_client = OpenAI()
        self.created_at = datetime.utcnow()
        self.request_count = 0
        
    @abstractmethod
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return results"""
        pass
    
    def log_request(self, request_type: str, data: Dict[str, Any]):
        """Log agent request for monitoring"""
        self.request_count += 1
        print(f"[{self.name}] Processing {request_type} request #{self.request_count}")
        print(f"[{self.name}] Request data: {json.dumps(data, indent=2)}")
    
    def log_response(self, response: Dict[str, Any]):
        """Log agent response for monitoring"""
        print(f"[{self.name}] Response: {json.dumps(response, indent=2)}")
    
    async def call_openai_gpt(self, messages: List[Dict[str, str]], model: str = "gpt-4") -> str:
        """Call OpenAI GPT API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[{self.name}] OpenAI API error: {str(e)}")
            return f"Error: Unable to process request - {str(e)}"
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web for information (mock implementation)"""
        # In a real implementation, this would use a search API like Google Custom Search
        mock_results = [
            {
                'title': f'Search result for: {query}',
                'url': f'https://example.com/search/{query.replace(" ", "-")}',
                'snippet': f'This is a mock search result for the query: {query}. In a real implementation, this would contain actual search results from a search engine API.'
            }
        ]
        return mock_results[:num_results]
    
    async def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        """Translate text using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text from {source_language} to {target_language}. Only return the translated text, no explanations."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            return await self.call_openai_gpt(messages)
        except Exception as e:
            print(f"[{self.name}] Translation error: {str(e)}")
            return text  # Return original text if translation fails
    
    def validate_request(self, request_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that request contains required fields"""
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                print(f"[{self.name}] Missing required field: {field}")
                return False
        return True
    
    def format_error_response(self, error_message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'error': error_message,
            'agent': self.name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def format_success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format success response"""
        return {
            'success': True,
            'data': data,
            'agent': self.name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def communicate_with_agent(self, agent_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with another agent (to be implemented with message bus)"""
        # This would be implemented with Redis pub/sub or similar message bus
        print(f"[{self.name}] Sending message to {agent_name}: {message}")
        return {'status': 'message_sent'}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            'name': self.name,
            'capabilities': self.capabilities,
            'created_at': self.created_at.isoformat(),
            'request_count': self.request_count,
            'status': 'active'
        }


class AgentOrchestrator:
    """Orchestrates multiple agents and manages their interactions"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.request_queue = asyncio.Queue()
        self.running = False
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        print(f"[Orchestrator] Registered agent: {agent.name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    async def route_request(self, agent_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to a specific agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {
                'success': False,
                'error': f'Agent {agent_name} not found',
                'available_agents': list(self.agents.keys())
            }
        
        try:
            result = await agent.process_request(request_data)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Agent {agent_name} failed to process request: {str(e)}',
                'agent': agent_name
            }
    
    async def broadcast_request(self, request_data: Dict[str, Any], agent_capabilities: List[str]) -> Dict[str, Any]:
        """Broadcast a request to all agents with specific capabilities"""
        matching_agents = [
            agent for agent in self.agents.values()
            if any(cap in agent.capabilities for cap in agent_capabilities)
        ]
        
        if not matching_agents:
            return {
                'success': False,
                'error': f'No agents found with capabilities: {agent_capabilities}'
            }
        
        results = {}
        for agent in matching_agents:
            try:
                result = await agent.process_request(request_data)
                results[agent.name] = result
            except Exception as e:
                results[agent.name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'success': True,
            'results': results,
            'agents_contacted': len(matching_agents)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'orchestrator_status': 'active' if self.running else 'inactive',
            'total_agents': len(self.agents),
            'agents': {name: agent.get_agent_info() for name, agent in self.agents.items()},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        print("[Orchestrator] Started successfully")
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        print("[Orchestrator] Stopped")


# Global orchestrator instance
orchestrator = AgentOrchestrator()

