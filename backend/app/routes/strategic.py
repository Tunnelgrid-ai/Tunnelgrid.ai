"""
Strategic Recommendations API routes
Provides advanced analytics and recommendations for brand visibility optimization
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from collections import defaultdict
import statistics

from app.core.database import get_supabase_client
from app.routes.analysis import validate_uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategic", tags=["strategic"])

# =============================================================================
# STRATEGIC RECOMMENDATION MODELS
# =============================================================================

class OpportunityGap:
    """Represents a persona-topic combination with improvement potential"""
    def __init__(self, persona_name: str, topic_name: str, current_score: int, 
                 potential_score: int, impact: str, effort: str, priority: int):
        self.persona_name = persona_name
        self.topic_name = topic_name
        self.current_score = current_score
        self.potential_score = potential_score
        self.impact = impact
        self.effort = effort
        self.priority = priority

class ContentStrategy:
    """Content strategy recommendation for a specific topic"""
    def __init__(self, topic_name: str, current_visibility: int, competitor_mentions: int,
                 recommended_action: str, target_increase: int):
        self.topic_name = topic_name
        self.current_visibility = current_visibility
        self.competitor_mentions = competitor_mentions
        self.recommended_action = recommended_action
        self.target_increase = target_increase

class CompetitiveInsight:
    """Competitive analysis insight"""
    def __init__(self, competitor_name: str, mention_count: int, 
                 strongest_topics: List[str], opportunity_areas: List[str]):
        self.competitor_name = competitor_name
        self.mention_count = mention_count
        self.strongest_topics = strongest_topics
        self.opportunity_areas = opportunity_areas

# =============================================================================
# STRATEGIC ANALYSIS ENGINE
# =============================================================================

class StrategicAnalysisEngine:
    """Advanced analytics engine for strategic recommendations"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.main_brand_keywords = ['haldiram', 'haldirams']  # Configurable
        
    def calculate_opportunity_gaps(self, audit_id: str) -> List[Dict[str, Any]]:
        """Calculate persona-topic combinations with highest improvement potential"""
        logger.info(f"📊 Calculating opportunity gaps for audit: {audit_id}")
        
        # Get all necessary data
        personas = self._get_personas(audit_id)
        topics = self._get_topics(audit_id)
        queries = self._get_queries(audit_id)
        responses = self._get_responses_for_audit(audit_id)
        brand_mentions = self._get_brand_mentions_for_audit(audit_id)
        
        gaps = []
        
        for persona in personas:
            persona_name = persona.get('persona_type', 'Unknown')
            
            for topic in topics:
                topic_name = topic.get('topic_name', 'Unknown')
                
                # Find relevant queries for this persona-topic combination
                relevant_queries = [q for q in queries 
                                  if q.get('persona') == persona.get('persona_id') 
                                  and q.get('topic_name') == topic_name]
                
                if not relevant_queries:
                    continue
                
                # Calculate current performance
                current_score = self._calculate_persona_topic_score(
                    relevant_queries, responses, brand_mentions
                )
                
                # Calculate potential score using industry benchmarks
                potential_score = self._calculate_potential_score(current_score, topic_name, persona_name)
                
                # Only include if significant improvement potential exists
                if potential_score - current_score >= 15:
                    impact = self._calculate_impact(len(relevant_queries), current_score)
                    effort = self._calculate_effort(persona_name, topic_name)
                    priority = self._calculate_priority(potential_score - current_score, impact, effort)
                    
                    gaps.append({
                        'personaName': persona_name,
                        'topicName': topic_name,
                        'currentScore': current_score,
                        'potentialScore': potential_score,
                        'impact': impact,
                        'effort': effort,
                        'priority': priority
                    })
        
        # Sort by priority (highest first)
        gaps.sort(key=lambda x: x['priority'], reverse=True)
        logger.info(f"✅ Found {len(gaps)} opportunity gaps")
        return gaps[:10]  # Return top 10
    
    def analyze_content_strategy(self, audit_id: str) -> List[Dict[str, Any]]:
        """Analyze content strategy opportunities by topic"""
        logger.info(f"📝 Analyzing content strategy for audit: {audit_id}")
        
        topics = self._get_topics(audit_id)
        queries = self._get_queries(audit_id)
        responses = self._get_responses_for_audit(audit_id)
        brand_mentions = self._get_brand_mentions_for_audit(audit_id)
        
        strategies = []
        
        for topic in topics:
            topic_name = topic.get('topic_name', 'Unknown')
            
            # Get all queries for this topic
            topic_queries = [q for q in queries if q.get('topic_name') == topic_name]
            
            if not topic_queries:
                continue
            
            # Calculate current visibility
            current_visibility = self._calculate_topic_visibility(topic_queries, responses, brand_mentions)
            
            # Count competitor mentions
            competitor_mentions = self._count_competitor_mentions(topic_queries, responses, brand_mentions)
            
            # Generate recommendation
            recommended_action = self._generate_content_recommendation(
                topic_name, current_visibility, competitor_mentions
            )
            
            # Calculate target increase
            target_increase = min(30, max(15, 70 - current_visibility))
            
            strategies.append({
                'topicName': topic_name,
                'currentVisibility': current_visibility,
                'competitorMentions': competitor_mentions,
                'recommendedAction': recommended_action,
                'targetIncrease': target_increase
            })
        
        # Sort by opportunity (competitor activity vs current visibility)
        strategies.sort(key=lambda x: (x['competitorMentions'] - x['currentVisibility']), reverse=True)
        logger.info(f"✅ Generated {len(strategies)} content strategies")
        return strategies
    
    def analyze_competitive_insights(self, audit_id: str) -> List[Dict[str, Any]]:
        """Analyze competitive landscape and opportunities using competitors table"""
        logger.info(f"⚔️ Analyzing competitive insights for audit: {audit_id}")
        
        # Get competitors directly from competitors table
        competitors_result = self.supabase.table("competitors").select("*").eq("audit_id", audit_id).order("mention_count", desc=True).execute()
        
        if hasattr(competitors_result, 'error') and competitors_result.error:
            logger.error(f"❌ Failed to fetch competitors: {competitors_result.error}")
            return []
        
        competitors = competitors_result.data or []
        logger.info(f"🏆 Found {len(competitors)} competitors in database")
        
        # Get topics for opportunity analysis
        topics = self._get_topics(audit_id)
        all_topic_names = [t.get('topic_name', 'Unknown') for t in topics]
        
        # Convert competitors to insights format
        insights = []
        for competitor in competitors:
            brand_name = competitor.get('brand_name', '').strip()
            mention_count = competitor.get('mention_count', 0)
            
            if not brand_name or mention_count < 1:  # Only include competitors with at least 1 mention
                continue
            
            # Filter out non-brand-like entries (phrases, common words, etc.)
            brand_lower = brand_name.lower()
            non_brand_keywords = ['unlike', 'some', 'other', 'use', 'both', 'the', 'convenience', 'grocery', 'delivery', 'and', 'or', 'with', 'for', 'in', 'on', 'at', 'to', 'of', 'a', 'an', 'the']
            if any(keyword in brand_lower for keyword in non_brand_keywords) and len(brand_name.split()) > 2:
                continue  # Skip phrases that are likely not brand names
            
            # For now, we'll use a simplified approach since competitors table doesn't have topic breakdown
            # In the future, we could add topic-specific competitor data to the competitors table
            
            # Generate some sample strongest topics and opportunity areas based on mention count
            # This is a placeholder - ideally the competitors table would have topic breakdown
            strongest_topics = []
            opportunity_areas = []
            
            # If we have topics, assign some based on mention count (placeholder logic)
            if all_topic_names:
                # Simple heuristic: assign topics based on mention count
                if mention_count >= 50:
                    strongest_topics = all_topic_names[:3] if len(all_topic_names) >= 3 else all_topic_names
                    opportunity_areas = all_topic_names[3:6] if len(all_topic_names) >= 6 else []
                elif mention_count >= 20:
                    strongest_topics = all_topic_names[:2] if len(all_topic_names) >= 2 else all_topic_names
                    opportunity_areas = all_topic_names[2:5] if len(all_topic_names) >= 5 else []
                else:
                    strongest_topics = all_topic_names[:1] if all_topic_names else []
                    opportunity_areas = all_topic_names[1:4] if len(all_topic_names) >= 4 else []
            
            logger.info(f"🔍 Competitor {brand_name}: {mention_count} mentions, strongest={strongest_topics}, opportunities={opportunity_areas}")
            
            insights.append({
                'competitorName': brand_name,
                'mentionCount': mention_count,
                'strongestTopics': strongest_topics,
                'opportunityAreas': opportunity_areas
            })
        
        # Sort by mention count (already sorted from database, but ensure it)
        insights.sort(key=lambda x: x['mentionCount'], reverse=True)
        logger.info(f"✅ Analyzed {len(insights)} competitors from database")
        return insights[:5]  # Top 5 competitors
    
    def calculate_overall_potential(self, audit_id: str, opportunity_gaps: List[Dict]) -> Dict[str, int]:
        """Calculate overall brand visibility potential using competitors table"""
        logger.info(f"🎯 Calculating overall potential for audit: {audit_id}")
        
        # Get current metrics from competitors table
        total_responses = len(self._get_responses_for_audit(audit_id))
        
        # Get total mentions from competitors table
        competitors_result = self.supabase.table("competitors").select("mention_count").eq("audit_id", audit_id).execute()
        if hasattr(competitors_result, 'error') and competitors_result.error:
            logger.error(f"❌ Failed to fetch competitors for potential calculation: {competitors_result.error}")
            total_mentions = 0
        else:
            competitors = competitors_result.data or []
            total_mentions = sum(comp.get('mention_count', 0) for comp in competitors)
        
        current_visibility = round((total_mentions / total_responses) * 100) if total_responses > 0 else 0
        
        # Calculate potential based on opportunity gaps
        if opportunity_gaps:
            avg_gap_increase = sum(gap['potentialScore'] - gap['currentScore'] for gap in opportunity_gaps) / len(opportunity_gaps)
            potential = min(85, current_visibility + round(avg_gap_increase * 0.6))
        else:
            potential = min(85, current_visibility + 15)  # Default improvement
        
        logger.info(f"📊 Overall potential: current={current_visibility}%, potential={potential}%, total_mentions={total_mentions}")
        
        return {
            'current': current_visibility,
            'potential': potential
        }
    
    def generate_key_recommendations(self, opportunity_gaps: List[Dict], 
                                   content_strategy: List[Dict], 
                                   competitive_insights: List[Dict]) -> List[str]:
        """Generate actionable key recommendations"""
        logger.info("💡 Generating key recommendations")
        
        recommendations = []
        
        # Top opportunity gap recommendation
        if opportunity_gaps:
            top_gap = opportunity_gaps[0]
            recommendations.append(
                f"Focus on {top_gap['personaName']} × {top_gap['topicName']} content to increase visibility by {top_gap['potentialScore'] - top_gap['currentScore']}%"
            )
        
        # Content strategy recommendation
        if content_strategy:
            top_strategy = content_strategy[0]
            recommendations.append(
                f"Strengthen presence in \"{top_strategy['topicName']}\" where competitors have {top_strategy['competitorMentions']} mentions"
            )
        
        # Competitive positioning
        if competitive_insights:
            top_competitor = competitive_insights[0]
            if top_competitor['strongestTopics']:
                recommendations.append(
                    f"Challenge {top_competitor['competitorName']}'s dominance in {top_competitor['strongestTopics'][0]} conversations"
                )
        
        # Add generic strategic recommendations
        recommendations.extend([
            "Develop persona-specific content for underperforming segments",
            "Create comparative content highlighting brand advantages",
            "Increase brand mentions in organic conversation topics"
        ])
        
        return recommendations[:6]
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _get_personas(self, audit_id: str) -> List[Dict]:
        """Get personas for audit"""
        result = self.supabase.table("personas").select("*").eq("audit_id", audit_id).execute()
        return result.data or []
    
    def _get_topics(self, audit_id: str) -> List[Dict]:
        """Get topics for audit"""
        result = self.supabase.table("topics").select("*").eq("audit_id", audit_id).execute()
        return result.data or []
    
    def _get_queries(self, audit_id: str) -> List[Dict]:
        """Get queries for audit"""
        result = self.supabase.table("queries").select("*").eq("audit_id", audit_id).execute()
        return result.data or []
    
    def _get_responses_for_audit(self, audit_id: str) -> List[Dict]:
        """Get all responses for audit"""
        queries = self._get_queries(audit_id)
        if not queries:
            return []
        
        query_ids = [q['query_id'] for q in queries]
        result = self.supabase.table("responses").select("*").in_("query_id", query_ids).execute()
        return result.data or []
    
    def _get_brand_mentions_for_audit(self, audit_id: str) -> List[Dict]:
        """Get all brand mentions for audit"""
        responses = self._get_responses_for_audit(audit_id)
        if not responses:
            return []
        
        response_ids = [r['response_id'] for r in responses]
        result = self.supabase.table("brand_mentions").select("*").in_("response_id", response_ids).execute()
        return result.data or []
    
    def _calculate_persona_topic_score(self, queries: List[Dict], responses: List[Dict], mentions: List[Dict]) -> int:
        """Calculate visibility score for persona-topic combination"""
        query_ids = [q['query_id'] for q in queries]
        relevant_responses = [r for r in responses if r['query_id'] in query_ids]
        
        if not relevant_responses:
            return 0
        
        response_ids = [r['response_id'] for r in relevant_responses]
        relevant_mentions = [m for m in mentions if m['response_id'] in response_ids]
        
        return round((len(relevant_mentions) / len(relevant_responses)) * 100)
    
    def _calculate_potential_score(self, current_score: int, topic_name: str, persona_name: str) -> int:
        """Calculate potential score based on industry benchmarks"""
        # Base potential on topic type and persona complexity
        base_potential = 60  # Industry average
        
        # Adjust for branded topics (higher potential)
        if 'haldiram' in topic_name.lower():
            base_potential = 75
        
        # Adjust for persona complexity
        complex_personas = ['Health-Conscious Parent', 'Foodie Explorer']
        if any(complex_persona in persona_name for complex_persona in complex_personas):
            base_potential -= 10
        
        return min(85, max(current_score + 20, base_potential))
    
    def _calculate_impact(self, query_count: int, current_score: int) -> str:
        """Calculate impact level"""
        if query_count >= 4 and current_score < 30:
            return 'High'
        elif query_count >= 2 and current_score < 50:
            return 'Medium'
        return 'Low'
    
    def _calculate_effort(self, persona_name: str, topic_name: str) -> str:
        """Calculate effort level"""
        complex_personas = ['Health-Conscious Parent', 'Foodie Explorer']
        specific_topics = ['Haldiram Snacks Pvt Bhujia Recipes', 'Haldiram Snacks Pvt Online Ordering Experience']
        
        is_complex_persona = any(persona in persona_name for persona in complex_personas)
        is_specific_topic = any(topic in topic_name for topic in specific_topics)
        
        if is_complex_persona and is_specific_topic:
            return 'High'
        elif is_complex_persona or is_specific_topic:
            return 'Medium'
        return 'Low'
    
    def _calculate_priority(self, potential_increase: int, impact: str, effort: str) -> int:
        """Calculate priority score (1-10)"""
        priority = potential_increase / 10  # Base on potential increase
        
        # Adjust for impact
        if impact == 'High':
            priority += 3
        elif impact == 'Medium':
            priority += 1.5
        
        # Adjust for effort (inverse relationship)
        if effort == 'Low':
            priority += 2
        elif effort == 'Medium':
            priority += 1
        else:
            priority -= 1
        
        return max(1, min(10, round(priority)))
    
    def _calculate_topic_visibility(self, queries: List[Dict], responses: List[Dict], mentions: List[Dict]) -> int:
        """Calculate current visibility for a topic"""
        return self._calculate_persona_topic_score(queries, responses, mentions)
    
    def _count_competitor_mentions(self, queries: List[Dict], responses: List[Dict], mentions: List[Dict]) -> int:
        """Count competitor mentions for topic using competitors table"""
        # For now, we'll use a simplified approach since we don't have topic-specific competitor data
        # Get total competitor mentions from competitors table
        try:
            # Get the audit_id from the first query (they should all have the same audit_id)
            if not queries:
                return 0
            
            first_query = queries[0]
            audit_id = first_query.get('audit_id')
            if not audit_id:
                return 0
            
            # Get total competitor mentions from competitors table
            competitors_result = self.supabase.table("competitors").select("mention_count").eq("audit_id", audit_id).execute()
            if hasattr(competitors_result, 'error') and competitors_result.error:
                logger.error(f"❌ Failed to fetch competitors for mention count: {competitors_result.error}")
                return 0
            
            competitors = competitors_result.data or []
            total_mentions = sum(comp.get('mention_count', 0) for comp in competitors)
            
            # Estimate topic-specific mentions based on total mentions and number of topics
            topics = self._get_topics(audit_id)
            num_topics = len(topics) if topics else 1
            
            # Simple heuristic: distribute mentions across topics
            estimated_topic_mentions = max(1, total_mentions // num_topics)
            
            return estimated_topic_mentions
            
        except Exception as e:
            logger.error(f"❌ Error counting competitor mentions: {e}")
            return 0
    
    def _is_main_brand(self, brand_name: str) -> bool:
        """Check if brand name is the main brand"""
        if not brand_name:
            return False
        brand_lower = brand_name.lower()
        return any(keyword in brand_lower for keyword in self.main_brand_keywords)
    
    def _generate_content_recommendation(self, topic_name: str, current_visibility: int, competitor_mentions: int) -> str:
        """Generate content recommendation for topic"""
        if competitor_mentions > current_visibility * 2:
            return "High competitor activity detected. Create thought leadership content to reclaim conversation space."
        elif current_visibility < 30:
            return "Low brand visibility. Develop targeted content addressing common questions in this topic."
        elif current_visibility < 50:
            return "Moderate visibility. Increase content frequency and improve messaging quality."
        else:
            return "Strong performance. Maintain current strategy and explore advanced positioning opportunities."

# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/recommendations/{audit_id}")
async def get_strategic_recommendations(audit_id: str):
    """
    Get comprehensive strategic recommendations for an audit
    
    Returns:
    - Opportunity gaps analysis
    - Content strategy recommendations  
    - Competitive insights
    - Overall potential scoring
    - Key actionable recommendations
    """
    try:
        logger.info(f"🎯 Getting strategic recommendations for audit: {audit_id}")
        
        # Validate UUID format
        validated_audit_id = validate_uuid(audit_id, "audit_id")
        
        # Initialize analysis engine
        supabase = get_supabase_client()
        engine = StrategicAnalysisEngine(supabase)
        
        # Run all analyses
        opportunity_gaps = engine.calculate_opportunity_gaps(validated_audit_id)
        content_strategy = engine.analyze_content_strategy(validated_audit_id)
        competitive_insights = engine.analyze_competitive_insights(validated_audit_id)
        overall_score = engine.calculate_overall_potential(validated_audit_id, opportunity_gaps)
        key_recommendations = engine.generate_key_recommendations(
            opportunity_gaps, content_strategy, competitive_insights
        )
        
        # Compile results
        results = {
            "opportunityGaps": opportunity_gaps,
            "contentStrategy": content_strategy,
            "competitiveInsights": competitive_insights,
            "overallScore": overall_score,
            "keyRecommendations": key_recommendations,
            "metadata": {
                "audit_id": validated_audit_id,
                "generated_at": datetime.utcnow().isoformat(),
                "analysis_engine": "StrategicAnalysisEngine v1.0"
            }
        }
        
        logger.info(f"✅ Strategic recommendations generated successfully")
        logger.info(f"📊 Summary: {len(opportunity_gaps)} gaps, {len(content_strategy)} strategies, {len(competitive_insights)} competitors")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating strategic recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for strategic recommendations service"""
    return {
        "status": "healthy",
        "service": "Strategic Recommendations API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }