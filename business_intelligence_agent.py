import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class BusinessIntelligenceAgent(BaseAgent):
    """Agent responsible for business analytics, insights, and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="BusinessIntelligenceAgent",
            capabilities=["user_analytics", "performance_insights", "recommendations", "trend_prediction"]
        )
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process business intelligence requests"""
        self.log_request("business_intelligence", request_data)
        
        request_type = request_data.get('type')
        
        if request_type == 'user_analytics':
            result = await self._analyze_user_performance(request_data)
        elif request_type == 'product_insights':
            result = await self._analyze_product_performance(request_data)
        elif request_type == 'market_recommendations':
            result = await self._generate_market_recommendations(request_data)
        elif request_type == 'competitive_analysis':
            result = await self._analyze_competition(request_data)
        elif request_type == 'growth_opportunities':
            result = await self._identify_growth_opportunities(request_data)
        else:
            result = self.format_error_response(f"Unknown request type: {request_type}")
        
        self.log_response(result)
        return result
    
    async def _analyze_user_performance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's business performance and provide insights"""
        required_fields = ['user_id']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for user analytics")
        
        user_id = request_data['user_id']
        time_period = request_data.get('time_period', '30_days')
        
        # In a real implementation, this would query the database for user data
        # For now, we'll generate mock analytics
        
        analytics_prompt = f"""
        Generate business performance analytics for a user in an export business platform.
        
        Time period: {time_period}
        
        Create realistic analytics including:
        1. Profile completion score
        2. Product listing performance
        3. Message response rate
        4. Market research activity
        5. Business connections made
        6. Engagement metrics
        7. Areas for improvement
        8. Success indicators
        
        Return as JSON:
        {{
            "performance_score": 85,
            "profile_completion": 90,
            "product_views": 1250,
            "message_response_rate": 85,
            "connections_made": 15,
            "market_research_requests": 5,
            "engagement_score": 78,
            "strengths": ["strength1", "strength2"],
            "improvement_areas": ["area1", "area2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "trends": {{
                "views_trend": "increasing",
                "connections_trend": "stable",
                "response_rate_trend": "improving"
            }},
            "benchmarks": {{
                "industry_average_views": 800,
                "industry_average_response_rate": 75,
                "industry_average_connections": 10
            }}
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a business analytics expert specializing in export business performance metrics."
            },
            {"role": "user", "content": analytics_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                analytics_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback analytics data
                analytics_data = {
                    "performance_score": 75,
                    "profile_completion": 80,
                    "recommendations": ["Complete your business profile", "Add more product photos", "Respond to messages faster"],
                    "analysis_text": ai_response
                }
            
            return self.format_success_response({
                "user_analytics": analytics_data,
                "user_id": user_id,
                "time_period": time_period,
                "generated_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return self.format_error_response(f"User analytics failed: {str(e)}")
    
    async def _analyze_product_performance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product performance and market reception"""
        required_fields = ['products']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for product insights")
        
        products = request_data['products']
        
        product_insights = []
        
        for product in products:
            product_name = product.get('name', 'Unknown Product')
            product_category = product.get('category', 'General')
            
            insights_prompt = f"""
            Analyze the market performance and potential for {product_name} in the {product_category} category.
            
            Provide insights on:
            1. Market demand level
            2. Competition intensity
            3. Price positioning
            4. Target market suitability
            5. Seasonal trends
            6. Growth potential
            7. Optimization recommendations
            
            Return as JSON:
            {{
                "demand_level": "high/medium/low",
                "competition_intensity": "high/medium/low",
                "price_competitiveness": "competitive/above_market/below_market",
                "target_markets": ["market1", "market2"],
                "seasonal_trends": "description of seasonal patterns",
                "growth_potential": "high/medium/low",
                "performance_score": 85,
                "optimization_tips": ["tip1", "tip2"],
                "market_opportunities": ["opportunity1", "opportunity2"],
                "risk_factors": ["risk1", "risk2"]
            }}
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a product market analyst with expertise in international trade and product positioning."
                },
                {"role": "user", "content": insights_prompt}
            ]
            
            try:
                ai_response = await self.call_openai_gpt(messages)
                try:
                    insight_data = json.loads(ai_response)
                    insight_data['product'] = product
                    product_insights.append(insight_data)
                except json.JSONDecodeError:
                    product_insights.append({
                        "product": product,
                        "performance_score": 70,
                        "analysis_text": ai_response,
                        "optimization_tips": ["Improve product description", "Add more images"]
                    })
            except Exception as e:
                print(f"Error analyzing product {product_name}: {str(e)}")
        
        return self.format_success_response({
            "product_insights": product_insights,
            "total_products_analyzed": len(products),
            "overall_portfolio_score": sum(p.get('performance_score', 70) for p in product_insights) / len(product_insights) if product_insights else 0
        })
    
    async def _generate_market_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized market recommendations"""
        required_fields = ['user_profile']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for market recommendations")
        
        user_profile = request_data['user_profile']
        user_country = user_profile.get('country', 'Unknown')
        user_industry = request_data.get('industry', 'General')
        
        recommendations_prompt = f"""
        Generate personalized market expansion recommendations for a business from {user_country} in the {user_industry} industry.
        
        Consider:
        1. Geographic expansion opportunities
        2. Product diversification suggestions
        3. Partnership opportunities
        4. Digital marketing strategies
        5. Trade show participation
        6. Certification requirements
        7. Funding opportunities
        8. Risk mitigation strategies
        
        Return as JSON:
        {{
            "priority_markets": [
                {{
                    "country": "country name",
                    "opportunity_score": 85,
                    "entry_difficulty": "easy/medium/hard",
                    "potential_revenue": "revenue estimate",
                    "key_requirements": ["requirement1", "requirement2"],
                    "timeline": "estimated timeline"
                }}
            ],
            "product_opportunities": [
                {{
                    "product_type": "product category",
                    "market_demand": "high/medium/low",
                    "competition_level": "low/medium/high",
                    "investment_required": "amount estimate"
                }}
            ],
            "strategic_recommendations": [
                {{
                    "category": "marketing/partnerships/certification/funding",
                    "recommendation": "specific recommendation",
                    "priority": "high/medium/low",
                    "expected_impact": "impact description",
                    "implementation_steps": ["step1", "step2"]
                }}
            ],
            "risk_factors": ["risk1", "risk2"],
            "success_metrics": ["metric1", "metric2"]
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a strategic business consultant specializing in international market expansion and export business development."
            },
            {"role": "user", "content": recommendations_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                recommendations_data = json.loads(ai_response)
            except json.JSONDecodeError:
                recommendations_data = {
                    "recommendations_text": ai_response,
                    "priority_markets": [{"country": "Global", "opportunity_score": 75}],
                    "strategic_recommendations": [{"recommendation": "Conduct market research", "priority": "high"}]
                }
            
            return self.format_success_response({
                "market_recommendations": recommendations_data,
                "user_country": user_country,
                "industry": user_industry
            })
            
        except Exception as e:
            return self.format_error_response(f"Market recommendations failed: {str(e)}")
    
    async def _analyze_competition(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        required_fields = ['industry', 'target_market']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for competitive analysis")
        
        industry = request_data['industry']
        target_market = request_data['target_market']
        
        competition_prompt = f"""
        Analyze the competitive landscape for the {industry} industry in {target_market}.
        
        Include:
        1. Key competitors and market share
        2. Competitive advantages and weaknesses
        3. Pricing strategies
        4. Distribution channels
        5. Marketing approaches
        6. Innovation trends
        7. Market gaps and opportunities
        8. Competitive threats
        
        Return as JSON:
        {{
            "market_leaders": [
                {{
                    "company": "company name",
                    "market_share": "percentage",
                    "strengths": ["strength1", "strength2"],
                    "weaknesses": ["weakness1", "weakness2"]
                }}
            ],
            "market_dynamics": {{
                "competition_intensity": "high/medium/low",
                "price_competition": "high/medium/low",
                "innovation_rate": "high/medium/low",
                "market_growth": "growing/stable/declining"
            }},
            "opportunities": [
                {{
                    "opportunity": "market gap description",
                    "potential": "high/medium/low",
                    "requirements": ["requirement1", "requirement2"]
                }}
            ],
            "threats": ["threat1", "threat2"],
            "success_factors": ["factor1", "factor2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a competitive intelligence analyst with expertise in global market analysis."
            },
            {"role": "user", "content": competition_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                competition_data = json.loads(ai_response)
            except json.JSONDecodeError:
                competition_data = {
                    "analysis_text": ai_response,
                    "market_dynamics": {"competition_intensity": "medium"},
                    "recommendations": ["Conduct detailed competitive research"]
                }
            
            return self.format_success_response({
                "competitive_analysis": competition_data,
                "industry": industry,
                "target_market": target_market
            })
            
        except Exception as e:
            return self.format_error_response(f"Competitive analysis failed: {str(e)}")
    
    async def _identify_growth_opportunities(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify growth opportunities based on user data"""
        required_fields = ['user_data']
        if not self.validate_request(request_data, required_fields):
            return self.format_error_response("Missing required fields for growth opportunities")
        
        user_data = request_data['user_data']
        current_markets = user_data.get('current_markets', [])
        products = user_data.get('products', [])
        
        growth_prompt = f"""
        Identify growth opportunities for a business with the following profile:
        
        Current markets: {', '.join(current_markets) if current_markets else 'None specified'}
        Products: {len(products)} products in portfolio
        
        Analyze opportunities in:
        1. Market expansion (new geographic markets)
        2. Product line extension
        3. Value chain integration
        4. Digital transformation
        5. Strategic partnerships
        6. Technology adoption
        7. Sustainability initiatives
        8. Customer segment expansion
        
        Return as JSON:
        {{
            "growth_opportunities": [
                {{
                    "type": "market_expansion/product_extension/partnership/digital/sustainability",
                    "title": "opportunity title",
                    "description": "detailed description",
                    "potential_impact": "high/medium/low",
                    "investment_required": "low/medium/high",
                    "timeline": "short/medium/long term",
                    "success_probability": 85,
                    "key_steps": ["step1", "step2"],
                    "risks": ["risk1", "risk2"],
                    "expected_roi": "roi estimate"
                }}
            ],
            "priority_ranking": [1, 2, 3],
            "resource_requirements": {{
                "financial": "investment estimate",
                "human": "staffing needs",
                "technology": "tech requirements",
                "time": "timeline estimate"
            }},
            "success_metrics": ["metric1", "metric2"]
        }}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a business growth strategist with expertise in international expansion and business development."
            },
            {"role": "user", "content": growth_prompt}
        ]
        
        try:
            ai_response = await self.call_openai_gpt(messages)
            try:
                growth_data = json.loads(ai_response)
            except json.JSONDecodeError:
                growth_data = {
                    "growth_analysis": ai_response,
                    "growth_opportunities": [
                        {
                            "type": "market_expansion",
                            "title": "Explore new markets",
                            "potential_impact": "high",
                            "key_steps": ["Market research", "Local partnerships"]
                        }
                    ]
                }
            
            return self.format_success_response({
                "growth_opportunities": growth_data,
                "analysis_date": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return self.format_error_response(f"Growth opportunity analysis failed: {str(e)}")
    
    async def generate_dashboard_insights(self, user_id: int) -> Dict[str, Any]:
        """Generate insights for user dashboard"""
        try:
            # This would typically query the database for user data
            # For now, we'll generate mock insights
            
            insights = {
                "performance_summary": {
                    "overall_score": 82,
                    "trend": "improving",
                    "key_metric": "Profile views increased by 25%"
                },
                "quick_wins": [
                    "Add 3 more product images to increase engagement",
                    "Respond to pending messages to improve response rate",
                    "Complete business verification to build trust"
                ],
                "market_alerts": [
                    "New trade opportunity in Italy for coffee products",
                    "Upcoming trade show in Germany relevant to your industry"
                ],
                "recommendations": [
                    {
                        "title": "Expand to European Markets",
                        "priority": "high",
                        "potential_impact": "25% revenue increase"
                    },
                    {
                        "title": "Improve Product Descriptions",
                        "priority": "medium",
                        "potential_impact": "15% more inquiries"
                    }
                ]
            }
            
            return self.format_success_response(insights)
            
        except Exception as e:
            return self.format_error_response(f"Dashboard insights generation failed: {str(e)}")

