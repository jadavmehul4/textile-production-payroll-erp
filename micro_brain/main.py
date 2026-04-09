from fastapi import FastAPI

app = FastAPI(title="Micro Brain AI", version="0.1.0")

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify system status.
    """
    return {"status": "ok"}

# Router inclusion placeholder
# app.include_router(api_router, prefix="/api/v1")
