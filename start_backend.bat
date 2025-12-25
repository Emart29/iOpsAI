@echo off
echo Starting iOps Backend...
cd backend
call venv\Scripts\activate
uvicorn main:app --reload --port 8000
pause
