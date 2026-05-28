#!/usr/bin/env python3
"""
Super Enhanced Chatbot - Works with your existing database
Provides intelligent, targeted responses that match questions asked
"""

import sys
import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add cultureAI to path
sys.path.append('cultureAI')

class SuperEnhancedTribesBot:
    """Enhanced chatbot with intelligent response matching"""
    
    def __init__(self):
        # Find and load database
        self.database_file = self._find_database()
        if not self.database_file:
            print("❌ No database file found!")
            return
        
        print(f"Using database: {self.database_file}")
        
        # Load database
        self.database = self._load_database()
        
        # Initialize base chatbot if available
        self.base_chatbot = None
        try:
            from cameroon_chatbot import AdvancedTribesBot
            self.base_chatbot = AdvancedTribesBot(self.database_file, verbose=False)
            print("Base chatbot loaded successfully")
        except Exception as e:
            print(f"Note: Base chatbot not available: {e}")
        
        # Enhanced response templates
        self.response_templates = {
            'marriage': "When it comes to marriage and family traditions among the {tribe} people:\n\n{content}\n\nThese marriage customs reflect their deep cultural values and social organization.",
            'food': "The culinary traditions of the {tribe} people include:\n\n{content}\n\nTheir food traditions are deeply connected to their environment and cultural practices.",
            'religion': "The spiritual beliefs and religious practices of the {tribe} people encompass:\n\n{content}\n\nThese beliefs form the foundation of their worldview and community life.",
            'economy': "The economic activities and livelihood of the {tribe} people involve:\n\n{content}\n\nTheir economic practices are closely tied to their environment and cultural values.",
            'arts': "The artistic traditions and craftsmanship of the {tribe} people feature:\n\n{content}\n\nThese artistic expressions are integral to their cultural identity and heritage.",
            'governance': "The governance and leadership systems of the {tribe} people include:\n\n{content}\n\nThese leadership structures reflect their traditional values and social organization.",
            'history': "The historical background and origins of the {tribe} people reveal:\n\n{content}\n\nThis history has shaped their current cultural practices and identity.",
            'culture': "The cultural practices and traditions of the {tribe} people encompass:\n\n{content}\n\nThese cultural elements work together to create their unique way of life.",
            'overview': "About the {tribe} people:\n\n{content}\n\nThis provides an overview of their rich cultural heritage."
        }
        
        # Keywords for intent detection
        self.intent_keywords = {
            'marriage': ['marriage', 'wedding', 'bride', 'groom', 'family', 'kinship', 'spouse', 'matrimony', 'marry', 'married', 'wedding ceremonies', 'social structure', 'customs and social'],
            'food': ['food', 'cuisine', 'eat', 'cooking', 'diet', 'meal', 'dish', 'recipe', 'traditional food'],
            'religion': ['religion', 'belief', 'spiritual', 'god', 'worship', 'prayer', 'sacred', 'ritual'],
            'economy': ['economy', 'work', 'job', 'trade', 'business', 'livelihood', 'occupation', 'farming'],
            'arts': ['art', 'craft', 'carving', 'pottery', 'weaving', 'music', 'dance', 'sculpture'],
            'governance': ['governance', 'leadership', 'chief', 'king', 'ruler', 'government', 'authority'],
            'history': ['history', 'origin', 'past', 'ancestor', 'migration', 'ancient', 'historical'],
            'culture': ['culture', 'tradition', 'custom', 'practice', 'ceremony', 'festival', 'celebration']
        }
        
        print("Super Enhanced Tribes Bot Initialized!")
        print("Features:")
        print("- Intelligent intent detection")
        print("- Question-specific responses")
        print("- Enhanced response formatting")
        print("- Comprehensive tribal database")
    
    def _find_database(self) -> Optional[str]:
        """Find the tribal database file"""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            # Relative to script location
            os.path.join(script_dir, "backend", "tribes_data.json"),
            os.path.join(script_dir, "AI_logics", "txt", "cultural_data.json"),
            
            # Relative to current working directory
            "backend/tribes_data.json",
            "AI_logics/txt/cultural_data.json",
            "Robix/backend/tribes_data.json", 
            "Robix/AI_logics/txt/cultural_data.json",
            "Robix/Robix/backend/tribes_data.json",
            "Robix/Robix/AI_logics/txt/cultural_data.json",
            
            # Absolute paths based on known structure
            "C:/Users/BANVEN/Desktop/Robix1/Robix/Robix/backend/tribes_data.json",
            "C:/Users/BANVEN/Desktop/Robix1/Robix/Robix/AI_logics/txt/cultural_data.json"
        ]
        
        print("Searching for database files...")
        for path in possible_paths:
            print(f"   Checking: {path}")
            if os.path.exists(path):
                print(f"   Found: {path}")
                return path
        
        print("   No database file found in any location")
        return None
    
    def _load_database(self) -> Dict:
        """Load the tribal database"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
            return {'tribes': {}}
    
    def detect_intent(self, query: str) -> Tuple[str, float]:
        """Detect what the user is asking about"""
        query_lower = query.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            return best_intent, confidence
        
        return 'overview', 0.5  # Default fallback
    
    def extract_tribe_name(self, query: str) -> Optional[str]:
        """Extract tribe name from query"""
        query_lower = query.lower()
        
        # Get all tribe names from database
        if 'tribes' in self.database:
            for tribe_key, tribe_data in self.database['tribes'].items():
                tribe_name = tribe_data.get('name', tribe_key)
                if tribe_name.lower() in query_lower:
                    return tribe_name
                if tribe_key in query_lower:
                    return tribe_name
        
        # Common tribe names to check
        common_tribes = [
            'Bamileke', 'Fulani', 'Bamum', 'Duala', 'Bassa', 'Beti', 'Kotoko', 
            'Mafa', 'Baka', 'Massa', 'Tikar', 'Kom', 'Bakweri', 'Oroko'
        ]
        
        for tribe in common_tribes:
            if tribe.lower() in query_lower:
                return tribe
        
        return None
    
    def get_tribe_data(self, tribe_name: str) -> Optional[Dict]:
        """Get data for a specific tribe"""
        if 'tribes' not in self.database:
            return None
        
        # Try exact match first
        tribe_key = tribe_name.lower()
        if tribe_key in self.database['tribes']:
            return self.database['tribes'][tribe_key]
        
        # Try partial match
        for key, data in self.database['tribes'].items():
            if tribe_name.lower() in key or key in tribe_name.lower():
                return data
            
            # Check tribe name in data
            if 'name' in data and data['name'].lower() == tribe_name.lower():
                return data
        
        return None
    
    def get_relevant_content(self, tribe_data: Dict, intent: str) -> str:
        """Get content relevant to the detected intent"""
        if 'sections' not in tribe_data:
            return "Information is being researched and will be updated soon."
        
        sections = tribe_data['sections']
        
        # Special handling for marriage and social structure questions
        if intent == 'marriage' and 'marriage' in sections:
            marriage_content = sections['marriage']
            
            # For comprehensive marriage questions, include social structure info
            additional_sections = []
            if 'culture' in sections:
                additional_sections.append(f"SOCIAL STRUCTURE & CULTURAL ORGANIZATION:\n{sections['culture']}")
            if 'governance' in sections:
                additional_sections.append(f"GOVERNANCE & SOCIAL HIERARCHY:\n{sections['governance']}")
            if 'traditions' in sections:
                additional_sections.append(f"TRADITIONAL SOCIAL PRACTICES:\n{sections['traditions']}")
            
            if additional_sections:
                return f"MARRIAGE CUSTOMS:\n{marriage_content}\n\n" + "\n\n".join(additional_sections)
            else:
                return marriage_content
        
        # Map intents to section names
        section_mapping = {
            'marriage': ['marriage', 'traditions', 'culture'],
            'food': ['food', 'culture', 'economy'],
            'religion': ['religion', 'traditions', 'culture'],
            'economy': ['economy', 'culture', 'overview'],
            'arts': ['arts_and_crafts', 'culture', 'traditions'],
            'governance': ['governance', 'culture', 'history'],
            'history': ['history', 'overview', 'culture'],
            'culture': ['culture', 'traditions', 'overview'],
            'overview': ['overview', 'culture']
        }
        
        relevant_sections = section_mapping.get(intent, ['overview', 'culture'])
        
        # Get content from relevant sections
        content_parts = []
        for section in relevant_sections:
            if section in sections and sections[section]:
                content = sections[section].strip()
                if content and len(content) > 20:  # Skip very short content
                    content_parts.append(content)
        
        if content_parts:
            return '\n\n'.join(content_parts[:2])  # Limit to 2 sections for readability
        
        # Fallback to any available content
        for section, content in sections.items():
            if content and len(content) > 20:
                return content
        
        return "Detailed information about this aspect is being researched and will be updated soon."
    
    def chat(self, query: str) -> str:
        """Enhanced chat with intelligent response matching"""
        try:
            # Extract tribe name
            tribe_name = self.extract_tribe_name(query)
            
            if not tribe_name:
                return "I'd be happy to help! Please specify which Cameroonian tribe you'd like to know about. For example: 'Tell me about Bamileke marriage customs' or 'What do Fulani people eat?'"
            
            # Get tribe data
            tribe_data = self.get_tribe_data(tribe_name)
            
            if not tribe_data:
                return f"I don't have information about the {tribe_name} people in my database yet. Please try another tribe or check the spelling."
            
            # Detect intent
            intent, confidence = self.detect_intent(query)
            
            # Get relevant content
            content = self.get_relevant_content(tribe_data, intent)
            
            # Format response using template
            if intent in self.response_templates:
                response = self.response_templates[intent].format(
                    tribe=tribe_name,
                    content=content
                )
            else:
                response = f"About the {tribe_name} people:\n\n{content}"
            
            # Add metadata info for debugging (optional)
            if confidence > 0.7:
                print(f"Intent: {intent} (confidence: {confidence:.2f})")
            
            return response
            
        except Exception as e:
            print(f"Error: {e}")
            
            # Fallback to base chatbot if available
            if self.base_chatbot:
                try:
                    response, _ = self.base_chatbot.response_generator.generate_response(query)
                    return response
                except:
                    pass
            
            return f"I apologize, but I encountered an error processing your query. Please try rephrasing your question."
    
    def start_interactive_chat(self):
        """Start interactive chat session"""
        print("\n" + "="*60)
        print("SUPER ENHANCED CAMEROONIAN TRIBES BOT")
        print("Intelligent Responses That Match Your Questions")
        print("="*60)
        print("Features:")
        print("- Intelligent intent detection")
        print("- Question-specific responses")
        print("- Comprehensive tribal knowledge")
        print("- Enhanced response formatting")
        print("\nExamples:")
        print("- 'What are Bamileke marriage customs?'")
        print("- 'Tell me about Fulani food traditions'")
        print("- 'How do Kotoko people worship?'")
        print("- 'What is the economy of Mafa people like?'")
        print("\nType 'quit' to exit")
        print("="*60)
        
        while True:
            try:
                query = input("\nAsk about any Cameroonian tribe: ").strip()
                
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("Thank you for using Super Enhanced Tribes Bot!")
                    break
                
                if not query:
                    continue
                
                print("\nProcessing your question...")
                response = self.chat(query)
                print(f"\nResponse:\n{response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def test_system(self):
        """Test the enhanced system with sample queries"""
        test_queries = [
            "What are Bamileke marriage customs?",
            "Tell me about Fulani food traditions",
            "How do Kotoko people worship?",
            "What is the economy of Mafa people like?",
            "Describe Baka arts and crafts",
            "Who leads the Kom people?",
            "What is the history of Tikar people?"
        ]
        
        print("\nTESTING ENHANCED SYSTEM")
        print("="*40)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 30)
            
            response = self.chat(query)
            print(f"Response: {response[:200]}...")
            print()

def main():
    """Main function"""
    bot = SuperEnhancedTribesBot()
    
    if not bot.database_file:
        print("Cannot start - no database found!")
        return
    
    import argparse
    parser = argparse.ArgumentParser(description="Super Enhanced Tribes Bot")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--interactive", action="store_true", help="Start interactive chat")
    
    args = parser.parse_args()
    
    if args.test:
        bot.test_system()
    elif args.interactive:
        bot.start_interactive_chat()
    else:
        # Default to interactive
        bot.start_interactive_chat()

if __name__ == "__main__":
    main()
