#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intelligent Cameroonian Tribes Educational Chatbot
==========================================================

An enhanced intelligent chatbot that uses structured JSON data for fast, accurate responses
about Cameroonian tribes with improved natural language processing and comparative analysis.

Features:
- Lightning-fast JSON-based data retrieval
- Multi-layered search: categories, keywords, full-text
- Intelligent query understanding and intent detection
- Comparative analysis between tribes
- Contextual recommendations based on user interests
- Hybrid responses: Structured data + LLM enhancement
- Text and speech input/output with mode switching
- Comprehensive logging and analytics

Dependencies:
- Standard library only for core functionality
- Optional: speechrecognition, pyttsx3 for speech features
- Optional: Ollama for LLM enhancement

Usage:
    python intelligent_chatbot.py intelligent_tribes_data.json
    python intelligent_chatbot.py --data tribes.json --model llama3.2 --verbose
    python intelligent_chatbot.py tribes.json --no-speech --analytics
"""

import os
import re
import sys
import json
import time
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

# Global variable for Ollama model
OLLAMA_MODEL = "llama3.2"


# =============================================================================
# Configuration
# =============================================================================

SUPPORTED_TRIBES = [
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
    "overview": [
        r"\b(what|who|tell me about|describe|introduce|overview|general|about)\b",
        r"\b(tribe|people|group|ethnic)\b"
    ],
    "history": [
        r"\b(history|historical|origin|past|ancient|founded|established|began)\b",
        r"\b(ancestors|migration|settlement|empire|kingdom)\b"
    ],
    "culture": [
        r"\b(culture|cultural|customs|practices|lifestyle|society|values)\b",
        r"\b(way of life|social|community|beliefs|worldview)\b"
    ],
    "language": [
        r"\b(language|speak|dialect|tongue|communication|linguistic)\b",
        r"\b(words|vocabulary|oral|written)\b"
    ],
    "traditions": [
        r"\b(tradition|traditional|ritual|ceremony|heritage|customs)\b",
        r"\b(sacred|spiritual|initiation|ancestral)\b"
    ],
    "marriage": [
        r"\b(marriage|wedding|marry|bride|groom|spouse|matrimony)\b",
        r"\b(dowry|courtship|family|kinship|clan)\b"
    ],
    "religion": [
        r"\b(religion|religious|spiritual|belief|faith|worship|god)\b",
        r"\b(prayer|sacred|holy|ancestor|deity|divine)\b"
    ],
    "food": [
        r"\b(food|eat|cuisine|dish|meal|cook|recipe|diet)\b",
        r"\b(crop|agriculture|hunt|fish|feast|ingredient)\b"
    ],
    "economy": [
        r"\b(economy|economic|trade|business|work|job|occupation)\b",
        r"\b(farming|livestock|craft|income|wealth|market)\b"
    ],
    "art": [
        r"\b(art|craft|carving|sculpture|pottery|weaving|mask)\b",
        r"\b(artistic|creative|decoration|jewelry|artifact)\b"
    ],
    "music": [
        r"\b(music|song|dance|instrument|drum|performance)\b",
        r"\b(rhythm|melody|cultural music|entertainment)\b"
    ],
    "festivals": [
        r"\b(festival|celebration|ceremony|event|commemoration)\b",
        r"\b(annual|seasonal|harvest|cultural festival)\b"
    ],
    "compare": [
        r"\b(compare|difference|similar|versus|vs|contrast)\b",
        r"\b(both|and|or|either)\b"
    ]
}

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = """You are an expert educator on Cameroonian tribal culture, specializing in over 50 tribes of Cameroon and neighboring regions.

Guidelines:
- Use the provided structured data as your primary source
- Be educational, respectful, and culturally sensitive
- Synthesize information clearly and engagingly
- If information is incomplete, acknowledge gaps honestly
- Focus on the tribes specified in the data
- Keep responses conversational but informative
- When comparing tribes, highlight both similarities and differences
- When users ask about related topics, provide contextual recommendations
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
    """Extract tribe names from text"""
    text_lower = normalize_text(text)
    found_tribes = []
    
    for tribe in SUPPORTED_TRIBES:
        if tribe in text_lower:
            found_tribes.append(tribe)
    
    return found_tribes


# =============================================================================
# JSON Data Manager
# =============================================================================

class TribesDataManager:
    """Manages structured tribal data from JSON with enhanced intelligence"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = {}
        self.metadata = {}
        self.search_index = {}
        self.cross_references = {}
        self.logger = logging.getLogger('TribesBot.DataManager')
        self.load_data()
        self.build_search_index()
        self.build_cross_references()
    
    def load_data(self):
        """Load structured data from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            # Handle both nested and flat JSON structures
            if 'tribes' in full_data:
                self.metadata = full_data.get('metadata', {})
                self.data = full_data.get('tribes', {})
                self.cross_references = full_data.get('cross_references', {})
            else:
                # Flat structure: tribes are at the top level
                self.data = full_data
                self.metadata = full_data.get('metadata', {})
                self.cross_references = full_data.get('cross_references', {})
                # Remove non-tribe keys from self.data
                for key in ['metadata', 'cross_references']:
                    if key in self.data:
                        del self.data[key]
            
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
    
    def build_cross_references(self):
        """Build cross-references for enhanced intelligence"""
        self.logger.info("Building cross-references...")
        
        # Create reverse index for categories
        self.category_index = defaultdict(list)
        for tribe_name, tribe_data in self.data.items():
            categories = tribe_data.get('categories', {})
            for category_type, category_values in categories.items():
                for value in category_values:
                    self.category_index[f"{category_type}:{value}"].append(tribe_name)
        
        self.logger.info("Cross-references built successfully")
    
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
    
    def get_tribes_by_category(self, category_type: str, category_value: str) -> List[str]:
        """Get tribes that belong to a specific category"""
        return self.category_index.get(f"{category_type}:{category_value}", [])
    
    def get_related_tribes(self, tribe_name: str, relation_type: str = "cultural_similarities") -> List[Dict]:
        """Get tribes related to a specific tribe"""
        cross_refs = self.cross_references.get(relation_type, {})
        return cross_refs.get(tribe_name, [])
    
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
    """Detects user intent from queries with enhanced capabilities"""
    
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
        
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(query_lower))
                score += matches
            
            if score > 0:
                # Normalize by query length
                intent_scores[intent] = score / len(query.split()) * 10
        
        return dict(intent_scores)
    
    def get_primary_intent(self, query: str) -> Optional[str]:
        """Get the primary intent category"""
        intents = self.detect_intent(query)
        if intents:
            return max(intents.items(), key=lambda x: x[1])[0]
        return None


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
                context_parts.append(f"{section.title()}: {content[:300]}...")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""{SYSTEM_PROMPT}

User Question: {query}

Structured Data Available:
{context}

Please provide a comprehensive, well-structured answer based on this information. If the data is incomplete, mention what additional information might be useful."""
        
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
                self.logger.info("Ollama enhancement successful")
                return response
            else:
                self.logger.error(f"Ollama error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Ollama request timed out")
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
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self.microphone = sr.Microphone() if SR_AVAILABLE else None
        self.tts_engine = self._init_tts()
        
        if self.microphone:
            self._calibrate_microphone()
    
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
        
        # Generate response using best strategy
        response = self._select_response_strategy(query_clean, mentioned_tribes, primary_intent, metadata)
        
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
        cultural_keywords = ['culture', 'tradition', 'tribe', 'people', 'cameroon', 'heritage', 'compare']
        return any(keyword in query for keyword in cultural_keywords)
    
    def _out_of_scope_response(self) -> str:
        """Generate out-of-scope response"""
        return ("I specialize in Cameroonian tribes. Please ask me about their culture, traditions, "
                "history, or other aspects of these tribes! You can also ask me to compare different tribes.")
    
    def _select_response_strategy(self, query: str, tribes: List[str], intent: str, metadata: Dict) -> str:
        """Select the best response strategy based on query analysis"""
        
        # Strategy for comparison queries
        if intent == "compare" and len(tribes) >= 2:
            response = self._comparison_response(tribes, metadata)
            if response:
                return response
        
        # Strategy 1: Direct section access (fastest)
        if tribes and intent:
            response = self._direct_section_response(tribes, intent, metadata)
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
        
        response_parts = [f"**Comparison of {', '.join(tribes)}**\n"]
        
        # Add similarities
        if comparison_data.get("similarities"):
            response_parts.append("📝 **Similarities:**")
            for category, content in comparison_data["similarities"].items():
                response_parts.append(f"- {category.title()}: {content[:200]}...")
            response_parts.append("")
        
        # Add differences
        if comparison_data.get("differences"):
            response_parts.append("🔄 **Key Differences:**")
            for category, contents in comparison_data["differences"].items():
                response_parts.append(f"\n**{category.title()}:**")
                for tribe, content in contents.items():
                    if content:
                        response_parts.append(f"- {tribe.capitalize()}: {content[:150]}...")
        
        metadata['confidence'] = 0.8
        return "\n".join(response_parts)
    
    def _direct_section_response(self, tribes: List[str], intent: str, metadata: Dict) -> Optional[str]:
        """Direct access to specific sections"""
        metadata['search_strategy'] = 'direct_section'
        
        responses = []
        for tribe in tribes:
            content = self.data_manager.get_tribe_section(tribe, intent)
            if content:
                responses.append(f"**{tribe.capitalize()} - {intent.title()}:**\n{content}")
                metadata['confidence'] = 0.9
        
        if responses:
            return "\n\n".join(responses)
        return None
    
    def _keyword_search_response(self, query: str, tribes: List[str], metadata: Dict) -> Optional[str]:
        """Search using extracted keywords"""
        metadata['search_strategy'] = 'keyword_search'
        
        # Extract query keywords
        query_words = [word for word in query.split() if len(word) > 2]
        
        # Search by keywords
        search_results = self.data_manager.search_by_keywords(query_words)
        
        if search_results:
            relevant_tribes = [tribe for tribe, score in search_results[:3] if score > 0.2]
            # Filter by mentioned tribes if any
            if tribes:
                relevant_tribes = [t for t in relevant_tribes if t in tribes]
            
            if relevant_tribes:
                response_parts = []
                for tribe in relevant_tribes:
                    tribe_data = self.data_manager.get_tribe_data(tribe)
                    # Get the most relevant section
                    best_section = self._find_best_section(query, tribe_data)
                    if best_section:
                        response_parts.append(f"**{tribe.capitalize()}:**\n{best_section}")
                
                if response_parts:
                    metadata['confidence'] = 0.7
                    return "\n\n".join(response_parts)
        
        return None
    
    def _similarity_search_response(self, query: str, tribes: List[str], metadata: Dict) -> Optional[str]:
        """Search using content similarity"""
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
                        response_parts.append(f"**{tribe.capitalize()} - {best_section.title()}:**\n{content[:300]}...")
                
                if response_parts:
                    metadata['confidence'] = 0.6
                    return "\n\n".join(response_parts)
        
        return None
    
    def _llm_fallback_response(self, query: str, metadata: Dict) -> str:
        """LLM-enhanced response as fallback"""
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
                return f"{llm_response}\n\n📚 *Based on available tribal data*"
        
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
        response_parts.append("Based on the information I have about Cameroonian tribes:")
        
        for tribe_key, content in context_data.items():
            if content:
                # Extract tribe name from key
                tribe_name = tribe_key.split('_')[0]
                response_parts.append(f"\n**{tribe_name.capitalize()}:** {content[:200]}...")
        
        if len(response_parts) > 1:
            response_parts.append("\n\nI can provide more specific details if you ask about particular aspects like history, culture, traditions, or economy.")
            return "\n".join(response_parts)
        else:
            return None

    def _find_best_section(self, query: str, tribe_data: Dict) -> Optional[str]:
        """Find the most relevant section based on query keywords"""
        if not tribe_data:
            return None
            
        sections = tribe_data.get('sections', {})
        if not sections:
            return None
            
        # Score each section based on keyword matches
        section_scores = {}
        query_words = set(query.split())
        
        for section_name, content in sections.items():
            if content:
                content_words = set(content.lower().split())
                # Count matching words
                matches = len(query_words.intersection(content_words))
                section_scores[section_name] = matches
        
        # Return section with highest score
        if section_scores:
            best_section = max(section_scores.items(), key=lambda x: x[1])
            if best_section[1] > 0:  # At least one match
                return sections[best_section[0]]
        
        # Fallback to overview if no matches
        return sections.get('overview', list(sections.values())[0] if sections else None)


# =============================================================================
# Contextual Recommendations
# =============================================================================

class ContextualRecommender:
    """Provides contextual recommendations based on user interests"""
    
    def __init__(self, data_manager: TribesDataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger('TribesBot.Recommender')
        self.user_interests = defaultdict(list)  # Track user interests over time
        self.query_history = []  # Track recent queries for context
        self.interest_categories = defaultdict(int)  # Track interest in categories
    
    def update_user_interests(self, query: str, response_metadata: Dict):
        """Update user interest profiles based on query and response"""
        # Track tribes mentioned
        tribes_mentioned = response_metadata.get('tribes_mentioned', [])
        for tribe in tribes_mentioned:
            self.user_interests['tribes'].append(tribe)
        
        # Track categories of interest
        intent = response_metadata.get('intent_detected')
        if intent:
            self.interest_categories[intent] += 1
        
        # Track query for context
        self.query_history.append({
            'query': query,
            'timestamp': time.time(),
            'tribes': tribes_mentioned,
            'intent': intent
        })
        
        # Keep only recent history (last 10 queries)
        if len(self.query_history) > 10:
            self.query_history = self.query_history[-10:]
    
    def get_recommendations(self, query: str, response_metadata: Dict) -> List[str]:
        """Generate contextual recommendations based on query and response"""
        # Update user interests first
        self.update_user_interests(query, response_metadata)
        
        recommendations = []
        
        # Extract tribes mentioned in query
        tribes_mentioned = response_metadata.get('tribes_mentioned', [])
        
        # If specific tribes were mentioned, suggest related tribes
        for tribe in tribes_mentioned:
            related_tribes = self.data_manager.get_related_tribes(tribe)
            for related in related_tribes[:2]:  # Limit to 2 related tribes
                if isinstance(related, dict):
                    related_name = related.get('tribe', '')
                    relation_type = related.get('relation', 'related')
                else:
                    related_name = related
                    relation_type = 'related'
                    
                if related_name and related_name not in tribes_mentioned:
                    recommendations.append(f"You might also be interested in the {related_name.capitalize()} people, who are {relation_type} to the {tribe.capitalize()}.")
        
        # Suggest based on user's interest categories
        if self.interest_categories:
            most_popular_category = max(self.interest_categories.items(), key=lambda x: x[1])[0]
            # Find tribes related to this category that user hasn't explored much
            category_tribes = []
            for tribe_name, tribe_data in self.data_manager.data.items():
                if tribe_name not in tribes_mentioned:
                    categories = tribe_data.get('categories', {})
                    for cat_type, cat_values in categories.items():
                        if most_popular_category.replace('_', '') in [v.lower() for v in cat_values]:
                            category_tribes.append(tribe_name)
                            break
            
            if category_tribes:
                # Recommend tribes from user's most interested category
                recommendations.append(f"Since you're interested in {most_popular_category.replace('_', ' ')}, you might enjoy learning about the {category_tribes[0].capitalize()} people.")
        
        # If no specific tribes mentioned, recommend popular tribes
        if not tribes_mentioned and not recommendations:
            popular_tribes = ['bamileke', 'bamum', 'duala', 'fulani', 'beti']
            recommendations.append("You might be interested in learning about these prominent Cameroonian tribes:")
            recommendations.append(", ".join([t.capitalize() for t in popular_tribes]) + ".")
        
        # Add contextual recommendations based on query patterns
        if "compare" in query.lower() or "versus" in query.lower() or "difference" in query.lower():
            recommendations.append("💡 You can compare any two tribes by asking questions like 'Compare Bamileke and Bamum traditions'")
        
        if "history" in query.lower() or "origin" in query.lower():
            recommendations.append("💡 Try asking about cultural practices like 'What are traditional marriage customs of the Duala people?'")
        
        return recommendations[:3]  # Limit to 3 recommendations


# =============================================================================
# Feedback Learning System
# =============================================================================

class FeedbackLearningSystem:
    """Implements feedback learning to improve responses over time"""
    
    def __init__(self, data_manager: TribesDataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger('TribesBot.Feedback')
        self.feedback_log = []  # Store feedback for analysis
        self.response_improvements = {}  # Track improvements for specific queries
        self.user_ratings = defaultdict(list)  # Track user ratings for responses
    
    def collect_feedback(self, query: str, response: str, rating: int, comment: str = ""):
        """Collect user feedback on responses"""
        feedback_entry = {
            'timestamp': time.time(),
            'query': query,
            'response': response,
            'rating': rating,  # 1-5 scale
            'comment': comment
        }
        
        self.feedback_log.append(feedback_entry)
        self.user_ratings[query].append(rating)
        
        # Log feedback
        self.logger.info(f"Feedback received for query: {query[:50]}... Rating: {rating}")
        
        # If negative feedback, suggest improvements
        if rating <= 2:
            self._analyze_negative_feedback(query, response, comment)
    
    def _analyze_negative_feedback(self, query: str, response: str, comment: str):
        """Analyze negative feedback to identify improvement areas"""
        # Simple analysis for now - could be enhanced with NLP
        feedback_keywords = []
        if "short" in comment.lower() or "brief" in comment.lower():
            feedback_keywords.append("expand_content")
        if "confusing" in comment.lower() or "unclear" in comment.lower():
            feedback_keywords.append("clarify_content")
        if "wrong" in comment.lower() or "incorrect" in comment.lower():
            feedback_keywords.append("correct_facts")
        
        # Store for future reference
        if query not in self.response_improvements:
            self.response_improvements[query] = []
        self.response_improvements[query].extend(feedback_keywords)
    
    def get_average_rating(self, query: str = None) -> float:
        """Get average rating for a specific query or overall"""
        if query:
            ratings = self.user_ratings.get(query, [])
            return sum(ratings) / len(ratings) if ratings else 0.0
        else:
            # Overall average
            all_ratings = []
            for ratings in self.user_ratings.values():
                all_ratings.extend(ratings)
            return sum(all_ratings) / len(all_ratings) if all_ratings else 0.0
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback for analytics"""
        if not self.feedback_log:
            return {}
        
        recent_feedback = self.feedback_log[-20:]  # Last 20 feedback entries
        
        return {
            'total_feedback': len(self.feedback_log),
            'average_rating': self.get_average_rating(),
            'recent_feedback': recent_feedback,
            'improvement_suggestions': self.response_improvements
        }


# Update the main chatbot class to include feedback functionality
class IntelligentTribesChatbot:
    """Main chatbot interface with enhanced intelligence"""
    
    def __init__(self, data_file: str, use_speech: bool = True, verbose: bool = False):
        self.logger = setup_logging(verbose)
        self.use_speech = use_speech and SR_AVAILABLE and TTS_AVAILABLE
        self.verbose = verbose
        
        # Initialize components
        self.logger.info("Initializing Intelligent Tribes Chatbot...")
        self.data_manager = TribesDataManager(data_file)
        self.intent_detector = IntentDetector()
        self.ollama_client = OllamaClient()
        self.response_generator = SmartResponseGenerator(
            self.data_manager, 
            self.intent_detector, 
            self.ollama_client
        )
        self.recommender = ContextualRecommender(self.data_manager)
        self.feedback_system = FeedbackLearningSystem(self.data_manager)
        
        if self.use_speech:
            self.speech_interface = SpeechInterface()
        else:
            self.speech_interface = None
        
        self.session_stats = {
            'queries': 0,
            'total_response_time': 0,
            'tribes_mentioned': set()
        }
        
        self.logger.info("Chatbot initialization complete")
    
    def process_query(self, query: str) -> str:
        """Process a user query and generate response"""
        self.session_stats['queries'] += 1
        
        # Generate response
        response, metadata = self.response_generator.generate_response(query)
        
        # Update session stats
        self.session_stats['total_response_time'] += metadata.get('response_time', 0)
        self.session_stats['tribes_mentioned'].update(metadata.get('tribes_mentioned', []))
        
        # Update user interests and get recommendations
        self.recommender.update_user_interests(query, metadata)
        recommendations = self.recommender.get_recommendations(query, metadata)
        if recommendations:
            response += "\n\n" + "\n".join([f"💡 {rec}" for rec in recommendations])
        
        return response
    
    def provide_feedback(self, query: str, response: str, rating: int, comment: str = ""):
        """Provide feedback on a response"""
        self.feedback_system.collect_feedback(query, response, rating, comment)
        print("🤖 Thank you for your feedback! It helps me improve.")
    
    def chat_loop(self):
        """Main chat loop with enhanced interaction"""
        print("=" * 80)
        print("🤖 INTELLIGENT CAMEROONIAN TRIBES CHATBOT")
        print("=" * 80)
        print("Welcome! I'm here to help you learn about Cameroonian tribes.")
        print("Ask me about their culture, history, traditions, or compare different tribes.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'feedback' to provide feedback on the last response.")
        print()
        
        if self.use_speech:
            print("🎤 Speech mode enabled - say 'switch to text' to toggle")
        else:
            print("⌨️  Text mode - type 'switch to speech' to toggle (if available)")
        print("-" * 80)
        
        last_query = ""
        last_response = ""
        
        while True:
            try:
                # Get user input
                if self.use_speech:
                    user_input = self.speech_interface.listen()
                    if not user_input:
                        # Fallback to text if speech failed
                        user_input = input("\n💬 You (text): ").strip()
                else:
                    user_input = input("\n💬 You: ").strip()
                
                # Check for mode switching
                if 'switch to speech' in user_input.lower() and SR_AVAILABLE and TTS_AVAILABLE:
                    self.use_speech = True
                    print("🎤 Switched to speech mode")
                    continue
                elif 'switch to text' in user_input.lower():
                    self.use_speech = False
                    print("⌨️  Switched to text mode")
                    continue
                
                # Check for feedback command
                if user_input.lower() == 'feedback':
                    if last_response:
                        self._collect_feedback(last_query, last_response)
                    else:
                        print("🤖 No previous response to provide feedback on.")
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    self._goodbye()
                    break
                
                # Check for help command
                if user_input.lower() in ['help', 'help me']:
                    self._show_help()
                    continue
                
                # Check for stats command
                if user_input.lower() in ['stats', 'statistics']:
                    self._show_stats()
                    continue
                
                if not user_input:
                    print("🤖 Please say or type something...")
                    continue
                
                # Process query
                print("🤖 Thinking...")
                response = self.process_query(user_input)
                
                # Store for potential feedback
                last_query = user_input
                last_response = response
                
                # Output response
                print(f"\n🤖 Chatbot: {response}")
                
                # Speak response if in speech mode
                if self.use_speech and self.speech_interface:
                    self.speech_interface.speak(response)
                
            except KeyboardInterrupt:
                self._goodbye()
                break
            except Exception as e:
                self.logger.error(f"Error processing query: {e}")
                print("🤖 Sorry, I encountered an error. Please try again.")
    
    def _collect_feedback(self, query: str, response: str):
        """Collect feedback from user"""
        print(f"\n📝 Providing feedback for: {query[:50]}...")
        print(f"Response: {response[:100]}...")
        
        try:
            rating = int(input("Rate this response (1-5, where 5 is excellent): "))
            if 1 <= rating <= 5:
                comment = input("Any additional comments? (optional): ").strip()
                self.provide_feedback(query, response, rating, comment)
            else:
                print("🤖 Please provide a rating between 1 and 5.")
        except ValueError:
            print("🤖 Invalid rating. Please enter a number between 1 and 5.")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📚 INTELLIGENT TRIBES CHATBOT - HELP

You can ask me about:
• Specific tribes and their culture, history, traditions
• Comparisons between different tribes
• Economic activities, religious practices, languages
• Arts, crafts, and cultural practices
• Geographic locations and population information

Commands:
• 'help' - Show this help message
• 'stats' - Show conversation statistics
• 'switch to speech/text' - Toggle input mode
• 'quit', 'exit', 'bye' - End conversation

Examples:
• "Tell me about Bamileke culture"
• "Compare Fulani and Duala traditions"
• "What languages do the Beti people speak?"
• "Show me information about Tikar history"
        """
        print(help_text)
    
    def _show_stats(self):
        """Show session statistics"""
        avg_response_time = (
            self.session_stats['total_response_time'] / self.session_stats['queries']
            if self.session_stats['queries'] > 0 else 0
        )
        
        stats_text = f"""
📊 SESSION STATISTICS
====================
Total Queries: {self.session_stats['queries']}
Average Response Time: {avg_response_time:.2f}s
Tribes Discussed: {len(self.session_stats['tribes_mentioned'])}
Unique Tribes: {', '.join(sorted([t.capitalize() for t in self.session_stats['tribes_mentioned']]))}
        """
        print(stats_text)
    
    def _goodbye(self):
        """Show goodbye message"""
        print("\n🤖 Thank you for learning about Cameroonian tribes!")
        print("Feel free to come back anytime to explore more cultural knowledge.")
        print("👋 Goodbye!")
        self._show_stats()


# =============================================================================
# Command Line Interface
# =============================================================================

def main():
    """Main entry point with enhanced CLI options"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Intelligent Cameroonian Tribes Educational Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'data_file',
        nargs='?',
        default='intelligent_tribes_data.json',
        help='Path to JSON data file (default: intelligent_tribes_data.json)'
    )
    
    parser.add_argument(
        '--no-speech',
        action='store_true',
        help='Disable speech input/output'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--model',
        default='llama3.2',
        help='LLM model to use (default: llama3.2)'
    )
    
    parser.add_argument(
        '--analytics',
        action='store_true',
        help='Enable analytics mode'
    )
    
    args = parser.parse_args()
    
    # Set model if specified
    global OLLAMA_MODEL
    OLLAMA_MODEL = args.model
    
    # Validate data file exists
    if not os.path.exists(args.data_file):
        print(f"❌ Error: Data file '{args.data_file}' not found.")
        print("Please provide a valid JSON data file.")
        sys.exit(1)
    
    try:
        # Initialize and run chatbot
        chatbot = IntelligentTribesChatbot(
            data_file=args.data_file,
            use_speech=not args.no_speech,
            verbose=args.verbose
        )
        
        if args.analytics:
            print("📊 Analytics mode enabled")
            # Could implement analytics-specific functionality here
        
        chatbot.chat_loop()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logging.getLogger('TribesBot').error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
