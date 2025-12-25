@echo off
echo ========================================
echo   iOps Backend - Phase 1 Setup
echo ========================================
echo.

REM Check if .env exists
if exist .env (
    echo [OK] .env file found
) else (
    echo [!] Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [!] IMPORTANT: Edit .env and add your API keys:
    echo     - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
    echo     - GROQ_API_KEY (your existing Groq API key)
    echo     - RESEND_API_KEY (optional, for emails - get from https://resend.com/)
    echo.
    pause
)

echo.
echo Starting iOps Backend Server...
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

uvicorn main:app --reload --port 8000
