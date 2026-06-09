# CULTIA Deployment Guide

## Project Structure
- **Backend**: Flask application (serves both main app and admin panel from same server
- **Static Files**: Frontend files in `Frontends/` directory (served as static files
- **Database**: SQLite (for simple deployment)

## Deployment Options (Free)

1. **Render (Recommended)**:
   - Push to GitHub
   - Sign up at [render.com](https://render.com)
   - Create a new **Web Service**
   - Connect your repo
   - Set build command to empty (Render auto-detects requirements.txt)
   - Set start command to: `gunicorn --chdir backend api:app`
   - Add environment variables (e.g., `SECRET_KEY`, `GEMINI_API_KEY` (if used)
   - Deploy!

2. **Vercel**: (Note: For static sites mostly, use with serverless functions for backend**
3. **Railway**: (Easy to use with databases)
4. **Heroku (No longer free, but works)

## Important Notes
- Both main app and admin are on same server! No separate deployment needed!
- Admin is at `/bot/admin.html` (requires admin role)
- To switch to admin in user: make sure your account has `role='admin' in the database
