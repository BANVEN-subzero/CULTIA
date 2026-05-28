# CULTIA - Architectural Design Report

## Project Overview
CULTIA is a cultural AI platform focused on preserving and educating about Cameroonian tribes and cultural heritage through an intelligent chatbot, interactive learning modules, quizzes, and gamification features.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  (HTML/CSS/JS - Static Pages + Bot Interface)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                          │
│  (Flask API Server + Authentication + Data Management)      │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   AI/Chatbot Layer       │     │   Data Layer             │
│  (CultureAI Engine)     │     │  (SQLite + JSON Data)    │
└─────────────────────────┘     └─────────────────────────┘
```

## Component Breakdown

### 1. Frontend Layer (`Frontends/`)

**Public Pages:**
- `index.html` - Landing page with Cameroon map, feature cards, and navigation
- `about.html` - About the platform
- `features.html` - Feature descriptions (Educator, Storyteller, Personal Assistant modes)
- `explore.html` - Cultural exploration with interactive elements
- `contact.html` - Contact form
- `login.html` / `register.html` - Authentication pages

**Bot Interface (`Frontends/bot/`):**
- `assistant.html` - Main AI chatbot interface
- `dashboard.html` - User dashboard with tribe view, achievements, points
- `gamification.html` - Gamification system (badges, leaderboard, achievements)
- `quizzes.html` - Quiz interface with categories and results
- `culturalRecipes.html` - Cultural recipes module
- `interactiveLanguageLearning.html` - Language learning module
- `culturalComparison.html` - Cultural comparison tool
- `art_crafts.html` - Art and crafts showcase
- Additional interactive modules

**Styling:**
- `css/styles.css` - Main stylesheet with responsive design, dark mode support
- `css/enhanced-design.css` - Enhanced UI components, animations, interactive map
- `css/navigation-buttons.css` - Navigation button styling

**JavaScript:**
- `js/main.js` - Core functionality (navigation, smooth scroll, form validation)
- `js/enhanced-design.js` - Interactive elements, map tooltips, card effects
- `js/themeManager.js` - Theme toggle (light/dark mode)
- `js/gamification.js` - Gamification system (points, badges, achievements)

### 2. Backend Layer (`backend/`)

**API Server:**
- `api.py` - Main Flask API with endpoints:
  - `/api/chat` - Chatbot responses
  - `/api/login` - User authentication
  - `/api/register` - User registration
  - `/api/quiz_results` - Quiz result submission
  - `/api/quiz_history` - Quiz history retrieval
  - `/api/tribes` - Tribe data serving
  - `/api/me` - Session authentication check
  - Static file serving for Frontends

- `app.py` - Alternative Flask app with enhanced chatbot integration

**Authentication:**
- `auth.py` - Authentication blueprint with user registration, login, session management
- SQLite database (`users.db`) for user credentials and session data

**Data Management:**
- `tribes_data.json` - Structured tribe data (72+ tribes with detailed sections)
- `quizzes_data.json` - Quiz questions and categories
- `view_data.py` / `view_users.py` - Database inspection utilities

### 3. AI/Chatbot Layer (`cultureAI/`)

**Core Chatbot:**
- `cameroon_chatbot.py` - AdvancedTribesBot class with:
  - Intent detection using regex patterns
  - Multi-layered search (categories, keywords, full-text)
  - Structured JSON data retrieval
  - Fuzzy tribe name matching
  - Hybrid responses (structured data + LLM enhancement via Ollama)
  - Speech input/output (optional)
  - Comprehensive logging and analytics

**Enhanced Chatbot Variants:**
- `super_enhanced_chatbot.py` - SuperEnhancedTribesBot with advanced features
- `enhanced_intelligent_chatbot.py` - Enhanced response generation

**Data Enhancement Scripts:**
- `add_30_tribes.py` - Add new tribes to dataset
- `add_tribe_stories.py` - Add cultural stories
- `enhance_tribes_data.py` - Enhance existing tribe data
- `expand_tribes_data.py` - Expand tribe information
- `merge_tribes.py` - Merge tribe datasets

**Data Files:**
- `intelligent_tribes_data.json` - Main enhanced tribe dataset
- `expanded_tribes_data.json` - Expanded tribe information
- `tribes.json` - Large comprehensive tribe dataset
- Multiple backup and versioned JSON files

### 4. Data Layer

**SQLite Database (`users.db`):**
- Users table (id, email, password_hash, first_name, last_name, created_at)
- Quiz results table (id, user_id, quiz_id, score, total_questions, completed_at)
- Session management via Flask sessions

**JSON Data Files:**
- Tribe data with structured sections:
  - Overview
  - History
  - Culture
  - Traditions
  - Economy
  - Governance
  - Notable Figures
  - Language
  - Religion
  - Arts & Crafts
  - Cuisine
  - Modern Context

- Quiz data with categories, questions, options, correct answers

### 5. AI Logic Layer (`AI_logics/`)

- Text processing utilities
- Cultural data storage and processing

## Key Design Patterns

### 1. Separation of Concerns
- Frontend (presentation) separated from backend (logic)
- AI/Chatbot logic encapsulated in separate module
- Data layer abstracted through JSON files and SQLite

### 2. RESTful API Design
- Standard HTTP methods (GET, POST)
- JSON request/response format
- CORS enabled for cross-origin requests

### 3. Modular Architecture
- Each component (auth, chatbot, gamification) is a separate module
- Easy to add new features without affecting existing code

### 4. Data-Driven AI
- Chatbot responses based on structured JSON data
- Fast retrieval without external API calls
- Fuzzy matching for flexible query handling

### 5. Progressive Enhancement
- Basic functionality works without AI enhancements
- Optional LLM integration (Ollama) for enhanced responses
- Speech features optional (speechrecognition, pyttsx3)

## Technology Stack

**Frontend:**
- HTML5
- CSS3 (with custom properties, flexbox, grid)
- Vanilla JavaScript (no frameworks)
- FontAwesome for icons

**Backend:**
- Python 3.x
- Flask (web framework)
- Flask-CORS (cross-origin support)
- SQLite (database)
- Threading (database lock for concurrent access)

**AI/Chatbot:**
- Standard Python libraries (re, json, difflib, collections)
- Optional: Ollama (LLM integration)
- Optional: speechrecognition, pyttsx3 (speech I/O)

**Data:**
- JSON (structured tribe and quiz data)
- SQLite (user authentication and quiz results)

## Data Flow

### Chatbot Query Flow:
1. User sends message via frontend
2. Frontend POSTs to `/api/chat`
3. Backend routes to chatbot engine
4. Chatbot detects intent and tribe
5. Retrieves relevant data from JSON
6. Generates structured response
7. Optional: Enhances with LLM (Ollama)
8. Returns JSON response to frontend
9. Frontend displays response

### Authentication Flow:
1. User registers via `/api/register`
2. Password hashed and stored in SQLite
3. User logs in via `/api/login`
4. Session created with user_id
5. Subsequent requests check session
6. Protected routes redirect to login if not authenticated

### Quiz Flow:
1. User completes quiz in frontend
2. Frontend POSTs to `/api/quiz_results`
3. Backend stores result in SQLite
4. Gamification system awards points/badges
5. Dashboard updates with new achievements
6. Quiz history retrievable via `/api/quiz_history`

## Security Considerations

- Password hashing (bcrypt in auth.py)
- Session-based authentication
- CORS enabled for specific origins
- Database lock for concurrent access
- Input validation on forms
- SQL injection prevention (parameterized queries)

## Scalability Considerations

- JSON-based data allows easy addition of new tribes
- Modular chatbot design supports multiple bot variants
- SQLite can be replaced with PostgreSQL/MySQL for larger scale
- Static frontend can be served via CDN
- API endpoints can be cached

## Deployment

**Development:**
- `start_backend.bat` - Starts Flask API server
- `start_frontend.bat` - Serves static frontend files
- Both run on localhost:5000

**Production Considerations:**
- Use WSGI server (gunicorn, uWSGI)
- Serve static files via nginx
- Use production-grade database (PostgreSQL)
- Enable HTTPS
- Configure CORS for production domain
- Implement rate limiting
- Add monitoring and logging

## Future Enhancements

- Add more interactive cultural modules
- Implement user profiles and preferences
- Add social features (sharing, comments)
- Integrate more AI models
- Add mobile app (React Native)
- Implement caching layer (Redis)
- Add analytics dashboard
- Multi-language support

## Conclusion

CULTIA follows a clean, modular architecture with clear separation between frontend, backend, and AI components. The JSON-based data approach ensures fast, reliable responses while the modular design allows for easy extension and maintenance. The platform successfully combines traditional web technologies with modern AI capabilities to create an engaging cultural education experience.
