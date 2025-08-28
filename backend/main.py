import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from copilot.router import router
from copilot import feedback
from copilot import auth

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Serve index.html as the homepage
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# ✅ Move the health check to a different route
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running successfully"}

# ✅ Admin history route
@router.get("/admin/chat_history")
async def get_chat_history():
    conn = sqlite3.connect("chat_history.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, session_id, sender, message, timestamp FROM chat_messages ORDER BY id DESC LIMIT 500")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
