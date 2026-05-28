# Intelligent Cameroonian Tribes Chatbot

An enhanced intelligent chatbot that provides comprehensive information about Cameroonian tribes with improved natural language processing and comparative analysis capabilities.

## Features

- **Enhanced Natural Language Processing**: Better understanding of user queries with intent detection
- **Comparative Analysis**: Compare different tribes side-by-side
- **Contextual Recommendations**: Personalized suggestions based on user interests
- **Feedback Learning System**: Collects user feedback to improve responses over time
- **Speech and Text Interface**: Supports both speech and text input/output
- **Fast JSON-based Data Retrieval**: Lightning-fast responses using structured data
- **Multi-layered Search**: Categories, keywords, and full-text search capabilities
- **LLM Integration**: Optional enhancement with Ollama for more natural responses

## Enhanced Capabilities

### 1. Improved Intelligence
- Advanced intent detection for better query understanding
- Contextual recommendations based on user interests
- Personalized experience through interest tracking

### 2. Comparative Analysis
- Compare any two or more tribes
- Highlight similarities and differences
- Cross-reference cultural practices, traditions, and history

### 3. Feedback Learning
- Collect user ratings (1-5 scale)
- Analyze feedback for continuous improvement
- Track response quality over time

### 4. Rich Data Structure
- Comprehensive information for 65 Cameroonian tribes
- Structured sections: Overview, History, Culture, Traditions, etc.
- Cross-references between related tribes
- Categorized by geographic regions, linguistic families, economic activities

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required dependencies:
   ```bash
   pip install speechrecognition pyttsx3 ollama
   ```
   (Note: These are optional - the chatbot works without them)

## Usage

### Command Line Interface
```bash
# Run with default data file
python intelligent_chatbot.py

# Run with specific data file
python intelligent_chatbot.py comprehensive_tribes_data.json

# Disable speech interface
python intelligent_chatbot.py --no-speech

# Enable verbose logging
python intelligent_chatbot.py --verbose

# Use specific LLM model
python intelligent_chatbot.py --model llama3.2
```

### Interactive Commands
- Type `help` for usage instructions
- Type `stats` to see conversation statistics
- Type `feedback` to rate the last response
- Type `quit`, `exit`, or `bye` to exit

### Example Queries
- "Tell me about Bamileke culture"
- "Compare Fulani and Duala traditions"
- "What are the economic activities of the Beti people?"
- "Show me information about Tikar history"
- "What languages do the Bamum people speak?"
- "Compare the governance systems of Bamileke and Bamum"

## Data Structure

The chatbot uses a comprehensive JSON dataset with:
- Metadata about the dataset
- Detailed information for 65 Cameroonian tribes
- Structured sections for each tribe
- Keywords for improved search
- Cross-references between related tribes
- Categorization by various attributes

## Development

### Key Components
1. **TribesDataManager**: Manages structured tribal data
2. **IntentDetector**: Detects user intent from queries
3. **SmartResponseGenerator**: Generates intelligent responses
4. **ContextualRecommender**: Provides personalized recommendations
5. **FeedbackLearningSystem**: Collects and analyzes user feedback
6. **SpeechInterface**: Handles speech input/output

### Testing
Run the test suite:
```bash
python test_chatbot.py
```

## Requirements
- Python 3.6+
- Standard library only for core functionality
- Optional: speechrecognition, pyttsx3 for speech features
- Optional: Ollama for LLM enhancement

## License
This project is licensed under the MIT License.