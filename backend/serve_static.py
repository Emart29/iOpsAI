# backend/serve_static.py - Serve frontend from backend
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount the frontend static files
frontend_path = "../frontend"
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    if os.path.exists(f"{frontend_path}/index.html"):
        return FileResponse(f"{frontend_path}/index.html")
    return {"message": "Frontend files not found"}

@app.get("/dashboard")
async def serve_dashboard():
    if os.path.exists(f"{frontend_path}/dashboard.html"):
        return FileResponse(f"{frontend_path}/dashboard.html")
    return {"message": "Dashboard not found"}

# Import your main app routes
from main import app as main_app
app.include_router(main_app.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)