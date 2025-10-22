from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import championships, users, games, pairings, admin
from app.database import create_tables

app = FastAPI(title="Zehnly Championship API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Include routers
app.include_router(championships.router)
app.include_router(users.router)
app.include_router(games.router)
app.include_router(pairings.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Zehnly Championship API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}