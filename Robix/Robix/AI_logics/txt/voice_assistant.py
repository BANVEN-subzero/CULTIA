import os
import sys
import time
import sqlite3
import requests
import speech_recognition as sr
import pyttsx3
from typing import Optional, Tuple, List, Dict
from bs4 import BeautifulSoup

# ===== CONFIGURATION ===== #
DB_NAME = "ai_assistant.db"
SCRAPE_INTERVAL = 86400  # 24 hours in seconds
DEFAULT_VOICE_RATE = 150
DEFAULT_VOICE_VOLUME = 0.9

# Try to import Ollama with better error handling
try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama Python package not installed. Install with: pip install ollama")


# ===== INITIALIZATION ===== #
def initialize_systems():
    """Initialize all required systems with better error handling"""
    init_db()
    voice_engine = init_voice_engine()

    # Check Ollama connection if available
    if OLLAMA_AVAILABLE:
        if not check_ollama_connection():
            print("Falling back to simpler responses without Ollama")

    return voice_engine


def check_ollama_connection(retries=3, delay=2):
    """Check if Ollama is running with retries"""
    for attempt in range(retries):
        try:
            ollama.list()  # Simple test of Ollama connection
            return True
        except Exception as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} of {retries}: Ollama not ready, retrying...")
                time.sleep(delay)
            else:
                print(f"Failed to connect to Ollama after {retries} attempts")
                print("Please ensure Ollama is installed and running")
                print("Download from https://ollama.com/download")
                return False
    return False


def init_db():
    """Initialize the SQLite database"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS knowledge_base
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               source_url
                               TEXT
                               NOT
                               NULL,
                               category
                               TEXT
                               NOT
                               NULL,
                               content
                               TEXT
                               NOT
                               NULL,
                               timestamp
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''')

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS voice_settings
                           (
                               voice_id
                               TEXT
                               PRIMARY
                               KEY,
                               rate
                               INTEGER
                               DEFAULT
                               ?,
                               volume
                               REAL
                               DEFAULT
                               ?,
                               last_updated
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''', (DEFAULT_VOICE_RATE, DEFAULT_VOICE_VOLUME))

            cursor.execute('''
                           CREATE INDEX IF NOT EXISTS idx_content_search
                               ON knowledge_base(content)
                           ''')

            conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")


def init_voice_engine():
    """Initialize the text-to-speech engine with better error handling"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', DEFAULT_VOICE_RATE)
        engine.setProperty('volume', DEFAULT_VOICE_VOLUME)

        # Try a silent test to verify initialization
        engine.say(" ")
        engine.runAndWait()
        return engine
    except Exception as e:
        print(f"Voice engine initialization failed: {e}")
        print("Continuing in text-only mode")
        return None


# ===== INPUT HANDLING ===== #
def get_user_input(voice_engine) -> Tuple[Optional[str], str]:
    """Get user input with automatic mode detection"""
    # Try voice input first if engine is available
    if voice_engine is not None:
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("\n[Listening...] (or type text)")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    text = recognizer.recognize_google(audio)
                    print(f"[Voice Input]: {text}")
                    return text, 'voice'
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Voice input error: {e}")

    # Fall back to text input
    try:
        print("\n[Ready for text input] (or speak)")
        text = input("> ").strip()
        if text:
            print(f"[Text Input]: {text}")
            return text, 'text'
    except Exception as e:
        print(f"Text input error: {e}")

    return None, 'text'


# ===== KNOWLEDGE MANAGEMENT ===== #
def query_local_knowledge(query: str) -> List[Dict]:
    """Search local database for relevant information"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT source_url, content
                           FROM knowledge_base
                           WHERE content LIKE ?
                           ORDER BY timestamp DESC
                               LIMIT 3
                           ''', (f'%{query}%',))

            return [
                {"source": row[0], "content": row[1]}
                for row in cursor.fetchall()
            ]
    except Exception as e:
        print(f"Database query error: {e}")
        return []


def scrape_web(query: str) -> List[Dict]:
    """Scrape web for information related to query"""
    if input("Search web for additional info? (y/n): ").lower() != 'y':
        return []

    try:
        # Example: Search Wikipedia
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()

        results = []
        for item in response.json().get('query', {}).get('search', [])[:3]:
            page_url = f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
            page_content = get_page_content(page_url)
            if page_content:
                results.append({
                    "source": page_url,
                    "content": page_content
                })

        return results
    except Exception as e:
        print(f"Web scraping error: {e}")
        return []


def get_page_content(url: str) -> Optional[str]:
    """Get cleaned content from a web page"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'aside']):
            element.decompose()

        # Extract main content
        content = []
        for paragraph in soup.find_all('p'):
            text = ' '.join(paragraph.get_text().split())
            if text and len(text) > 50:  # Filter out short paragraphs
                content.append(text)

        return ' '.join(content)[:2000]  # Limit content length
    except Exception as e:
        print(f"Page content extraction error: {e}")
        return None


def store_knowledge(data: List[Dict]):
    """Store scraped knowledge in database"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                               INSERT INTO knowledge_base (source_url, category, content)
                               VALUES (?, ?, ?)
                               ''', [
                                   (item['source'], 'web_scrape', item['content'])
                                   for item in data
                               ])
            conn.commit()
    except Exception as e:
        print(f"Knowledge storage error: {e}")


# ===== AI PROCESSING ===== #
def generate_response(query: str, context: List[Dict]) -> str:
    """Generate response with fallback if Ollama isn't available"""
    if not OLLAMA_AVAILABLE:
        return simple_response(query, context)

    try:
        # Prepare context for the LLM
        context_str = "\n".join(
            f"Source {i + 1} ({item['source']}):\n{item['content']}\n"
            for i, item in enumerate(context)
        ) if context else "No additional context available."

        response = ollama.chat(
            model='llama3',
            messages=[{
                'role': 'system',
                'content': '''You are an AI assistant. Provide helpful, accurate responses 
                based on the context provided. Cite sources when available.'''
            }, {
                'role': 'user',
                'content': f"Question: {query}\n\nContext:\n{context_str}"
            }],
            options={
                'temperature': 0.7,
                'num_ctx': 4096
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f"LLM generation error: {e}")
        return simple_response(query, context)


def simple_response(query: str, context: List[Dict]) -> str:
    """Fallback response generator when Ollama isn't available"""
    if context:
        return f"I found this information about '{query}':\n" + \
            "\n".join(f"- {item['content'][:200]}..." for item in context)
    return f"I don't have information about '{query}'. Please try another question."


# ===== OUTPUT HANDLING ===== #
def respond(response: str, mode: str, voice_engine):
    """Deliver response in the appropriate mode"""
    try:
        print(f"\n[Assistant]: {response}")
        if mode == 'voice' and voice_engine is not None:
            try:
                voice_engine.say(response)
                voice_engine.runAndWait()
            except Exception as e:
                print(f"Voice output error: {e}")
    except Exception as e:
        print(f"Response delivery error: {e}")


def configure_voice(voice_engine):
    """Configure voice settings interactively"""
    if voice_engine is None:
        print("Voice output not available")
        return

    voices = voice_engine.getProperty('voices')
    if not voices:
        print("No voices available")
        return

    print("\nAvailable Voices:")
    for i, voice in enumerate(voices):
        print(f"{i + 1}. {voice.name} ({voice.id})")

    try:
        choice = int(input("Select voice (number): ")) - 1
        if 0 <= choice < len(voices):
            rate = int(input(f"Speech rate (50-300, default {DEFAULT_VOICE_RATE}): ") or DEFAULT_VOICE_RATE)
            volume = float(input(f"Volume (0.1-1.0, default {DEFAULT_VOICE_VOLUME}): ") or DEFAULT_VOICE_VOLUME)

            voice_engine.setProperty('voice', voices[choice].id)
            voice_engine.setProperty('rate', rate)
            voice_engine.setProperty('volume', volume)

            # Save settings
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO voice_settings (voice_id, rate, volume)
                    VALUES (?, ?, ?)
                ''', (voices[choice].id, rate, volume))

            print("Voice settings updated!")
            respond("Voice settings have been updated", 'voice', voice_engine)
        else:
            print("Invalid selection")
    except ValueError:
        print("Invalid input")


# ===== MAIN LOOP ===== #
def main_loop(voice_engine):
    """Main interaction loop with better error handling"""
    print("\n=== AI Assistant ===")
    print("You can speak or type your queries.")
    print("Special commands: 'settings', 'mode', 'exit'")

    while True:
        try:
            # Get user input
            query, mode = get_user_input(voice_engine)
            if not query:
                continue

            # Handle special commands
            if query.lower() == 'exit':
                respond("Goodbye!", mode, voice_engine)
                break

            if query.lower() == 'settings':
                configure_voice(voice_engine)
                continue

            if query.lower() == 'mode':
                new_mode = 'text' if mode == 'voice' else 'voice'
                respond(f"Switched to {new_mode} mode", mode, voice_engine)
                mode = new_mode
                continue

            # Process query
            respond("Processing your request...", mode, voice_engine)

            # Get knowledge from local and web sources
            local_knowledge = query_local_knowledge(query)
            web_knowledge = scrape_web(query)

            # Store new knowledge
            if web_knowledge:
                store_knowledge(web_knowledge)

            # Generate and deliver response
            context = local_knowledge + web_knowledge
            response = generate_response(query, context)
            respond(response, mode, voice_engine)

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            respond("Sorry, I encountered an error processing your request.", mode, voice_engine)


# ===== ENTRY POINT ===== #
if __name__ == "__main__":
    # Initialize systemshh
    voice_engine = initialize_systems()

    # Run main loop
    try:
        main_loop(voice_engine)
    finally:
        # Cleanup
        if voice_engine is not None:
            voice_engine.stop()
        print("Assistant shutdown complete")