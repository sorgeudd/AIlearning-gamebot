import os
import json
from typing import Dict, List
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class OpenAIAnalyzer:
    def __init__(self):
        self.action_history = []
        self.analysis_cache = {}
        
    def analyze_game_state(self, game_state: Dict, recent_actions: List[Dict]) -> Dict:
        """Analyze current game state and recent actions to provide strategic insights"""
        state_summary = {
            'player_position': game_state.get('player_position'),
            'nearby_objects': [
                {
                    'type': obj.type,
                    'properties': obj.properties
                } for obj in game_state.get('nearby_objects', [])
            ],
            'player_status': game_state.get('player_status'),
            'recent_actions': recent_actions[-5:] if recent_actions else []  # Last 5 actions
        }
        
        # Create prompt for analysis
        prompt = f"""Analyze this game state and recent actions to provide strategic recommendations:
        Current Game State: {json.dumps(state_summary, indent=2)}
        
        Provide analysis in JSON format with the following structure:
        {
            "recommended_action": str,  # One of: "gather", "fish", "combat", "explore", "healing"
            "target_priority": List[str],  # Types of targets to prioritize
            "risk_assessment": float,  # 0-1 scale
            "strategic_reasoning": str
        }
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": "You are a game AI strategist analyzing player behavior and game states."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            self.analysis_cache[str(game_state['player_position'])] = analysis
            return analysis
            
        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            # Fallback to last cached analysis or default
            return self.analysis_cache.get(
                str(game_state['player_position']),
                {
                    "recommended_action": "explore",
                    "target_priority": [],
                    "risk_assessment": 0.5,
                    "strategic_reasoning": "Fallback to exploration due to analysis failure"
                }
            )
    
    def learn_from_outcome(self, action: Dict, outcome: Dict, success: bool) -> Dict:
        """Learn from action outcomes to improve future recommendations"""
        self.action_history.append({
            "action": action,
            "outcome": outcome,
            "success": success
        })
        
        # Analyze patterns in successful actions
        if len(self.action_history) >= 10:  # Analyze after collecting enough data
            recent_history = self.action_history[-10:]
            prompt = f"""Analyze these recent action outcomes to identify successful patterns:
            Action History: {json.dumps(recent_history, indent=2)}
            
            Provide analysis in JSON format with the following structure:
            {
                "successful_patterns": List[str],
                "failure_patterns": List[str],
                "improvement_suggestions": List[str],
                "success_rate": float
            }
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "system",
                        "content": "You are a game AI strategist analyzing action patterns and outcomes."
                    }, {
                        "role": "user",
                        "content": prompt
                    }],
                    response_format={"type": "json_object"}
                )
                
                pattern_analysis = json.loads(response.choices[0].message.content)
                # Keep only recent history
                self.action_history = self.action_history[-50:]
                return pattern_analysis
                
            except Exception as e:
                print(f"OpenAI pattern analysis failed: {e}")
                return {
                    "successful_patterns": [],
                    "failure_patterns": [],
                    "improvement_suggestions": ["Continue current strategy"],
                    "success_rate": sum(1 for x in recent_history if x["success"]) / len(recent_history)
                }
        
        return None  # Not enough data for analysis yet
