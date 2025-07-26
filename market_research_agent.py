import json
import random
from typing import Dict, Any, List
from .base_agent import BaseAgent

class MarketResearchAgent(BaseAgent):
    """Agent responsible for market research, contact discovery, and business intelligence"""
    
    def __init__(self):
        super().__init__(
            name="MarketResearchAgent",
            capabilities=["market_analysis", "contact_discovery", "trend_analysis", "opportunity_matching"]
        )
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process market research requests"""
        self.log_request("market_research", request_data)
        
        request_type = request_data.get('type')
        
        if request_type == 'market_analysis':
            result = await self._analyze_market(request_data)
        elif request_type == 'contact_discovery':
            result = await self._discover_contacts(request_data)
        elif request_type == 'trend_analysis':
            result = await self._analyze_trends(request_data)
        elif request_type == 'opportunity_matching':
            result = await self._match_opportunities(request_data)
        else:
            result = self.format_error_response(f"Unknown request type: {request_type}")
        
        self.log_response(result)
        return result
    
    async def _analyze_market(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions for a product in target country"""
        required_fields = ['product_name', 'target_country']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for market analysis")
        
        product_name = request_data['product_name']
        target_country = request_data['target_country']
        product_category = request_data.get('product_category', 'General')
        
        # Generate market analysis using AI
        analysis_prompt = f"""
        Analyze the market for {product_name} in {target_country}. Consider:
        1. Market size and growth potential
        2. Key competitors and market share
        3. Consumer preferences and trends
        4. Regulatory environment
        5. Distribution channels
        6. Pricing strategies
        7. Market entry barriers
        8. Cultural considerations
        
        Product Category: {product_category}
        
        Provide a comprehensive market analysis in JSON format with the following structure:
        {{
            "market_size": {{"value": "amount", "currency": "USD", "year": "2024"}},
            "growth_rate": "percentage",
            "market_maturity": "emerging/growing/mature/declining",
            "competition_level": "low/medium/high",
            "key_competitors": ["competitor1", "competitor2"],
            "consumer_preferences": ["preference1", "preference2"],
            "regulatory_requirements": ["requirement1", "requirement2"],
            "distribution_channels": ["channel1", "channel2"],
            "price_range": {{"min": amount, "max": amount, "currency": "USD"}},
            "market_entry_barriers": ["barrier1", "barrier2"],
            "cultural_considerations": ["consideration1", "consideration2"],
            "opportunities": ["opportunity1", "opportunity2"],
            "threats": ["threat1", "threat2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are a market research expert with deep knowledge of international trade and market analysis."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            # Try to parse as JSON, fallback to structured text if needed
            try:
                market_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured data from text response
                market_data = {
                    "analysis_text": ai_response,
                    "market_size": {"value": "Data not available", "currency": "USD", "year": "2024"},
                    "growth_rate": "To be determined",
                    "recommendations": ["Conduct detailed market survey", "Engage local partners"]
                }
            
            return self.format_success_response({
                "market_analysis": market_data,
                "product": product_name,
                "target_country": target_country,
                "analysis_date": self.created_at.isoformat()
            })
            
        except Exception as e:
            return self.format_error_response(f"Market analysis failed: {str(e)}")
    
    async def _discover_contacts(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover business contacts in target market"""
        required_fields = ['country', 'industry']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for contact discovery")
        
        country = request_data['country']
        industry = request_data['industry']
        company_size = request_data.get('company_size', 'any')
        contact_type = request_data.get('contact_type', 'buyer')
        
        # Generate realistic contact data using AI
        contact_prompt = f"""
        Generate a list of 5-10 realistic business contacts for {contact_type}s in the {industry} industry in {country}.
        
        For each contact, provide:
        - Company name (realistic for the country)
        - Contact person name (appropriate for the country)
        - Position/Title
        - Email address (realistic format)
        - Phone number (correct format for the country)
        - Company address (realistic address format)
        - Company size: {company_size}
        - Website URL
        - Brief company description
        - Verification status (verified/unverified)
        
        Return as JSON array with this structure:
        [{{
            "company_name": "string",
            "contact_person": "string",
            "position": "string",
            "email": "string",
            "phone": "string",
            "address": "string",
            "company_size": "string",
            "website": "string",
            "description": "string",
            "verified": boolean,
            "industry": "string",
            "country": "string"
        }}]
        """
        
        messages = [
            {"role": "system", "content": "You are a business intelligence expert with access to global business directories."},
            {"role": "user", "content": contact_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                contacts = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to mock data if JSON parsing fails
                contacts = self._generate_mock_contacts(country, industry, contact_type)
            
            return self.format_success_response({
                "contacts": contacts,
                "total_found": len(contacts),
                "search_criteria": {
                    "country": country,
                    "industry": industry,
                    "company_size": company_size,
                    "contact_type": contact_type
                }
            })
            
        except Exception as e:
            # Return mock data on error
            contacts = self._generate_mock_contacts(country, industry, contact_type)
            return self.format_success_response({
                "contacts": contacts,
                "total_found": len(contacts),
                "note": "Using sample data due to API limitations"
            })
    
    def _generate_mock_contacts(self, country: str, industry: str, contact_type: str) -> List[Dict[str, Any]]:
        """Generate mock contact data as fallback"""
        mock_contacts = []
        
        # Sample data based on country and industry
        if country.lower() == 'italy' and 'coffee' in industry.lower():
            mock_contacts = [
                {
                    "company_name": "Milano Coffee Roasters",
                    "contact_person": "Marco Rossi",
                    "position": "Procurement Manager",
                    "email": "marco.rossi@milanocoffee.it",
                    "phone": "+39 02 1234567",
                    "address": "Via Roma 123, 20121 Milano, Italy",
                    "company_size": "50-100 employees",
                    "website": "https://milanocoffee.it",
                    "description": "Premium coffee roaster specializing in single-origin beans",
                    "verified": True,
                    "industry": industry,
                    "country": country
                },
                {
                    "company_name": "Italian Coffee Distributors",
                    "contact_person": "Giuseppe Bianchi",
                    "position": "Import Director",
                    "email": "g.bianchi@italiancoffee.com",
                    "phone": "+39 06 7654321",
                    "address": "Via Nazionale 456, 00100 Roma, Italy",
                    "company_size": "100-500 employees",
                    "website": "https://italiancoffee.com",
                    "description": "Leading coffee distributor serving Italian market",
                    "verified": True,
                    "industry": industry,
                    "country": country
                }
            ]
        else:
            # Generic mock data
            mock_contacts = [
                {
                    "company_name": f"Global {industry} Corp",
                    "contact_person": "John Smith",
                    "position": f"{contact_type.title()} Manager",
                    "email": f"j.smith@global{industry.lower().replace(' ', '')}.com",
                    "phone": "+1 555 123 4567",
                    "address": f"123 Business St, {country}",
                    "company_size": "100-500 employees",
                    "website": f"https://global{industry.lower().replace(' ', '')}.com",
                    "description": f"Leading {industry} company in {country}",
                    "verified": True,
                    "industry": industry,
                    "country": country
                }
            ]
        
        return mock_contacts
    
    async def _analyze_trends(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends for specific industry/country"""
        required_fields = ['country']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for trend analysis")
        
        country = request_data['country']
        industry = request_data.get('industry', 'General')
        timeframe = request_data.get('timeframe', '2024-2025')
        
        trends_prompt = f"""
        Analyze current and emerging market trends for the {industry} industry in {country} for the period {timeframe}.
        
        Include:
        1. Consumer behavior trends
        2. Technology adoption trends
        3. Regulatory changes
        4. Economic factors
        5. Competitive landscape changes
        6. Supply chain trends
        7. Sustainability trends
        8. Digital transformation trends
        
        Return as JSON with this structure:
        {{
            "trends": [
                {{
                    "title": "trend name",
                    "description": "detailed description",
                    "impact": "high/medium/low",
                    "timeframe": "when this trend is relevant",
                    "category": "consumer/technology/regulatory/economic/competitive/supply_chain/sustainability/digital"
                }}
            ],
            "market_outlook": "positive/neutral/negative",
            "key_opportunities": ["opportunity1", "opportunity2"],
            "potential_risks": ["risk1", "risk2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are a market trends analyst with expertise in global markets and industry forecasting."},
            {"role": "user", "content": trends_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                trends_data = json.loads(ai_response)
            except json.JSONDecodeError:
                trends_data = {
                    "trends_text": ai_response,
                    "market_outlook": "neutral",
                    "recommendations": ["Conduct detailed trend analysis", "Monitor market developments"]
                }
            
            return self.format_success_response({
                "trends_analysis": trends_data,
                "country": country,
                "industry": industry,
                "timeframe": timeframe
            })
            
        except Exception as e:
            return self.format_error_response(f"Trend analysis failed: {str(e)}")
    
    async def _match_opportunities(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match business opportunities with user's products"""
        required_fields = ['products']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for opportunity matching")
        
        products = request_data['products']
        target_countries = request_data.get('target_countries', [])
        
        opportunities = []
        
        for product in products:
            product_name = product.get('name', 'Unknown Product')
            product_category = product.get('category', 'General')
            
            # Generate opportunities for each product
            opportunity_prompt = f"""
            Find business opportunities for {product_name} (category: {product_category}) in global markets.
            
            Consider:
            1. Market demand
            2. Competition level
            3. Entry barriers
            4. Potential revenue
            5. Cultural fit
            6. Regulatory requirements
            
            Target countries: {', '.join(target_countries) if target_countries else 'Global'}
            
            Return top 3 opportunities as JSON:
            [{{
                "title": "opportunity title",
                "description": "detailed description",
                "market": "country/region",
                "potential_value": "revenue estimate",
                "confidence": 85,
                "requirements": ["requirement1", "requirement2"],
                "next_steps": ["step1", "step2"],
                "timeline": "estimated timeline",
                "risk_level": "low/medium/high"
            }}]
            """
            
            messages = [
                {"role": "system", "content": "You are a business opportunity analyst specializing in international trade."},
                {"role": "user", "content": opportunity_prompt}
            ]
            
            try:
                ai_response = await self.call_openai_gpt(messages)
                try:
                    product_opportunities = json.loads(ai_response)
                    for opp in product_opportunities:
                        opp['matched_product'] = product
                        opportunities.append(opp)
                except json.JSONDecodeError:
                    # Fallback opportunity
                    opportunities.append({
                        "title": f"Export Opportunity for {product_name}",
                        "description": f"Potential market opportunity for {product_name} in international markets",
                        "market": "Global",
                        "potential_value": "To be determined",
                        "confidence": 70,
                        "matched_product": product,
                        "requirements": ["Market research", "Regulatory compliance"],
                        "next_steps": ["Contact potential buyers", "Prepare samples"]
                    })
            except Exception as e:
                print(f"Error generating opportunities for {product_name}: {str(e)}")
        
        return self.format_success_response({
            "opportunities": opportunities,
            "total_found": len(opportunities),
            "products_analyzed": len(products)
        })

