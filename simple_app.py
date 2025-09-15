"""
Простейшее FastAPI приложение для Railway
"""
from fastapi import FastAPI

app = FastAPI(
    title="Photo to 3D",
    version="1.0.0",
    description="AI-powered photo to 3D model generation service"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Photo to 3D API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0", 
        "mode": "railway_demo"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "v1",
        "status": "operational",
        "endpoints": [
            "/health",
            "/api/v1/status", 
            "/api/v1/generate"
        ]
    }

@app.post("/api/v1/generate")
async def generate_3d():
    """Mock 3D generation endpoint"""
    return {
        "task_id": "demo-task-123",
        "status": "completed",
        "message": "3D model generated successfully (demo mode)",
        "glb_url": "/download/demo-task-123.glb",
        "ply_url": "/download/demo-task-123.ply"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
