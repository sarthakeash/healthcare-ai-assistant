from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import practice, scenarios, results
from backend.core.config import settings

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    practice.router,
    prefix=f"{settings.api_v1_str}/practice",
    tags=["practice"]
)
app.include_router(
    scenarios.router,
    prefix=f"{settings.api_v1_str}/scenarios",
    tags=["scenarios"]
)
app.include_router(
    results.router,
    prefix=f"{settings.api_v1_str}/results",
    tags=["results"]
)

@app.get("/")
def read_root():
    return {"message": "Healthcare Communication Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}