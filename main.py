from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import sqlite3

# Import your routers
from backend.copilot.router import router as chat_router
from backend.copilot import feedback
from backend.copilot import auth

# ─────────────────────────────────────
# Main App for Static + API Mounting
# ─────────────────────────────────────
app = FastAPI()

# Serve static files from frontend
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "backend" / "static"
INDEX_FILE = STATIC_DIR / "index.html"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    if INDEX_FILE.exists():
        return FileResponse(str(INDEX_FILE))
    return {
        "message": "Static frontend not found",
        "info": "API is running"
    }

# ─────────────────────────────────────
# Sub-App for API Only (Mounted at /api)
# ─────────────────────────────────────
api_app = FastAPI(
    title="AI Chatbot API",
    description="A FastAPI application for AI chatbot with feedback system",
    version="1.0.0"
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers inside API app
api_app.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_app.include_router(feedback.router, tags=["Feedback"])
api_app.include_router(auth.router, tags=["Authentication"])

# Health check
@api_app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running successfully"}

# Optional: Admin chat history
@api_app.get("/admin/chat_history")
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

# Mount the API app at /api
app.mount("/api", api_app)

# Run the app locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
