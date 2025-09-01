import sqlite3
import sys
import os
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.copilot.router import router
from backend.copilot import feedback
from backend.copilot import auth

app = FastAPI(
    title="AI Chatbot API",
    description="A FastAPI application for AI chatbot with feedback system",
    version="1.0.0"
)

# Enable CORS for all origins (for Development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/chat", tags=["Chat"])
app.include_router(feedback.router, tags=["Feedback"])
app.include_router(auth.router, tags=["Authentication"])

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "backend" / "static"
INDEX_FILE = STATIC_DIR / "index.html"

# Debug information (remove in production)
print(f"Base directory: {BASE_DIR}")
print(f"Static directory: {STATIC_DIR}")
print(f"Static directory exists: {STATIC_DIR.exists()}")
print(f"Index file exists: {INDEX_FILE.exists()}")

# Mount static files only if directory exists
if STATIC_DIR.exists() and STATIC_DIR.is_dir():
    try:
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
        print("✅ Static files mounted successfully")
    except Exception as e:
        print(f"❌ Failed to mount static files: {e}")
else:
    print(f"⚠️ Static directory not found at {STATIC_DIR}")

# ✅ Serve index.html as the homepage
@app.get("/")
def serve_index():
    if INDEX_FILE.exists():
        return FileResponse(str(INDEX_FILE))
    else:
        # Return a simple HTML response if index.html doesn't exist
        return """
        <html>
            <head><title>AI Chatbot API</title></head>
            <body>
                <h1>AI Chatbot API</h1>
                <p>API is running successfully!</p>
                <p><a href="/docs">View API Documentation</a></p>
            </body>
        </html>
        """

# ✅ Health check route
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running successfully"}

# ✅ Admin history route
@router.get("/admin/chat_history")
async def get_chat_history():
    try:
        conn = sqlite3.connect("chat_history.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, session_id, sender, message, timestamp FROM chat_messages ORDER BY id DESC LIMIT 500")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=10000,
        reload=True
    )