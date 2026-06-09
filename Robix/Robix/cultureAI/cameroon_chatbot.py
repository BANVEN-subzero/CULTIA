#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Cameroonian Tribes Educational Chatbot
==========================================================

An intelligent chatbot that uses structured JSON data for fast, accurate responses
about Cameroonian tribes.

Features:
- Lightning-fast JSON-based data retrieval
- Multi-layered search: categories, keywords, full-text
- Intelligent query understanding and intent detection
- Hybrid responses: Structured data + LLM enhancement
- Text and speech input/output with mode switching
- Comprehensive logging and analytics

Dependencies:
- Standard library only for core functionality
- Optional: speechrecognition, pyttsx3 for speech features
- Optional: Ollama for LLM enhancement

Usage:
    python json_chatbot.py structured_tribes.json
    python json_chatbot.py --data tribes.json --model llama3.2 --verbose
    python json_chatbot.py tribes.json --no-speech --analytics
"""

import os
import re
import sys
import json
import time
import requests
import subprocess
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# Optional speech libraries
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Import Ollama client
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

# Global tribe list for entity extraction
SUPPORTED_TRIBES = []

# =============================================================================
# Configuration
# =============================================================================

def load_supported_tribes(json_path):
    """Load supported tribes from the JSON data file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the JSON is nested under 'tribes' or flat
        if 'tribes' in data:
            return list(data['tribes'].keys())
        
        # If flat, filter out non-tribe keys if they exist (like 'metadata')
        return [k for k in data.keys() if k not in ['metadata', 'cross_references', 'source_file']]
    except Exception as e:
        print(f"Error loading tribes from {json_path}: {e}")
        # Fallback to original list
        return [
            "bamileke", "nsaw", "bamum", "bassa", "fulani", "duala", "beti", 
            "grassfields", "sawa", "north_bantu", "tikar", "bakweri", "widikum", 
            "kom", "bafut", "ogeez", "menka", "esu", "bafanji", "mbum", 
            "giziga", "mafa", "kapsiki", "moundang", "tupuri", "mass", 
            "kotoko", "kanuri", "hausa", "bororo", "baka", "bakola", "bedzan", 
            "bakossi", "balondo", "bangangte", "bafang", "bafoussam", 
            "bamendjou", "bandjoun", "bayangam", "babungo", "bali", "batanga", 
            "bulu", "fang", "ewondo", "etonde", "mbo", "oroko", "isubu"
        ]

# Query intent patterns
INTENT_PATTERNS = {
    # 1. Core Identity & Structure
    "core_identity": [
        r"\b(identity|who are|structure|organization|endonym|name)\b",
        r"\b(social structure|kinship|lineage|clan|family system)\b"
    ],
    "leadership": [
        r"\b(leadership|leader|chief|elder|governance|authority|government)\b",
        r"\b(council|decision|rule|govern|traditional authority)\b"
    ],
    
    # 2. Worldview & Spirituality  
    "worldview": [
        r"\b(worldview|cosmology|creation|origin story|mythology)\b",
        r"\b(universe|world creation|beginning|genesis)\b"
    ],
    "spirituality": [
        r"\b(spiritual|spirituality|sacred|holy|divine|supernatural)\b",
        r"\b(spirit|soul|ancestor|deity|god|goddess)\b"
    ],
    "religion": [
        r"\b(religion|religious|belief|faith|worship|prayer)\b",
        r"\b(christian|muslim|islam|traditional belief|animism)\b"
    ],
    "rituals": [
        r"\b(ritual|ceremony|rite|celebration|festival|tradition)\b",
        r"\b(initiation|coming of age|harvest|seasonal|healing)\b"
    ],
    
    # 3. Material Culture & Subsistence
    "subsistence": [
        r"\b(subsistence|livelihood|survival|food production|sustenance)\b",
        r"\b(hunting|gathering|fishing|farming|pastoralism|agriculture)\b"
    ],
    "food": [
        r"\b(food|eat|cuisine|dish|meal|cook|recipe|diet|nutrition)s?\b",
        r"\b(crop|staple|ingredient|feast|cooking|preparation)s?\b"
    ],
    "technology": [
        r"\b(technology|tool|weapon|instrument|equipment|craft|use|tools)s?\b",
        r"\b(traditional technology|indigenous technology|making|creation|implement)s?\b"
    ],
    "shelter": [
        r"\b(shelter|house|dwelling|architecture|building|construction)s?\b",
        r"\b(home|residence|village|settlement|traditional house)s?\b"
    ],
    "clothing": [
        r"\b(clothing|dress|garment|attire|adornment|jewelry)s?\b",
        r"\b(traditional dress|costume|fabric|textile|fashion)s?\b"
    ],
    
    # 4. History & Historical Trauma
    "history": [
        r"\b(history|historical|past|origin|ancient)s?\b",
        r"\b(came from|migration|settlement|founded|established)s?\b"
    ],
    "pre_contact": [
        r"\b(pre.contact|before contact|original|indigenous|native)\b",
        r"\b(traditional life|ancestral|pre.colonial|before colonization)\b"
    ],
    "colonialism": [
        r"\b(colonial|colonialism|colonization|european|contact)\b",
        r"\b(missionary|treaty|conquest|occupation|foreign rule)\b"
    ],
    "resistance": [
        r"\b(resistance|fight|struggle|revolt|rebellion|oppose)\b",
        r"\b(defend|protect|preserve|maintain|cultural survival)\b"
    ],
    
    # 5. Contemporary Life & Politics
    "modern_life": [
        r"\b(modern|contemporary|current|today|present|now)\b",
        r"\b(current life|modern society|today's|contemporary issues)\b"
    ],
    "politics": [
        r"\b(politics|political|government|sovereignty|rights|law)\b",
        r"\b(tribal government|self.governance|autonomy|recognition)\b"
    ],
    "economy": [
        r"\b(economy|economic|work|job|trade|business|income|employment)\b",
        r"\b(industry|tourism|gaming|entrepreneurship|development)\b"
    ],
    "revitalization": [
        r"\b(revitalization|revival|preservation|maintain|restore)\b",
        r"\b(cultural preservation|language revival|traditional knowledge)\b"
    ],
    
    # 6. Arts, Knowledge & Expression
    "oral_tradition": [
        r"\b(oral tradition|story|storytelling|myth|legend|narrative)\b",
        r"\b(folklore|tale|oral history|traditional story)\b"
    ],
    "visual_arts": [
        r"\b(art|artistic|visual|craft|creation|design|pattern)\b",
        r"\b(pottery|carving|painting|weaving|basketry|beadwork)\b"
    ],
    "music_dance": [
        r"\b(music|musical|dance|dancing|song|singing|performance)\b",
        r"\b(drum|instrument|rhythm|melody|ceremonial dance)\b"
    ],
    "traditional_knowledge": [
        r"\b(traditional knowledge|indigenous knowledge|wisdom|expertise)\b",
        r"\b(ethnoscience|plant medicine|ecological knowledge|astronomy)\b"
    ],
    
    # General categories (backwards compatibility)
    "overview": [
        r"\b(overview|general|about|tell me about|describe|profile)\b",
        r"\b(introduction|summary|basic|comprehensive)\b"
    ],
    "culture": [
        r"\b(culture|cultural|customs|way of life|lifestyle|heritage)\b",
        r"\b(values|practices|norms|social|traditional)\b"
    ],
    "traditions": [
        r"\b(tradition|ceremony|festival|customs|practices|observances)\b"
    ],
    "marriage": [
        r"\b(marriage|wedding|bride|groom|matrimony|spouse|courtship)\b",
        r"\b(engagement|dowry|bride price|family alliance)\b"
    ],
    "language": [
        r"\b(language|speak|dialect|tongue|linguistic|communication)\b",
        r"\b(words|vocabulary|oral|written|native language)\b"
    ],
    "festivals": [
        r"\b(festival|celebration|ceremony|event|commemoration)\b",
        r"\b(annual|seasonal|harvest|cultural festival)\b"
    ],
    "compare": [
        r"\b(compare|difference|similar|versus|vs|contrast)\b",
        r"\b(between|both|similarities|differences)\b"
    ]
}

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

SYSTEM_PROMPT = """You are an expert educator on Cameroonian tribal culture, specializing in over 50 tribes of Cameroon and neighboring regions.

Guidelines:
- Use the provided structured data as your primary source
- Be educational, respectful, and culturally sensitive
- Synthesize information clearly and engagingly
- If information is incomplete, acknowledge gaps honestly
- Focus on the tribes specified in the data
- Keep responses conversational but informative
"""


# =============================================================================
# Utilities
# =============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('chatbot.log'),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )
    return logging.getLogger('TribesBot')


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    return re.sub(r'\s+', ' ', text.lower().strip())


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using sequence matching"""
    return SequenceMatcher(None, normalize_text(text1), normalize_text(text2)).ratio()


def extract_tribe_names(text: str) -> List[str]:
    """Extract tribe names from text with fuzzy matching and aliases"""
    from difflib import get_close_matches
    
    text_lower = normalize_text(text)
    found_tribes = []
    
    # Use global SUPPORTED_TRIBES, fallback to hardcoded list if empty
    tribes_to_check = SUPPORTED_TRIBES if SUPPORTED_TRIBES else [
        "bamileke", "nsaw", "bamum", "bassa", "fulani", "duala", "beti", 
        "grassfields", "sawa", "north_bantu", "tikar", "bakweri", "widikum", 
        "kom", "bafut", "ogeez", "menka", "esu", "bafanji", "mbum", 
        "giziga", "mafa", "kapsiki", "moundang", "tupuri", "mass", 
        "kotoko", "kanuri", "hausa", "bororo", "baka", "bakola", "bedzan", 
        "bakossi", "balondo", "bangangte", "bafang", "bafoussam", 
        "bamendjou", "bandjoun", "bayangam", "babungo", "bali", "batanga", 
        "bulu", "fang", "ewondo", "etonde", "mbo", "oroko", "isubu"
    ]
    
    # Common aliases
    aliases = {
        "nso": "nsaw", "bamun": "bamum", "bamoun": "bamum",
        "ewondo": "beti", "fang": "beti", "bulu": "beti",
        "bororo": "fulani", "fula": "fulani", "peul": "fulani", "mbororo": "fulani",
        "pygmy": "baka", "pygmies": "baka", "bakola": "baka",
        "sawa": "duala", "douala": "duala",
        "grassfields": "bamileke", "grassfield": "bamileke",
        "kirdi": "mafa", "mandara": "mafa",
        "haoussa": "hausa"
    }
    
    # 1. Exact match and alias match
    for tribe in tribes_to_check:
        if tribe in text_lower:
            found_tribes.append(tribe)
            
    for alias, canonical in aliases.items():
        if alias in text_lower and canonical in tribes_to_check and canonical not in found_tribes:
            found_tribes.append(canonical)
            
    # 2. Fuzzy match if no exact matches found
    if not found_tribes:
        words = text_lower.split()
        for word in words:
            if len(word) >= 3:
                matches = get_close_matches(word, tribes_to_check, n=1, cutoff=0.7)
                if matches and matches[0] not in found_tribes:
                    found_tribes.append(matches[0])
    
    return found_tribes


# =============================================================================
# Wikipedia Integration
# =============================================================================

class WikipediaExtractor:
    """Extract information from Wikipedia for enhanced responses"""
    
    def __init__(self):
        self.logger = logging.getLogger('TribesBot.Wikipedia')
        self.cache = {}
        
    def search_wikipedia(self, query: str, tribe_name: str = None) -> Optional[Dict]:
        """Search Wikipedia for additional information"""
        try:
            # Construct search terms
            search_terms = []
            if tribe_name:
                search_terms.extend([
                    f"{tribe_name} people Cameroon",
                    f"{tribe_name} tribe",
                    f"{tribe_name} ethnic group"
                ])
            search_terms.append(query)
            
            for term in search_terms:
                if term in self.cache:
                    return self.cache[term]
                
                # Search Wikipedia
                search_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': term,
                    'srlimit': 3
                }
                
                headers = {
                    'User-Agent': 'CameroonTribesBot/1.0 (Educational Purpose)'
                }
                response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('query', {}).get('search'):
                        # Get the first result
                        first_result = data['query']['search'][0]
                        page_title = first_result['title']
                        
                        # Get page summary
                        summary = self.get_page_summary(page_title)
                        if summary:
                            self.cache[term] = summary
                            return summary
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Wikipedia search failed: {e}")
            return None
    
    def get_page_summary(self, page_title: str) -> Optional[Dict]:
        """Get Wikipedia page summary"""
        try:
            url = f"{WIKIPEDIA_API_URL}{page_title}"
            headers = {
                'User-Agent': 'CameroonTribesBot/1.0 (Educational Purpose)'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'extract': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }
            return None
            
        except Exception as e:
            self.logger.warning(f"Wikipedia page fetch failed: {e}")
            return None


# =============================================================================
# JSON Data Manager
# =============================================================================

class TribesDataManager:
    """Manages structured tribal data from JSON"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = {}
        self.metadata = {}
        self.search_index = {}
        self.logger = logging.getLogger('TribesBot.DataManager')
        
        self.load_data()
        self.build_search_index()
    
    def load_data(self):
        """Load structured data from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            # Handle both nested and flat JSON structures
            if 'tribes' in full_data:
                self.metadata = full_data.get('metadata', {})
                self.data = full_data.get('tribes', {})
            else:
                # Flat structure: tribes are at the top level
                self.data = full_data
                # Extract metadata if it exists as a key, or use empty dict
                self.metadata = full_data.get('metadata', {})
                # Remove non-tribe keys from self.data
                if 'metadata' in self.data:
                    del self.data['metadata']
            
            self.logger.info(f"Loaded data for {len(self.data)} tribes")
            self.logger.info(f"Source: {self.metadata.get('source_file', 'Unknown')}")
            
        except FileNotFoundError:
            self.logger.error(f"Data file not found: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def build_search_index(self):
        """Build search index for fast lookups"""
        self.logger.info("Building search index...")
        
        # Create keyword index
        self.search_index = {
            'keywords': defaultdict(list),
            'categories': defaultdict(list),
            'aliases': defaultdict(str)
        }
        
        for tribe_name, tribe_data in self.data.items():
            # Index keywords
            for keyword in tribe_data.get('keywords', []):
                self.search_index['keywords'][keyword.lower()].append(tribe_name)
            
            # Index categories
            for category, content in tribe_data.get('sections', {}).items():
                if content:
                    self.search_index['categories'][category].append(tribe_name)
            
            # Index aliases
            for alias in tribe_data.get('aliases', []):
                self.search_index['aliases'][alias.lower()] = tribe_name
        
        self.logger.info("Search index built successfully")
    
    def get_tribe_data(self, tribe_name: str) -> Optional[Dict]:
        """Get all data for a specific tribe"""
        return self.data.get(tribe_name.lower())
    
    def get_tribe_section(self, tribe_name: str, section: str) -> Optional[str]:
        """Get specific section content for a tribe"""
        tribe_data = self.get_tribe_data(tribe_name)
        if tribe_data:
            return tribe_data.get('sections', {}).get(section)
        return None
    
    def search_by_keywords(self, keywords: List[str]) -> List[Tuple[str, float]]:
        """Search tribes by keywords with relevance scoring"""
        tribe_scores = defaultdict(float)
        
        for keyword in keywords:
            keyword = keyword.lower()
            matching_tribes = self.search_index['keywords'].get(keyword, [])
            for tribe in matching_tribes:
                tribe_scores[tribe] += 1.0 / len(keywords)
        
        # Sort by relevance score
        return sorted(tribe_scores.items(), key=lambda x: x[1], reverse=True)
    
    def search_by_content(self, query: str, tribe_filter: Optional[List[str]] = None) -> List[Tuple[str, str, float]]:
        """Search content across all sections with similarity scoring"""
        results = []
        query_lower = normalize_text(query)
        
        tribes_to_search = tribe_filter if tribe_filter else self.data.keys()
        
        for tribe_name in tribes_to_search:
            tribe_data = self.data[tribe_name]
            
            for section, content in tribe_data.get('sections', {}).items():
                if content:
                    similarity = calculate_similarity(query_lower, content)
                    if similarity > 0.1:  # Minimum similarity threshold
                        results.append((tribe_name, section, similarity))
        
        return sorted(results, key=lambda x: x[2], reverse=True)
    
    def get_available_categories(self, tribe_name: Optional[str] = None) -> List[str]:
        """Get available content categories"""
        if tribe_name:
            tribe_data = self.get_tribe_data(tribe_name)
            if tribe_data:
                return [cat for cat, content in tribe_data.get('sections', {}).items() if content]
        else:
            categories = set()
            for tribe_data in self.data.values():
                categories.update(tribe_data.get('sections', {}).keys())
            return list(categories)
        return []
    
    def compare_tribes(self, tribe_names: List[str]) -> Dict:
        """Compare multiple tribes and return similarities and differences"""
        if len(tribe_names) < 2:
            return {}
        
        comparison = {
            "tribes": tribe_names,
            "similarities": {},
            "differences": {}
        }
        
        # Get data for all tribes
        tribe_data_list = [self.get_tribe_data(name) for name in tribe_names]
        
        # Find common categories
        all_categories = set()
        for tribe_data in tribe_data_list:
            if tribe_data:
                all_categories.update(tribe_data.get('sections', {}).keys())
        
        # Compare each category
        for category in all_categories:
            category_contents = []
            for tribe_data in tribe_data_list:
                if tribe_data:
                    content = tribe_data.get('sections', {}).get(category, "")
                    category_contents.append(content)
                else:
                    category_contents.append("")
            
            # Check if all contents are similar (simple approach)
            if all(content == category_contents[0] for content in category_contents):
                if category_contents[0]:  # Not empty
                    comparison["similarities"][category] = category_contents[0]
            else:
                # Different contents - add to differences
                comparison["differences"][category] = dict(zip(tribe_names, category_contents))
        
        return comparison


# =============================================================================
# Intent Detection
# =============================================================================

class IntentDetector:
    """Detects user intent from queries"""
    
    def __init__(self):
        self.logger = logging.getLogger('TribesBot.IntentDetector')
        self.compiled_patterns = {}
        
        # Compile regex patterns for better performance
        for intent, patterns in INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def detect_intent(self, query: str) -> Dict[str, float]:
        """Detect intent categories from query with confidence scores"""
        intent_scores = defaultdict(float)
        query_lower = query.lower()
        
        # Specific intent patterns with higher weight
        high_priority_patterns = {
            "leadership": [r"\bleadership\b", r"\bleader\b", r"\bchief\b", r"\bfon\b", r"\bking\b", r"\bgovernance\b"],
            "food": [r"\bfood\b", r"\bmeal\b", r"\bmeals\b", r"\bdish\b", r"\bdishes\b", r"\bcuisine\b", r"\beat\b", r"\btraditional meal\b", r"\btraditional meals\b"],
            "location": [r"\blocation\b", r"\bwhere\b", r"\blive\b", r"\bregion\b", r"\bsettlement\b"],
            "history": [r"\bhistory\b", r"\bpast\b", r"\borigin\b", r"\bmigration\b"],
            "arts_and_crafts": [r"\barts\b", r"\bcrafts\b", r"\bcarving\b", r"\bweaving\b", r"\bpottery\b"],
            "traditional_meals": [r"\btraditional meal\b", r"\btraditional meals\b", r"\btraditional food\b", r"\bnative food\b"]
        }
        
        # Standard patterns
        all_patterns = {**INTENT_PATTERNS}
        
        # 1. Check high priority patterns first
        for intent, patterns in high_priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    # Direct match gets a high score
                    intent_scores[intent] += 5.0

        # 2. Check all other patterns
        for intent, patterns in all_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] += score
        
        return dict(intent_scores)
    
    def get_primary_intent(self, query: str) -> Optional[str]:
        """Get the primary intent category based on the highest confidence score"""
        intents = self.detect_intent(query)
        if not intents:
            return None
            
        # Prioritize comparison intent if it has a significant score
        if "compare" in intents and intents["compare"] > 0.5:
            return "compare"
            
        # Specificity ranking: higher index means more general
        specificity_order = [
            'marriage', 'festivals', 'language', 'rituals', 'religion', 'food', 
            'technology', 'subsistence', 'shelter', 'clothing', 'history', 
            'pre_contact', 'colonialism', 'resistance', 'modern_life', 
            'politics', 'economy', 'revitalization', 'oral_tradition', 
            'visual_arts', 'music_dance', 'traditional_knowledge', 
            'leadership', 'governance', 'core_identity', 'spirituality',
            'culture', 'traditions', 'overview', 'general'
        ]
        
        # Find intent with highest score
        max_score = -1
        best_intent = None
        
        for intent, score in intents.items():
            if score > max_score:
                max_score = score
                best_intent = intent
            elif score == max_score:
                # Tie-breaker: choose the more specific one
                try:
                    idx1 = specificity_order.index(intent)
                    idx2 = specificity_order.index(best_intent)
                    if idx1 < idx2:
                        best_intent = intent
                except ValueError:
                    pass # Keep current best if not in list
                    
        return best_intent


# =============================================================================
# LLM Integration
# =============================================================================

class OllamaClient:
    """Ollama client for LLM integration"""
    
    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model
        self.logger = logging.getLogger('TribesBot.Ollama')
        self.available = self._check_availability()
        
        if self.available:
            self.logger.info("Ollama is available for LLM enhancement")
        else:
            self.logger.warning("Ollama not available, responses will be based on structured data only")
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            # Try HTTP API first (works even if ollama not in PATH)
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # Check if our model exists (with or without :latest suffix)
                is_available = any(self.model in name for name in model_names)
                if is_available:
                    self.logger.info(f"Ollama model '{self.model}' is available")
                else:
                    self.logger.warning(f"Ollama model '{self.model}' not available in: {model_names}")
                return is_available
            return False
        except requests.exceptions.RequestException:
            # Fallback to subprocess if HTTP fails
            try:
                result = subprocess.run(
                    ["ollama", "list"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                is_available = result.returncode == 0 and self.model in result.stdout
                if is_available:
                    self.logger.info(f"Ollama model '{self.model}' is available")
                else:
                    self.logger.warning(f"Ollama model '{self.model}' not available")
                return is_available
            except Exception as e:
                self.logger.warning(f"Ollama check failed: {e}")
                return False
        except Exception as e:
            self.logger.warning(f"Ollama check failed: {e}")
            return False
    
    def enhance_response(self, query: str, context_data: Dict) -> str:
        """Use LLM to enhance structured data into natural response"""
        if not self.available:
            return None
            
        return self._enhance_with_ollama(query, context_data)
    
    def _enhance_with_ollama(self, query: str, context_data: Dict) -> Optional[str]:
        """Enhance response using Ollama"""
        # Build context from structured data
        context_parts = []
        for section, content in context_data.items():
            if content:
                context_parts.append(f"{section.title()}: {content[:500]}...")  # Increase from 300 to 500 characters
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""{SYSTEM_PROMPT}

User Question: {query}

Structured Data Available:
{context}

Please provide a comprehensive, well-structured answer based on this information. If the data is incomplete, mention what additional information might be useful. Your response should be detailed and informative, providing rich context about the cultural practices, historical background, and social significance of the topics discussed. Aim for a response that is at least 3-4 paragraphs long with specific examples and explanations."""  # Enhanced prompt for more detailed responses
        
        try:
            # Try HTTP API first
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_response = result.get("response", "").strip()
                self.logger.info("Ollama enhancement successful")
                return enhanced_response
            else:
                self.logger.error(f"Ollama HTTP error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Ollama HTTP failed, trying subprocess: {e}")
            # Fallback to subprocess
            try:
                result = subprocess.run(
                    ["ollama", "run", self.model],
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    self.logger.info("Ollama enhancement successful (subprocess)")
                    return response
                else:
                    self.logger.error(f"Ollama error: {result.stderr}")
                    return None
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("Ollama request timed out")
                return None
            except Exception as e:
                self.logger.error(f"Ollama subprocess failed: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Ollama request failed: {e}")
            return None


# =============================================================================
# Speech Interface
# =============================================================================

class SpeechInterface:
    """Enhanced speech interface with better error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger('TribesBot.Speech')
        self.recognizer = None
        self.microphone = None
        
        if SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self._calibrate_microphone()
            except Exception as e:
                self.logger.warning(f"Microphone initialization failed: {e}")
                self.recognizer = None
                self.microphone = None
        
        self.tts_engine = self._init_tts()
    
    def _init_tts(self):
        """Initialize TTS with optimal settings"""
        if not TTS_AVAILABLE:
            return None
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 165)
            engine.setProperty('volume', 0.9)
            
            # Try to set a good voice
            voices = engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'english' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("TTS initialized successfully")
            return engine
        except Exception as e:
            self.logger.warning(f"TTS initialization failed: {e}")
            return None
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.logger.info("Microphone calibrated")
        except Exception as e:
            self.logger.warning(f"Microphone calibration failed: {e}")
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen for speech with enhanced error handling"""
        if not SR_AVAILABLE or not self.microphone:
            return None
        
        try:
            print("🎤 Listening... (speak clearly)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            print("⏳ Processing speech...")
            text = self.recognizer.recognize_google(audio)
            
            self.logger.info(f"Speech recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand speech")
            return None
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def speak(self, text: str):
        """Speak text with length optimization"""
        if not self.tts_engine:
            return
        
        try:
            # Limit length for better speech experience
            if len(text) > 400:
                sentences = text.split('. ')
                text = '. '.join(sentences[:3]) + '.'
            
            # Clean text
            clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
            
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            self.logger.warning(f"TTS failed: {e}")


# =============================================================================
# Response Generator
# =============================================================================

class SmartResponseGenerator:
    """Intelligent response generator using multiple strategies"""
    
    def __init__(self, data_manager: TribesDataManager, intent_detector: IntentDetector, 
                 ollama_client: OllamaClient):
        self.data_manager = data_manager
        self.intent_detector = intent_detector
        self.ollama_client = ollama_client
        self.wikipedia = WikipediaExtractor()
        self.logger = logging.getLogger('TribesBot.ResponseGenerator')
        
        # Analytics
        self.query_stats = defaultdict(int)
        self.response_times = []
    
    def generate_response(self, query: str) -> Tuple[str, Dict]:
        """Generate intelligent response with metadata"""
        start_time = time.time()
        metadata = {
            'tribes_mentioned': [],
            'intent_detected': None,
            'search_strategy': '',
            'llm_used': False,
            'wikipedia_used': False,
            'response_time': 0,
            'confidence': 0.0
        }
        
        # Normalize query
        query_clean = normalize_text(query)
        self.query_stats['total'] += 1
        
        # Check if query is in scope
        if not self._is_query_in_scope(query_clean):
            return self._out_of_scope_response(), metadata
        
        # Extract mentioned tribes
        mentioned_tribes = extract_tribe_names(query_clean)
        metadata['tribes_mentioned'] = mentioned_tribes
        
        # Detect intent
        primary_intent = self.intent_detector.get_primary_intent(query_clean)
        metadata['intent_detected'] = primary_intent
        
        # Generate comprehensive response with all enhancements
        response = self._generate_comprehensive_response(query_clean, mentioned_tribes, primary_intent, metadata)
        
        # Calculate response time and confidence
        metadata['response_time'] = time.time() - start_time
        self.response_times.append(metadata['response_time'])
        
        self.logger.info(f"Query processed: {query[:50]}... | Strategy: {metadata['search_strategy']} | Time: {metadata['response_time']:.2f}s")
        
        return response, metadata
    
    def _is_query_in_scope(self, query: str) -> bool:
        """Check if query is related to supported tribes"""
        # Check for tribe names
        if any(tribe in query for tribe in SUPPORTED_TRIBES):
            return True
        
        # Check for cultural keywords + cameroon
        cultural_keywords = ['culture', 'tradition', 'tribe', 'people', 'cameroon', 'heritage']
        return any(keyword in query for keyword in cultural_keywords)
    
    def _out_of_scope_response(self) -> str:
        """Generate out-of-scope response"""
        return (f"I specialize in {len(SUPPORTED_TRIBES)} Cameroonian tribes including Bakossi, Bamum, Bamileke, "
                "Nso, Bassa, Fulani, and many others. Please ask me about their culture, traditions, "
                "history, or other aspects of these tribes!")
    
    def _generate_comprehensive_response(self, query: str, tribes: List[str], intent: str, metadata: Dict) -> str:
        """Generate comprehensive response focused strictly on the user's intent"""
        metadata['search_strategy'] = 'comprehensive_enhanced'
        
        # 1. Step 1: Entity & Intent Extraction (Already done in caller)
        # Step 2: Hierarchical Database Lookup
        database_info = self._get_intent_first_database_info(tribes, intent, query)
        
        # Step 3: Response Generation Guardrails
        if database_info:
            metadata['confidence'] = 1.0
            return database_info
        
        # GENTLE FALLBACK: If requested category or tribe does not exist in JSON
        if tribes and intent:
            tribe_name = tribes[0].title()
            category_name = intent.replace('_', ' ')
            return f"I do not currently have verified data regarding the {category_name} of the {tribe_name} people in my database."

        # Final fallback for non-specific queries
        return self._llm_fallback_response(query, metadata)

    def _additional_info_relevant(self, additional_info: str, intent: Optional[str], query: str) -> bool:
        if not additional_info:
            return False
        if not intent:
            return True
        q = normalize_text(query)
        info = normalize_text(additional_info)
        intent_keywords = {
            'history': ['history', 'colon', 'migration', 'origin', 'war'],
            'language': ['language', 'dialect', 'speak'],
            'food': ['food', 'cuisine', 'dish', 'eat', 'meal'],
            'marriage': ['marriage', 'wedding', 'bride', 'dowry'],
            'religion': ['religion', 'belief', 'faith', 'spirit', 'ancestor'],
            'culture': ['culture', 'custom', 'tradition'],
            'traditions': ['festival', 'ceremony', 'ritual', 'tradition'],
            'economy': ['economy', 'trade', 'work', 'livelihood'],
            'governance': ['govern', 'chief', 'fon', 'authority'],
        }
        keys = intent_keywords.get(intent, [])
        if not keys:
            return True
        return any(k in q for k in keys) or any(k in info for k in keys)

    def _get_intent_first_database_info(self, tribes: List[str], intent: Optional[str], query: str) -> Optional[str]:
        if not tribes:
            return None

        tribe = tribes[0]
        tribe_data = self.data_manager.get_tribe_data(tribe)
        if not tribe_data:
            return None

        section_map = {
            'overview': ['overview', 'history'],
            'culture': ['culture', 'traditions', 'social_organization'],
            'traditions': ['traditions', 'rituals', 'culture'],
            'marriage': ['marriage', 'traditions', 'culture'],
            'food': ['traditional_meals', 'food', 'subsistence_patterns'],
            'traditional_meals': ['traditional_meals', 'food'],
            'economy': ['economy', 'subsistence_patterns', 'trade_partners'],
            'language': ['languages', 'oral_traditions'],
            'religion': ['religion', 'spiritual_beliefs', 'worldview'],
            'rituals': ['rituals', 'traditions', 'music_dance'],
            'history': ['history', 'pre_contact_history', 'colonial_impact'],
            'leadership': ['leadership', 'governance', 'modern_governance'],
            'governance': ['governance', 'leadership', 'modern_governance'],
            'modern_life': ['modern_life', 'challenges', 'cultural_revitalization'],
            'arts_and_crafts': ['arts_and_crafts', 'visual_arts', 'traditional_technology'],
            'music_dance': ['music_dance', 'arts_and_crafts'],
            'spirituality': ['spirituality', 'spiritual_beliefs', 'worldview', 'rituals'],
            'core_identity': ['core_identity', 'location', 'population', 'overview'],
            'location': ['location', 'overview']
        }
        requested_sections = section_map.get(intent, ['overview'])
        sections = tribe_data.get('sections', {}) or {}
        
        # Find the best section content
        content = None
        for s in requested_sections:
            if sections.get(s):
                content = sections[s]
                break
        
        if not content:
            return None

        # Format according to "The Architect" strict constraint
        title = tribe_data.get('name') or tribe.title()
        intent_label = intent.replace('_', ' ') if intent else "culture"
        
        # Sentence 1: Engaging transition
        intro = f"Regarding the {intent_label} of the {title} people:"
        
        # Sentence 2-3: Core data (clean and dense)
        # We preserve structure for detail while ensuring cleanliness
        clean_content = content.strip()
        
        return f"{intro}\n\n{clean_content}"
    
    def _get_additional_info(self, query: str, tribes: List[str]) -> Optional[str]:
        """Get additional information without Wikipedia references"""
        if not tribes:
            return None
        
        enhancements = []
        
        for tribe in tribes[:1]:  # Limit to 1 tribe to avoid rate limiting
            try:
                wiki_info = self.wikipedia.search_wikipedia(query, tribe)
                if wiki_info and wiki_info.get('extract'):
                    extract = wiki_info['extract']
                    # Truncate if too long
                    if len(extract) > 400:
                        extract = extract[:400] + "..."
                    
                    # Just present the content without "According to Wikipedia" prefix
                    enhancements.append(extract)
                    break  # Only get one result to keep response manageable
            except Exception as e:
                self.logger.warning(f"Additional information enhancement failed for {tribe}: {e}")
                continue
        
        return "\n\n".join(enhancements) if enhancements else None
    
    def _get_enhanced_database_info(self, tribes: List[str], intent: str, query: str) -> Optional[str]:
        """Get enhanced database information with better tribe detection and question-specific responses"""
        if not tribes:
            return None
        
        info_parts = []
        
        for tribe in tribes[:2]:  # Limit to 2 tribes
            # Try multiple variations of the tribe name
            tribe_variations = [
                tribe.lower(),
                tribe.lower().replace('_', ''),
                tribe.lower().replace('-', ''),
                tribe.capitalize(),
                tribe.upper()
            ]
            
            tribe_data = None
            for variation in tribe_variations:
                tribe_data = self.data_manager.get_tribe_data(variation)
                if tribe_data:
                    break
            
            if tribe_data:
                sections = tribe_data.get('sections', {})
                
                # Enhanced intent matching with question keywords
                question_keywords = query.lower()
                section_found = False
                
                # Direct intent match first
                if intent and intent in sections and sections[intent]:
                    content = sections[intent]
                    section_title = intent.replace('_', ' ').title()
                    info_parts.append(f"Here's what I know about their {section_title.lower()}:\n\n{content}")
                    section_found = True
                
                # If no direct match, try keyword matching
                elif not section_found:
                    keyword_sections = {
                        'marriage': ['marriage', 'wedding', 'bride', 'groom', 'matrimony', 'spouse', 'family'],
                        'food': ['food', 'cuisine', 'eat', 'cooking', 'diet', 'meal', 'dish', 'recipe'],
                        'traditions': ['tradition', 'custom', 'ceremony', 'festival', 'ritual', 'celebration'],
                        'economy': ['economy', 'work', 'job', 'trade', 'business', 'livelihood', 'income'],
                        'governance': ['governance', 'leadership', 'chief', 'king', 'ruler', 'government', 'authority'],
                        'religion': ['religion', 'belief', 'spiritual', 'god', 'worship', 'prayer', 'sacred'],
                        'arts_and_crafts': ['art', 'craft', 'carving', 'pottery', 'weaving', 'music', 'dance'],
                        'history': ['history', 'origin', 'past', 'ancestor', 'migration', 'ancient', 'historical'],
                        'culture': ['culture', 'cultural', 'way of life', 'lifestyle', 'social'],
                        'overview': ['about', 'describe', 'tell me', 'who are', 'what are']
                    }
                    
                    # Find best matching section based on keywords
                    best_section = None
                    max_matches = 0
                    
                    for section_name, keywords in keyword_sections.items():
                        if section_name in sections and sections[section_name]:
                            matches = sum(1 for keyword in keywords if keyword in question_keywords)
                            if matches > max_matches:
                                max_matches = matches
                                best_section = section_name
                    
                    if best_section and sections[best_section]:
                        content = sections[best_section]
                        section_title = best_section.replace('_', ' ').title()
                        info_parts.append(f"Here's what I know about their {section_title.lower()}:\n\n{content}")
                        section_found = True
                
                # Fallback to priority sections if still no match
                if not section_found:
                    priority_sections = ['overview', 'culture', 'history', 'traditions']
                    for section in priority_sections:
                        if section in sections and sections[section]:
                            content = sections[section]
                            section_title = section.replace('_', ' ').title()
                            info_parts.append(f"Here's what I know about their {section_title.lower()}:\n\n{content}")
                            break
            else:
                # No data in our database - we'll rely on Wikipedia
                info_parts.append(f"While the {tribe.capitalize()} people aren't extensively covered in our current database, they're definitely an important part of Cameroon's cultural diversity.")
        
        return "\n\n".join(info_parts) if info_parts else None
    
    def _get_cultural_connections(self, tribes: List[str], intent: str) -> Optional[str]:
        """Generate cultural connections and recommendations"""
        if not tribes:
            return None
        
        connections = []
        
        # Add related cultural aspects based on intent
        cultural_suggestions = {
            "food": "If you're interested in their cuisine, you might also want to learn about their traditional festivals where these foods take center stage, their agricultural practices, or the fascinating cooking methods that have been passed down through generations.",
            "marriage": "Their marriage customs are just one part of their rich social fabric. You might also find it interesting to explore their family structures, inheritance systems, courtship rituals, and how extended families play such important roles in their society.",
            "history": "Their historical journey is quite fascinating! You could also explore their migration patterns, how they've interacted with neighboring tribes over the centuries, their resistance to colonial rule, and their contributions to Cameroon's independence movement.",
            "culture": "There's so much more to discover about their cultural expressions! Consider exploring their artistic traditions, music and dance, oral literature, and the amazing ways they've adapted to modern life while still preserving their heritage.",
            "religion": "Their spiritual beliefs are deeply woven into every aspect of their lives. It's worth learning how these beliefs influence their daily routines, governance systems, their relationship with nature, and how they've blended with world religions.",
            "economy": "Economically, they're quite resourceful! You might want to understand their traditional crafts, modern business networks, their tontine systems (rotating credit associations), and how they contribute to Cameroon's national economy.",
            "traditions": "Their traditional practices are incredibly rich and meaningful. Consider diving deeper into their ceremonial calendars, rites of passage, seasonal celebrations, and the deep meanings behind these time-honored practices."
        }
        
        if intent and intent in cultural_suggestions:
            connections.append(cultural_suggestions[intent])
        
        # Add comparative suggestions if multiple tribes
        if len(tribes) > 1:
            tribe_names = [tribe.capitalize() for tribe in tribes]
            connections.append(f"Since you're interested in multiple groups, it would be fascinating to compare how the {' and '.join(tribe_names)} approach {intent or 'cultural practices'} differently based on their unique histories and environments.")
        
        return "\n\n".join(connections) if connections else None
    
    def _select_response_strategy(self, query: str, tribes: List[str], intent: str, metadata: Dict) -> str:
        """Select the best response strategy based on query analysis"""
        
        # Strategy for comparison queries
        if intent == "compare" and len(tribes) >= 2:
            response = self._comparison_response(tribes, metadata)
            if response:
                return response
        
        # Strategy 1: Direct section access (fastest) - improved
        if tribes and intent:
            response = self._direct_section_response(query, tribes, intent, metadata)
            if response:
                return response
        
        # Strategy 2: Keyword-based search
        if tribes:
            response = self._keyword_search_response(query, tribes, metadata)
            if response:
                return response
        
        # Strategy 3: Content similarity search
        response = self._similarity_search_response(query, tribes, metadata)
        if response:
            return response
        
        # Strategy 4: LLM fallback
        return self._llm_fallback_response(query, metadata)
    
    def _comparison_response(self, tribes: List[str], metadata: Dict) -> Optional[str]:
        """Generate comparison response between tribes"""
        metadata['search_strategy'] = 'comparison'
        
        comparison_data = self.data_manager.compare_tribes(tribes)
        if not comparison_data:
            return None
        
        response_parts = [f"Comparison of {', '.join(tribes)}:\n"]
        
        # Add similarities with more detail
        if comparison_data.get("similarities"):
            response_parts.append("Shared Cultural Elements:")
            for category, content in comparison_data["similarities"].items():
                # Extract more detailed information for similarities
                detailed_content = self._extract_relevant_information(f"{category} similarity", content, category)
                response_parts.append(f"{category.replace('_', ' ').title()}: {detailed_content[:300]}{'...' if len(detailed_content) > 300 else ''}")
            response_parts.append("")
        
        # Add differences with more detail
        if comparison_data.get("differences"):
            response_parts.append("Distinctive Cultural Features:")
            for category, contents in comparison_data["differences"].items():
                response_parts.append(f"\n{category.replace('_', ' ').title()}:")
                for tribe, content in contents.items():
                    if content:
                        # Extract more detailed information for each tribe's perspective
                        detailed_content = self._extract_relevant_information(f"{category} {tribe}", content, category)
                        response_parts.append(f"{tribe.capitalize()}: {detailed_content[:250]}{'...' if len(detailed_content) > 250 else ''}")
                    else:
                        response_parts.append(f"{tribe.capitalize()}: Information not available")
        
        # Add conclusion
        response_parts.append(f"\nThis comparison of {', '.join(tribes)} reveals the rich diversity within Cameroonian tribal cultures. While these groups share certain regional or historical influences, each maintains unique traditions, social structures, and cultural practices that contribute to the country's vibrant cultural landscape. Understanding both their commonalities and distinctions helps appreciate the complexity and beauty of Cameroon's multicultural heritage.")
        
        metadata['confidence'] = 0.85
        return "\n".join(response_parts)

        return "\n".join(response_parts)
    
    def _direct_section_response(self, query: str, tribes: List[str], intent: str, metadata: Dict) -> Optional[str]:
        """Direct access to specific sections with improved targeting"""
        metadata['search_strategy'] = 'direct_section'
        
        responses = []
        for tribe in tribes:
            # Get the specific section requested
            content = self.data_manager.get_tribe_section(tribe, intent)
            if content:
                # Create a more focused response that directly addresses the query with more detail
                focused_content = self._extract_relevant_information(query, content, intent)
                poetic_intro = self._generate_poetic_intro(tribe, intent)
                responses.append(f"{poetic_intro}\n\n**{tribe.capitalize()} {intent.replace('_', ' ').title()}:**\n\n{focused_content}")
                metadata['confidence'] = 0.95
            else:
                # If the specific section isn't available, try to find relevant information in other sections
                tribe_data = self.data_manager.get_tribe_data(tribe)
                if tribe_data:
                    # Look for sections that might contain relevant information
                    relevant_sections = []
                    
                    # 1. Core Identity & Structure
                    if intent in ['core_identity', 'leadership']:
                        relevant_sections = ['overview', 'culture', 'governance', 'population', 'languages']
                    
                    # 2. Worldview & Spirituality
                    elif intent in ['worldview', 'spirituality', 'religion', 'rituals']:
                        relevant_sections = ['culture', 'traditions', 'overview', 'history']
                    
                    # 3. Material Culture & Subsistence
                    elif intent in ['subsistence', 'food']:
                        relevant_sections = ['economy', 'traditions', 'culture', 'history', 'overview', 'arts_and_crafts']
                    elif intent in ['technology', 'shelter', 'clothing']:
                        relevant_sections = ['arts_and_crafts', 'economy', 'culture', 'traditions', 'overview']
                    
                    # 4. History & Historical Trauma
                    elif intent in ['history', 'pre_contact', 'colonialism', 'resistance']:
                        relevant_sections = ['history', 'culture', 'overview', 'traditions']
                    
                    # 5. Contemporary Life & Politics
                    elif intent in ['modern_life', 'politics', 'revitalization']:
                        relevant_sections = ['governance', 'challenges', 'economy', 'culture', 'overview']
                    elif intent == 'economy':
                        relevant_sections = ['economy', 'governance', 'culture', 'overview']
                    
                    # 6. Arts, Knowledge & Expression
                    elif intent in ['oral_tradition', 'visual_arts', 'music_dance', 'traditional_knowledge']:
                        relevant_sections = ['arts_and_crafts', 'traditions', 'culture', 'overview']
                    
                    # Backwards compatibility
                    elif intent == 'marriage':
                        relevant_sections = ['traditions', 'culture', 'overview']
                    elif intent in ['religion', 'beliefs']:
                        relevant_sections = ['culture', 'traditions', 'overview']
                    elif intent == 'festivals':
                        relevant_sections = ['traditions', 'culture', 'overview']
                    elif intent == 'language':
                        relevant_sections = ['languages', 'culture', 'overview', 'traditions']
                    elif intent == 'overview':
                        # For overview, try to get the most comprehensive information
                        relevant_sections = ['overview', 'culture', 'history']
                    else:
                        # For any other intent, try multiple sections
                        relevant_sections = ['culture', 'traditions', 'overview', 'history']
                    
                    # Try each relevant section
                    found_relevant_info = False
                    for section_name in relevant_sections:
                        section_content = self.data_manager.get_tribe_section(tribe, section_name)
                        if section_content:
                            focused_content = self._extract_relevant_information(query, section_content, intent)
                            # Only add response if we found relevant information
                            if focused_content and not focused_content.startswith("No specific information"):
                                # Special handling for religious beliefs in the culture section
                                if intent in ['religion', 'beliefs'] and section_name in ['culture', 'overview', 'traditions']:
                                    # Check if the content contains religious beliefs information
                                    religious_terms = ['belief', 'religion', 'faith', 'worship', 'god', 'christian', 'islam', 'muslim', 'catholic', 'protestant', 'ancestor', 'deity', 'prayer', 'spiritual']
                                    if any(term in focused_content.lower() for term in religious_terms) or len(focused_content.split()) > 30:
                                        poetic_intro = self._generate_poetic_intro(tribe, intent)
                                        responses.append(f"{poetic_intro}\n\n**{tribe.capitalize()} Religious Beliefs:**\n\n{focused_content}")
                                        metadata['confidence'] = 0.9
                                        found_relevant_info = True
                                        break
                                
                                # Special handling for other intents
                                if intent == 'marriage' and section_name in ['traditions', 'culture', 'overview']:
                                    marriage_terms = ['marriage', 'wedding', 'bride', 'groom', 'dowry', 'courtship', 'ceremonies', 'arranged', 'polygyny', 'bride price', 'family alliances']
                                    if any(term in focused_content.lower() for term in marriage_terms) or len(focused_content.split()) > 30:
                                        poetic_intro = self._generate_poetic_intro(tribe, intent)
                                        responses.append(f"{poetic_intro}\n\n**{tribe.capitalize()} Marriage Customs:**\n\n{focused_content}")
                                        metadata['confidence'] = 0.85
                                        found_relevant_info = True
                                        break
                                
                                # General case with more descriptive header and context
                                poetic_intro = self._generate_poetic_intro(tribe, intent)
                                responses.append(f"{poetic_intro}\n\n**{tribe.capitalize()} {intent.replace('_', ' ').title()}:**\n\n{focused_content}")
                                metadata['confidence'] = 0.85
                                found_relevant_info = True
                                break
                    
                    # If no relevant section found, fall back to best section
                    if not found_relevant_info:
                        best_section = self._find_best_section(query, tribe_data)
                        if best_section:
                            focused_content = self._extract_relevant_information(query, best_section, intent)
                            poetic_intro = self._generate_poetic_intro(tribe, intent)
                            responses.append(f"{poetic_intro}\n\n**{tribe.capitalize()} {intent.replace('_', ' ').title()}:**\n\n{focused_content}")
                            metadata['confidence'] = 0.75
                        else:
                            # If we still can't find anything, provide a more informative response with specific suggestions for food queries
                            if intent == 'food':
                                responses.append(f"{tribe.capitalize()} Food and Diet Information:\n\nI don't have specific detailed information about the traditional foods and diet of the {tribe} people in my current database. However, many Cameroonian tribes share similar dietary patterns based on their geographic region:\n\n• **Coastal tribes** (like Duala, Sawa): Often rely on fish, seafood, plantains, cassava, and palm oil\n• **Highland tribes** (like Bamileke, Bamum): Typically consume yams, maize, beans, vegetables, and livestock\n• **Northern tribes** (like Fulani): Focus on cattle products (milk, meat), millet, sorghum, and pastoral foods\n• **Forest tribes** (like Baka, Beti): Hunt game, gather forest products, grow plantains and cassava\n\nFor specific information about {tribe.capitalize()} food culture, I recommend consulting:\n- Local community members or cultural centers\n- Anthropological studies on Cameroonian ethnic groups\n- Regional cookbooks or cultural documentation\n- Academic research on West/Central African food systems")
                            else:
                                responses.append(f"{tribe.capitalize()} Information Status:\n\nI don't have specific detailed information about {intent} for the {tribe} tribe in my database. This could be because:\n- The information is not extensively documented in my sources\n- The topic falls outside the scope of my current knowledge base\n- The tribe's cultural practices in this area are primarily oral traditions not captured in written records\n- The specific aspect of {intent} may be less prominent or differently expressed in this community\n\nFor tribes with limited documentation, I recommend consulting academic sources, cultural institutions, community elders, or anthropological studies for more comprehensive information. Cultural practices are dynamic and continue to evolve, making ongoing research and community engagement essential for a complete understanding.")
                            metadata['confidence'] = 0.4
                    
                    if responses:
                        return "\n\n".join(responses)
                return None
    
    def _keyword_search_response(self, query: str, tribes: List[str], metadata: Dict) -> Optional[str]:
        """Search using extracted keywords with improved targeting"""
        metadata['search_strategy'] = 'keyword_search'
        
        # Extract query keywords
        query_words = [word for word in query.split() if len(word) > 2]
        
        # Search by keywords
        search_results = self.data_manager.search_by_keywords(query_words)
        
        if search_results:
            relevant_tribes = [tribe for tribe, score in search_results[:5] if score > 0.2]  # Increased from 3 to 5
            # Filter by mentioned tribes if any
            if tribes:
                relevant_tribes = [t for t in relevant_tribes if t in tribes]
            
            if relevant_tribes:
                response_parts = []
                for tribe in relevant_tribes:
                    tribe_data = self.data_manager.get_tribe_data(tribe)
                    if tribe_data:
                        # Get more comprehensive information by looking at multiple sections
                        sections = tribe_data.get('sections', {})
                        if sections:
                            # Collect information from all relevant sections
                            comprehensive_info = []
                            for section_name, section_content in sections.items():
                                if section_content:
                                    # Extract relevant information from each section
                                    relevant_content = self._extract_relevant_information(query, section_content, None)
                                    if relevant_content and not relevant_content.startswith("No specific information"):
                                        comprehensive_info.append(f"{section_name.replace('_', ' ').title()}:\n{relevant_content}")
                            
                            if comprehensive_info:
                                # Combine information from multiple sections (limit to 2 for conciseness)
                                combined_content = "\n\n".join(comprehensive_info[:2])
                                # Determine the primary intent for poetic intro
                                primary_intent = metadata.get('intent_detected', 'overview')
                                poetic_intro = self._generate_poetic_intro(tribe, primary_intent)
                                response_parts.append(f"{poetic_intro}\n\n**{tribe.capitalize()} Cultural Profile:**\n\n{combined_content}")
                
                if response_parts:
                    metadata['confidence'] = 0.8
                    return "\n\n".join(response_parts)
        
        return None
    
    def _similarity_search_response(self, query: str, tribes: List[str], metadata: Dict) -> Optional[str]:
        """Search using content similarity with improved targeting"""
        metadata['search_strategy'] = 'similarity_search'
        
        search_results = self.data_manager.search_by_content(query, tribes)
        
        if search_results:
            # Group by tribe
            tribe_results = defaultdict(list)
            for tribe, section, score in search_results[:5]:
                if score > 0.15:  # Minimum similarity threshold
                    tribe_results[tribe].append((section, score))
            
            if tribe_results:
                response_parts = []
                for tribe, sections in tribe_results.items():
                    best_section = sections[0][0]  # Highest scoring section
                    content = self.data_manager.get_tribe_section(tribe, best_section)
                    if content:
                        # Extract only the most relevant information
                        focused_content = self._extract_relevant_information(query, content, best_section)
                        primary_intent = metadata.get('intent_detected', best_section)
                        poetic_intro = self._generate_poetic_intro(tribe, primary_intent)
                        response_parts.append(f"{poetic_intro}\n\n**{tribe.capitalize()} {best_section.replace('_', ' ').title()}:**\n\n{focused_content}")
                
                if response_parts:
                    metadata['confidence'] = 0.6
                    return "\n\n".join(response_parts)
        
        return None
    
    def _llm_fallback_response(self, query: str, metadata: Dict) -> str:
        """LLM-enhanced response as fallback with improved structure"""
        metadata['search_strategy'] = 'llm_fallback'
        
        # Try to get some relevant context
        context_data = {}
        mentioned_tribes = extract_tribe_names(query)
        
        if mentioned_tribes:
            for tribe in mentioned_tribes[:2]:  # Limit to 2 tribes
                tribe_data = self.data_manager.get_tribe_data(tribe)
                if tribe_data:
                    # Get overview or best matching section
                    overview = tribe_data.get('sections', {}).get('overview', '')
                    if overview:
                        context_data[f"{tribe}_overview"] = overview
        
        # Try LLM enhancement
        if context_data and self.ollama_client.available:
            llm_response = self.ollama_client.enhance_response(query, context_data)
            if llm_response:
                metadata['llm_used'] = True
                metadata['confidence'] = 0.5
                return f"{llm_response}\n\nBased on available tribal data"
        
        # Enhanced fallback without LLM - provide more detailed responses from structured data
        if context_data:
            detailed_response = self._generate_detailed_response_from_context(query, context_data)
            if detailed_response:
                metadata['confidence'] = 0.6
                return detailed_response
        
        # Final fallback
        return ("I don't have specific information about that in my database. "
                "Try asking about the general culture, history, traditions, or customs "
                "of the tribes I know about!")

    def _generate_detailed_response_from_context(self, query: str, context_data: Dict) -> str:
        """Generate a more detailed response from structured context data"""
        if not context_data:
            return None
            
        response_parts = []
        
        # Add a more detailed introduction
        response_parts.append("Based on the comprehensive information I have about Cameroonian tribes:")
        
        for tribe_context, content in context_data.items():
            tribe_name = tribe_context.replace("_overview", "").capitalize()
            response_parts.append(f"\n{tribe_name} People - Detailed Cultural Profile:")
            
            # Break down the content into more readable sections with more detail
            if content:
                lines = content.split('\n')
                current_section = ""
                
                for line in lines:
                    if line.strip().startswith('-'):
                        # This is a list item
                        if not current_section:
                            current_section = "Key Cultural Aspects:"
                        response_parts.append(f"  {line.strip()}")
                    elif ':' in line and len(line) < 50:
                        # This looks like a section header
                        if current_section:
                            response_parts.append("")  # Add spacing
                        enhancements.append(f"Here's some additional information about the {tribe.capitalize()} people:\n\n{content}")
                        response_parts.append(f"{line.strip()}")
                        current_section = line.strip()
                    elif line.strip():
                        # Regular content - break long lines into sentences for better readability
                        if len(line) > 100:
                            sentences = line.split('. ')
                            for i, sentence in enumerate(sentences):
                                if sentence.strip():
                                    if i == 0:
                                        response_parts.append(f"  {sentence.strip()}.")
                                    else:
                                        response_parts.append(f"    {sentence.strip()}.")
                        else:
                            response_parts.append(f"  {line.strip()}")
        
        # Add a more elaborate conclusion with additional context
        response_parts.append("\n\nAdditional Context:")
        response_parts.append("This information represents the rich cultural heritage of Cameroonian tribes. Each tribe has unique traditions, beliefs, and practices that contribute to the diverse cultural landscape of Cameroon. For more specific details about any aspect mentioned above, please ask targeted questions about particular tribes or cultural elements.")
        
        return '\n'.join(response_parts)

    def _find_best_section(self, query: str, tribe_data: Dict) -> Optional[str]:
        """Find the most relevant section for a query"""
        if not tribe_data:
            return None
        
        sections = tribe_data.get('sections', {})
        if not sections:
            return None
        
        # Calculate similarity for each section
        best_score = 0
        best_content = None
        best_section_name = None
        
        for section, content in sections.items():
            if content:
                score = calculate_similarity(query, content)
                if score > best_score:
                    best_score = score
                    best_content = content
                    best_section_name = section
        
        # Return more content - up to 600 characters instead of 400
        return best_content[:600] + "..." if best_content and len(best_content) > 600 else best_content

    def _extract_relevant_information(self, query: str, content: str, intent: str) -> str:
        """Extract the most relevant information from content based on the query"""
        if not content:
            return "No specific information available."
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        # Initialize relevant paragraphs list
        relevant_paragraphs = []
        
        # If we have a specific intent, try to find relevant paragraphs
        if intent:
            # Special handling for specific intents with more comprehensive keyword matching
            if intent == 'marriage':
                # Look for paragraphs specifically mentioning marriage
                for paragraph in paragraphs:
                    if 'marriage' in paragraph.lower() or 'bride' in paragraph.lower() or 'groom' in paragraph.lower() or 'dowry' in paragraph.lower() or 'bride price' in paragraph.lower() or 'courtship' in paragraph.lower() or 'wedding' in paragraph.lower() or 'polygyny' in paragraph.lower() or 'polygamy' in paragraph.lower():
                        relevant_paragraphs.append(paragraph)
            elif intent == 'religion' or intent == 'beliefs':
                # Look for paragraphs specifically mentioning religious beliefs with more comprehensive keywords
                religious_keywords = [
                    'belief', 'religion', 'religious', 'faith', 'worship', 'god', 'christian', 'islam', 'muslim', 
                    'catholic', 'protestant', 'ancestor', 'deity', 'prayer', 'worship', 'spiritual', 'animist', 
                    'sunni', 'maliki', 'sufi', 'quranic', 'syncretic', 'hemba', 'ngi', 'epasa', 'traditional belief',
                    'supreme being', 'ancestral', 'shrine', 'ritual', 'ceremony', 'sacred', 'divine', 'cult', 'veneration'
                ]
                # Special handling for Bassa tribe - look for the "Beliefs:" subsection
                if 'beliefs:' in content.lower():
                    # Extract the Beliefs subsection with more context
                    content_lines = content.split('\n')
                    beliefs_section = []
                    in_beliefs_section = False
                    section_headers = []
                    
                    for line in content_lines:
                        line_stripped = line.strip()
                        # Check if this is a section header (not a list item)
                        is_section_header = (line_stripped and 
                                           not line_stripped.startswith('-') and 
                                           ':' in line_stripped and 
                                           len(line_stripped) < 50)
                        
                        if 'beliefs:' in line.lower():
                            in_beliefs_section = True
                            beliefs_section.append(line)
                            if is_section_header:
                                section_headers.append('beliefs')
                        elif in_beliefs_section and is_section_header:
                            # This is a new section header
                            header_name = line_stripped.lower().rstrip(':')
                            if header_name in section_headers:
                                # We've reached a duplicate section, stop here
                                break
                            else:
                                # Add this section header and continue
                                section_headers.append(header_name)
                                beliefs_section.append(line)
                        elif in_beliefs_section:
                            # This is content within the beliefs section
                            beliefs_section.append(line)
                    
                    if beliefs_section:
                        relevant_paragraphs.append('\n'.join(beliefs_section))
                else:
                    # General approach for other tribes or when no specific beliefs section found
                    for paragraph in paragraphs:
                        if any(keyword in paragraph.lower() for keyword in religious_keywords):
                            relevant_paragraphs.append(paragraph)
            elif intent == 'festivals':
                # Look for paragraphs specifically mentioning festivals with more comprehensive keywords
                festival_keywords = [
                    'festival', 'celebration', 'ceremony', 'event', 'commemoration', 'annual', 'seasonal', 
                    'harvest', 'lem', 'nguon', 'laela', 'assiko', 'ngondo', 'gerewol', 'lala', 'lela', 
                    'cultural celebration', 'traditional celebration', 'ritual celebration', 'community gathering',
                    'traditional festival', 'cultural festival', 'annual celebration', 'seasonal celebration',
                    'nguon festival', 'lem festival', 'lala festival', 'lela festival'
                ]
                # Special handling for cases where there might not be specific festival information
                festival_paragraphs = []
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in festival_keywords):
                        festival_paragraphs.append(paragraph)
                
                if festival_paragraphs:
                    relevant_paragraphs.extend(festival_paragraphs)
                else:
                    # If no specific festival information, look for general cultural celebrations
                    general_keywords = ['celebration', 'ceremony', 'annual', 'traditional']
                    for paragraph in paragraphs:
                        if any(keyword in paragraph.lower() for keyword in general_keywords):
                            relevant_paragraphs.append(paragraph)
            elif intent == 'spirituality':
                # Look for paragraphs specifically mentioning spiritual practices
                spiritual_keywords = [
                    'spiritual', 'belief', 'ritual', 'sacred', 'rituals', 'animism', 'jengi', 'forest spirit',
                    'shaman', 'ceremony', 'worship', 'ancestral', 'tradition', 'practice'
                ]
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in spiritual_keywords):
                        relevant_paragraphs.append(paragraph)
            elif intent == 'economy':
                # Look for paragraphs specifically mentioning economic activities with more comprehensive keywords
                economic_keywords = [
                    'economy', 'economic', 'trade', 'business', 'work', 'job', 'occupation', 'farming', 
                    'agriculture', 'commerce', 'livestock', 'craft', 'income', 'wealth', 'market', 'pastoral',
                    'commerce', 'trading', 'earning', 'production', 'industry', 'employment', 'profession',
                    'subsistence', 'cash crop', 'export', 'import', 'barter', 'currency', 'financial'
                ]
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in economic_keywords):
                        relevant_paragraphs.append(paragraph)
            elif intent == 'food':
                # Look for paragraphs specifically mentioning food and diet
                food_keywords = [
                    'food', 'eat', 'cuisine', 'dish', 'meal', 'cook', 'recipe', 'diet', 'crop', 'agriculture', 
                    'hunt', 'fish', 'feast', 'ingredient', 'staple', 'cassava', 'plantain', 'yam', 'rice', 
                    'maize', 'corn', 'meat', 'chicken', 'beef', 'goat', 'palm oil', 'groundnut', 'beans',
                    'vegetable', 'fruit', 'harvest', 'farming', 'cultivation', 'fishing', 'hunting',
                    'traditional food', 'local cuisine', 'cooking method', 'preparation', 'nutrition'
                ]
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in food_keywords):
                        relevant_paragraphs.append(paragraph)
            else:
                # Check if paragraph contains keywords related to the intent
                intent_keywords = {
                    'marriage': ['marriage', 'wedding', 'bride', 'groom', 'dowry', 'courtship', 'ceremonies', 'arranged', 'polygyny', 'bride price', 'family alliances', 'polygamy', 'nuptial', 'matrimony'],
                    'religion': ['religion', 'religious', 'belief', 'faith', 'worship', 'god', 'spiritual', 'ancestor', 'christian', 'islam', 'muslim', 'catholic', 'protestant', 'syncretic', 'deity', 'prayer', 'traditional belief', 'supreme being', 'ancestral', 'shrine', 'ritual'],
                    'economy': ['economy', 'economic', 'trade', 'business', 'work', 'job', 'occupation', 'farming', 'agriculture', 'commerce', 'livestock', 'craft', 'income', 'wealth', 'market', 'pastoral', 'commerce', 'trading', 'earning', 'production', 'industry', 'employment', 'profession', 'subsistence', 'cash crop', 'export', 'import', 'barter', 'currency', 'financial'],
                    'festivals': ['festival', 'celebration', 'ceremony', 'event', 'commemoration', 'annual', 'seasonal', 'harvest', 'cultural festival', 'lem', 'nguon', 'laela', 'assiko', 'ngondo', 'gerewol', 'lela', 'traditional celebration', 'cultural celebration'],
                    'language': ['language', 'speak', 'dialect', 'tongue', 'communication', 'linguistic', 'words', 'vocabulary', 'oral', 'written', 'shüpamom', 'lamnso', 'communication system'],
                    'traditions': ['tradition', 'ceremony', 'festival', 'rite', 'ritual', 'custom', 'celebration', 'practice', 'ancestral', 'cultural', 'heritage'],
                    'spirituality': ['spiritual', 'belief', 'ritual', 'sacred', 'rituals', 'animism', 'jengi', 'forest spirit', 'shaman', 'ceremony', 'worship', 'ancestral', 'tradition', 'practice'],
                    'food': ['food', 'eat', 'cuisine', 'dish', 'meal', 'cook', 'recipe', 'diet', 'crop', 'agriculture', 'hunt', 'fish', 'feast', 'ingredient', 'staple', 'cassava', 'plantain', 'yam', 'rice', 'maize', 'corn', 'meat', 'chicken', 'beef', 'goat', 'palm oil', 'groundnut', 'beans', 'vegetable', 'fruit', 'harvest', 'farming', 'cultivation', 'fishing', 'hunting', 'traditional food', 'local cuisine', 'cooking method', 'preparation', 'nutrition']
                }
                
                keywords = intent_keywords.get(intent, [])
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in keywords):
                        relevant_paragraphs.append(paragraph)
        
        # If we found relevant paragraphs, return more of them (up to 10 instead of 8)
        if relevant_paragraphs:
            # Remove duplicate paragraphs
            unique_paragraphs = []
            seen_content = set()
            for paragraph in relevant_paragraphs:
                # Create a normalized version for comparison
                normalized = ' '.join(paragraph.lower().split())
                if normalized not in seen_content:
                    unique_paragraphs.append(paragraph)
                    seen_content.add(normalized)
            
            # Return concise, focused information - up to 2 paragraphs, max 800 characters
            result = '\n\n'.join(unique_paragraphs[:2])
            return result[:800] + "..." if len(result) > 800 else result
    
        # If no specific intent or no relevant paragraphs found, find paragraphs most similar to query
        best_paragraphs = []
        query_words = set(query.lower().split())
        
        for paragraph in paragraphs:
            # Calculate relevance based on word overlap
            paragraph_words = set(paragraph.lower().split())
            overlap = len(query_words.intersection(paragraph_words))
            
            if overlap > 0:
                best_paragraphs.append((paragraph, overlap))
        
        # Sort by relevance and take top paragraphs (more paragraphs now)
        best_paragraphs.sort(key=lambda x: x[1], reverse=True)
        
        if best_paragraphs:
            # Remove duplicates
            unique_best = []
            seen_content = set()
            for paragraph, score in best_paragraphs:
                normalized = ' '.join(paragraph.lower().split())
                if normalized not in seen_content:
                    unique_best.append((paragraph, score))
                    seen_content.add(normalized)
            
            # Return concise information - up to 2 paragraphs
            result = '\n\n'.join([p[0] for p in unique_best[:2]])
            return result[:800] + "..." if len(result) > 800 else result
        
        # If no relevant paragraphs found, return first paragraphs with truncation (more paragraphs now)
        first_paragraphs = paragraphs[:3] if len(paragraphs) >= 3 else paragraphs
        first_content = '\n\n'.join(first_paragraphs) if first_paragraphs else content
        
        # If we still don't have enough content and have an intent, try to extract more broadly
        if intent and len(first_content.split()) < 50:
            # Try to get more paragraphs to provide a more comprehensive response
            more_paragraphs = paragraphs[:5] if len(paragraphs) >= 5 else paragraphs
            first_content = '\n\n'.join(more_paragraphs) if more_paragraphs else content
        
        return first_content[:2000] + "..." if len(first_content) > 2000 else first_content

    def _generate_humanized_intro(self, tribe: str, intent: str) -> str:
        """Generate a natural, humanized introduction for the tribe with unique intros"""
        
        # First check if tribe has a unique introduction in database
        tribe_data = self.data_manager.get_tribe_data(tribe.lower())
        if tribe_data and 'unique_intro' in tribe_data:
            unique_intro = tribe_data['unique_intro']
            # Add intent-specific transition
            topic_transitions = {
                "food": "When it comes to their cuisine and dietary traditions,",
                "marriage": "Their marriage customs and family traditions are particularly fascinating.",
                "history": "Their historical journey through the centuries is quite remarkable.",
                "culture": "What's really captivating about their cultural practices is",
                "religion": "Their spiritual beliefs and religious practices are deeply meaningful.",
                "economy": "Economically, they've developed some truly ingenious approaches.",
                "traditions": "Their ceremonial traditions and customs are incredibly rich.",
                "governance": "Their traditional leadership and governance systems are quite sophisticated.",
                "arts": "Their artistic traditions and craftsmanship are truly impressive.",
                "architecture": "Their building techniques and architectural styles are fascinating."
            }
            transition = topic_transitions.get(intent, "Let me tell you more about them.")
            return f"{unique_intro} {transition}"
        
        # Create natural, conversational introductions for major tribes
        humanized_intros = {
            "bamileke": "Let me tell you about the Bamileke people - they're truly fascinating! Living in the misty highlands of Cameroon, they've built some of the most sophisticated kingdoms you'll ever hear about. For centuries, they've been known for their incredible entrepreneurial spirit and those beautiful terraced gardens that seem to climb right up to the clouds.",
            
            "bamum": "The Bamum people have such an incredible story! You know what's amazing about them? They actually created their own writing system - how cool is that? Their Sultan Njoya was a real visionary who turned Foumban into this amazing center of learning and culture.",
            
            "fulani": "Oh, the Fulani people - now there's a group with wanderlust in their DNA! These nomadic herders have been traveling across West and Central Africa for over a thousand years with their cattle. You can almost hear the gentle bells of their zebu cattle echoing across the savannas.",
            
            "duala": "The Duala people are the masters of Cameroon's waterways! Living where the Wouri River meets the Atlantic Ocean, they've been the country's gateway to the world for generations. They're natural-born traders and have this beautiful relationship with the water that's just captivating.",
            
            "bassa": "The Bassa people are the guardians of some really ancient traditions. Living in the lush forests of central Cameroon, they've maintained this incredible connection to their ancestral ways while also being fierce defenders of their independence throughout history.",
            
            "nsaw": "Up in the Grassfields, you'll find the Nsaw people who've built one of Cameroon's most respected kingdoms. Their capital, Kumbo, sits high in the mountains, and their Fon (king) is revered throughout the region. They're known for their strong sense of unity and honor.",
            
            "bakweri": "The Bakweri people live in the shadow of Mount Cameroon - literally! This active volcano has shaped not just their landscape but their entire culture. They've learned to work with this powerful mountain, and their stories about it are absolutely fascinating.",
            
            "beti": "The Beti people call the rainforests of southern Cameroon home. They're incredible farmers who've figured out how to thrive in the forest environment, growing everything from cocoa to plantains. Their connection to the forest is something really special.",
            
            "tikar": "The Tikar people are like the cultural crossroads of Cameroon! They're believed to be the ancestors of many other groups in the region, and their influence has spread far and wide. They're master craftspeople and have this rich tradition of storytelling.",
            
            "sawa": "The Sawa people are Cameroon's coastal dwellers who've made the sea their second home. From fishing to trading, they've built their entire way of life around the rhythms of the ocean and rivers."
        }
        
        # Get specific intro or create a natural generic one
        base_intro = humanized_intros.get(tribe.lower(), 
            f"The {tribe.capitalize()} people are one of Cameroon's diverse ethnic groups, each with their own unique story to tell. While they might not be as well-known as some of the larger tribes, they've contributed their own special thread to the rich tapestry of Cameroonian culture.")
        
        # Add natural topic transitions
        topic_transitions = {
            "food": "Speaking of their cuisine, you're in for a treat!",
            "marriage": "Their marriage traditions are particularly interesting.",
            "history": "Their historical journey is quite remarkable.",
            "culture": "What's really fascinating about their culture is",
            "religion": "Their spiritual beliefs are deeply rooted and meaningful.",
            "economy": "Economically, they've found some really clever ways to thrive.",
            "traditions": "Their traditional practices have been passed down for generations.",
            "governance": "Their leadership systems are quite sophisticated.",
            "arts": "Their artistic expressions are truly remarkable.",
            "architecture": "Their building techniques are fascinating."
        }
        
        transition = topic_transitions.get(intent, "Let me share what I know about them.")
        
        return f"{base_intro} {transition}"

    def get_analytics(self) -> Dict:
        """Get chatbot analytics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'total_queries': self.query_stats['total'],
            'avg_response_time': round(avg_response_time, 3),
            'min_response_time': round(min(self.response_times), 3) if self.response_times else 0,
            'max_response_time': round(max(self.response_times), 3) if self.response_times else 0,
            'available_tribes': len(self.data_manager.data),
            'total_sections': sum(len(data.get('sections', {})) for data in self.data_manager.data.values())
        }


# =============================================================================
# Main Chatbot
# =============================================================================

class AdvancedTribesBot:
    """Advanced JSON-based chatbot for Cameroonian tribes"""
    
    def __init__(self, json_path: str, model_name: str = OLLAMA_MODEL, verbose: bool = False):
        self.logger = setup_logging(verbose)
        self.logger.info("Initializing Advanced Tribes Bot...")
        
        # Load supported tribes dynamically
        global SUPPORTED_TRIBES
        SUPPORTED_TRIBES = load_supported_tribes(json_path)
        self.logger.info(f"Loaded {len(SUPPORTED_TRIBES)} tribes from data file")
        
        # Initialize components
        self.data_manager = TribesDataManager(json_path)
        self.intent_detector = IntentDetector()
        self.ollama_client = OllamaClient(model_name)
        self.speech_interface = SpeechInterface()
        self.response_generator = SmartResponseGenerator(
            self.data_manager, self.intent_detector, self.ollama_client
        )
        
        # Configuration
        self.input_mode = "text"
        self.use_speech_output = TTS_AVAILABLE
        self.show_metadata = verbose
        
        self.logger.info("Bot initialization complete")
    
    def show_banner(self):
        """Display enhanced welcome banner"""
        stats = self.response_generator.get_analytics()
        
        # Determine which LLM is being used
        llm_status = "Not available"
        if self.ollama_client.available:
            llm_status = "Ollama ✓ Available"
        
        banner = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║            🇨🇲 SUPER INTELLIGENT CAMEROONIAN TRIBES BOT 🇨🇲                ║
╠════════════════════════════════════════════════════════════════════════════╣
║  🎯 Comprehensive responses with poetic tribal histories                  ║
║  📊 Data: {stats['available_tribes']} tribes, {stats['total_sections']} sections + Wikipedia integration          ║
║  🤖 LLM: {llm_status}                                       ║
║  🎤 Speech: {'✓ Available' if SR_AVAILABLE else '✗ Not available'}                                   ║
║  📚 Wikipedia: ✓ Enhanced with real-time information                     ║
║  🎭 Poetic Histories: ✓ Cultural context with artistic flair            ║
║                                                                            ║
║  Features: Poetic introductions + Database + Wikipedia + Cultural tips   ║
║                                                                            ║
║  Commands: :help :mode :stats :quit                                       ║
╚════════════════════════════════════════════════════════════════════════════╝

💬 Current mode: {self.input_mode.upper()} input, {'SPEECH' if self.use_speech_output else 'TEXT'} output
🌟 Enhanced with poetic tribal histories and Wikipedia integration!
        """
        print(banner)
    
    def get_user_input(self) -> Optional[str]:
        """Get user input based on current mode"""
        if self.input_mode == "speech" and SR_AVAILABLE:
            return self.speech_interface.listen()
        else:
            try:
                return input("\n💬 You: ").strip()
            except (KeyboardInterrupt, EOFError):
                return ":quit"
    
    def process_command(self, user_input: str) -> bool:
        """Process special commands"""
        command = user_input.lower()
        
        if command in [":quit", "quit", "exit", ":exit", "bye"]:
            return True
        
        elif command in [":help", "help"]:
            self.show_help()
            return True
        
        elif command in [":mode", "mode"]:
            self.toggle_input_mode()
            return True
        
        elif command in [":stats", "stats", ":analytics"]:
            self.show_analytics()
            return True
        
        elif command in [":tribes", "tribes"]:
            self.show_tribes_info()
            return True
        
        elif command in [":categories", "categories"]:
            self.show_categories()
            return True
            
        # Gemini integration removed - using Ollama only
        return False
        
        return False
    
    def show_help(self):
        """Display help information"""
        help_text = """
🆘 HELP - Available Commands and Features

📋 Commands:
   :help        - Show this help
   :mode        - Toggle between text and speech input
   :stats       - Show chatbot analytics and performance
   :tribes      - List available tribes and their data status
   :categories  - Show available content categories

   :quit        - Exit the chatbot

💬 Query Examples:
   "Tell me about Bakossi culture"
   "What are Bamum marriage traditions?"
   "How do Bamileke people celebrate festivals?"
   "What is the history of the Nso tribe?"
   "Compare Bassa and Awing food culture"
   "Explain the cultural significance of traditional masks"

🎯 Smart Features:
   • Multi-tribe queries: Ask about multiple tribes at once
   • Intent detection: Automatically categorizes your questions
   • Fuzzy matching: Handles typos and variations
   • Context-aware: Provides relevant information based on query type
   • LLM enhancement: Uses AI to create natural responses from data

🔧 Input Modes:
   • TEXT: Type your questions
   • SPEECH: Speak your questions (requires microphone)

📊 The bot uses structured JSON data for fast, accurate responses!
        """
        print(help_text)
    
    def toggle_input_mode(self):
        """Toggle between text and speech input modes"""
        if self.input_mode == "text":
            if SR_AVAILABLE:
                self.input_mode = "speech"
                print("🎤 Switched to SPEECH input mode")
                print("💡 Tip: Speak clearly and wait for the listening prompt")
            else:
                print("❌ Speech recognition not available")
                print("💡 Install requirements: pip install speechrecognition pyaudio")
        else:
            self.input_mode = "text"
            print("⌨️ Switched to TEXT input mode")
    
    def show_analytics(self):
        """Display chatbot analytics"""
        stats = self.response_generator.get_analytics()
        
        print(f"""
📊 CHATBOT ANALYTICS

🔢 Query Statistics:
   • Total queries processed: {stats['total_queries']}
   • Average response time: {stats['avg_response_time']}s
   • Fastest response: {stats['min_response_time']}s
   • Slowest response: {stats['max_response_time']}s

📚 Data Statistics:
   • Tribes with data: {stats['available_tribes']}/6
   • Total content sections: {stats['total_sections']}
   • Data source: {self.data_manager.metadata.get('source_file', 'Unknown')}
   • Last updated: {self.data_manager.metadata.get('conversion_date', 'Unknown')}

🤖 System Status:
   • LLM available: {'Yes' if self.ollama_client.available else 'No'}
   • Speech input: {'Yes' if SR_AVAILABLE else 'No'}
   • Speech output: {'Yes' if TTS_AVAILABLE else 'No'}
   • Current mode: {self.input_mode.upper()}
        """)
    
    def show_tribes_info(self):
        """Display information about available tribes"""
        print("\n👥 AVAILABLE TRIBES DATA\n")
        
        for tribe_name in SUPPORTED_TRIBES:
            tribe_data = self.data_manager.get_tribe_data(tribe_name)
            
            if tribe_data:
                sections = tribe_data.get('sections', {})
                available_sections = [cat for cat, content in sections.items() if content]
                word_count = tribe_data.get('metadata', {}).get('total_words', 0)
                confidence = tribe_data.get('metadata', {}).get('confidence_score', 0)
                
                status = "✅ Rich data" if len(available_sections) >= 5 else "⚠️ Limited data" if available_sections else "❌ No data"
                
                print(f"🔹 {tribe_name.capitalize()}")
                print(f"   Status: {status}")
                print(f"   Sections: {len(available_sections)}/12 ({', '.join(available_sections[:5])}{'...' if len(available_sections) > 5 else ''})")
                print(f"   Content: {word_count} words (confidence: {confidence})")
                
                aliases = tribe_data.get('aliases', [])
                if aliases:
                    print(f"   Aliases: {', '.join(aliases)}")
                print()
            else:
                print(f"🔹 {tribe_name.capitalize()}")
                print(f"   Status: ❌ No data available")
                print()
    
    def show_categories(self):
        """Display available content categories"""
        all_categories = set()
        for tribe_data in self.data_manager.data.values():
            all_categories.update(tribe_data.get('sections', {}).keys())
        
        print(f"\n📂 AVAILABLE CONTENT CATEGORIES ({len(all_categories)} total)\n")
        
        # Group categories by type
        category_groups = {
            "Basic Info": ["overview", "history", "culture"],
            "Social": ["marriage", "traditions", "religion", "language"],
            "Lifestyle": ["food", "economy", "art", "music", "festivals"],
        }
        
        for group_name, group_categories in category_groups.items():
            print(f"🏷️ {group_name}:")
            for category in group_categories:
                if category in all_categories:
                    # Count tribes with this category
                    tribe_count = sum(1 for tribe_data in self.data_manager.data.values() 
                                    if tribe_data.get('sections', {}).get(category))
                    print(f"   • {category.title()} ({tribe_count}/6 tribes)")
            print()
    
    def get_available_categories(self, tribe_name: Optional[str] = None) -> List[str]:
        """Get available content categories"""
        if tribe_name:
            tribe_data = self.get_tribe_data(tribe_name)
            if tribe_data:
                return [cat for cat, content in tribe_data.get('sections', {}).items() if content]
        else:
            categories = set()
            for tribe_data in self.data.values():
                categories.update(tribe_data.get('sections', {}).keys())
            return list(categories)
        return []
    
    def compare_tribes(self, tribe_names: List[str]) -> Dict:
        """Compare multiple tribes and return similarities and differences"""
        if len(tribe_names) < 2:
            return {}
        
        comparison = {
            "tribes": tribe_names,
            "similarities": {},
            "differences": {}
        }
        
        # Get data for all tribes
        tribe_data_list = [self.get_tribe_data(name) for name in tribe_names]
        
        # Find common categories
        all_categories = set()
        for tribe_data in tribe_data_list:
            if tribe_data:
                all_categories.update(tribe_data.get('sections', {}).keys())
        
        # Compare each category
        for category in all_categories:
            category_contents = []
            for tribe_data in tribe_data_list:
                if tribe_data:
                    content = tribe_data.get('sections', {}).get(category, "")
                    category_contents.append(content)
                else:
                    category_contents.append("")
            
            # Check if all contents are similar (simple approach)
            if all(content == category_contents[0] for content in category_contents):
                if category_contents[0]:  # Not empty
                    comparison["similarities"][category] = category_contents[0]
            else:
                # Different contents - add to differences
                comparison["differences"][category] = dict(zip(tribe_names, category_contents))
        
        return comparison
    
    def display_response(self, response: str, metadata: Dict):
        """Display response with optional metadata and speech"""
        print(f"\n🤖 Bot: {response}")
        
        # Show metadata if verbose mode
        if self.show_metadata:
            print(f"\n📊 Response Metadata:")
            print(f"   • Strategy: {metadata.get('search_strategy', 'unknown')}")
            print(f"   • Confidence: {metadata.get('confidence', 0):.1f}")
            print(f"   • Response time: {metadata.get('response_time', 0):.3f}s")
            print(f"   • LLM used: {'Yes' if metadata.get('llm_used') else 'No'}")
            print(f"   • Wikipedia used: {'Yes' if metadata.get('wikipedia_used') else 'No'}")
            if metadata.get('tribes_mentioned'):
                print(f"   • Tribes: {', '.join(metadata['tribes_mentioned'])}")
            if metadata.get('intent_detected'):
                print(f"   • Intent: {metadata['intent_detected']}")
        
        # Speech output
        if self.use_speech_output and self.input_mode == "speech":
            threading.Thread(
                target=self.speech_interface.speak,
                args=(response,),
                daemon=True
            ).start()
    
    def run(self):
        """Main chatbot loop"""
        self.show_banner()
        
        try:
            while True:
                user_input = self.get_user_input()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.process_command(user_input):
                    if user_input.lower() in [":quit", "quit", "exit", ":exit", "bye"]:
                        break
                    continue
                
                # Generate response
                print(f"\n🔍 Processing: {user_input}")
                response, metadata = self.response_generator.generate_response(user_input)
                self.display_response(response, metadata)
                
        except KeyboardInterrupt:
            print("\n\n⚡ Interrupted by user")
        
        # Show final analytics
        final_stats = self.response_generator.get_analytics()
        
        goodbye_msg = f"""
👋 Thank you for learning about Cameroonian tribes! 

📈 Session Summary:
   • Queries processed: {final_stats['total_queries']}
   • Average response time: {final_stats['avg_response_time']}s
   
🇨🇲 Asante sana! (Thank you in Cameroon!)
        """
        
        print(goodbye_msg)
        
        if self.use_speech_output:
            self.speech_interface.speak("Thank you for learning about Cameroonian tribes! Goodbye!")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Enhanced command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Advanced JSON-Based Cameroonian Tribes Educational Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python json_chatbot.py structured_tribes.json
    python json_chatbot.py --data tribes.json --model llama3.2 --verbose
    python json_chatbot.py tribes.json --no-speech --analytics
    
Features:
    • Lightning-fast JSON-based data retrieval
    • Multi-layered search strategies
    • Intent detection and smart categorization
    • LLM enhancement for natural responses
    • Comprehensive analytics and logging
    • Text and speech input/output modes
        """
    )
    
    parser.add_argument(
        'json_file',
        nargs='?',
        help='Path to structured JSON data file'
    )
    
    parser.add_argument(
        '--data', '-d',
        help='Path to JSON data file (alternative to positional)'
    )
    
    parser.add_argument(
        '--model', '-m',
        default=OLLAMA_MODEL,
        help=f'Ollama model name (default: {OLLAMA_MODEL})'
    )
    
    parser.add_argument(
        '--llm-backend', '-b',
        choices=['ollama', 'auto'],
        default='auto',
        help='LLM backend to use (default: auto)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging and metadata display'
    )
    
    parser.add_argument(
        '--no-speech',
        action='store_true',
        help='Disable speech output'
    )
    
    parser.add_argument(
        '--analytics',
        action='store_true',
        help='Show analytics at startup'
    )
    
    parser.add_argument(
        '--test-queries',
        action='store_true',
        help='Run test queries to validate the system'
    )
    
    args = parser.parse_args()
    
    # Determine JSON file path
    json_file = args.data or args.json_file
    
    if not json_file:
        print("❌ Error: JSON data file is required")
        print("\nUsage: python json_chatbot.py <json_file>")
        print("   or: python json_chatbot.py --data <json_file>")
        parser.print_help()
        return
    
    if not Path(json_file).exists():
        print(f"❌ Error: JSON file not found: {json_file}")
        print("\n💡 Tip: Use the DOCX to JSON converter first:")
        print("   python docx_to_json.py your_tribes.docx structured_tribes.json")
        return
    
    # Initialize chatbot
    try:
        print("🚀 Starting Advanced Tribes Chatbot...")
        
        bot = AdvancedTribesBot(
            json_path=json_file,
            model_name=args.model,
            verbose=args.verbose
        )
        
        # Set LLM backend preference
        if args.llm_backend == 'ollama' and not bot.ollama_client.available:
            print("⚠️  Ollama not available, responses will be based on structured data only")
        elif args.llm_backend == 'auto':
            if bot.ollama_client.available:
                print("🤖 Using Ollama for responses")
            else:
                print("⚠️  No LLM available, responses will be based on structured data only")
        
        if args.no_speech:
            bot.use_speech_output = False
        
        if args.analytics:
            bot.show_analytics()
        
        # Test queries mode
        if args.test_queries:
            run_test_queries(bot)
            return
        
        # Run the chatbot
        bot.run()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return


def run_test_queries(bot: AdvancedTribesBot):
    """Run test queries to validate the system"""
    test_queries = [
        "Tell me about Bakossi culture",
        "What are Bamum marriage traditions?",
        "How do Bamileke people celebrate festivals?",
        "What is the history of the Nso tribe?",
        "What do Bassa people eat?",
        "Tell me about Awing language",
        "Compare marriage customs across tribes",
        "What are the main religions in Cameroon tribes?"
    ]
    
    print("\n🧪 RUNNING TEST QUERIES\n")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/8] Query: {query}")
        print("-" * 40)
        
        response, metadata = bot.response_generator.generate_response(query)
        
        print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        print(f"Strategy: {metadata.get('search_strategy')}")
        print(f"Confidence: {metadata.get('confidence', 0):.2f}")
        print(f"Time: {metadata.get('response_time', 0):.3f}s")
    
    print(f"\n✅ Test completed! Final analytics:")
    stats = bot.response_generator.get_analytics()
    print(f"   • Total queries: {stats['total_queries']}")
    print(f"   • Average time: {stats['avg_response_time']}s")


if __name__ == "__main__":
    main()