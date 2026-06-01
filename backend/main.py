from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else reads environment variables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import debate, history
from services.storage import USE_DATABASE


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup, but only if a database is in use.
    if USE_DATABASE:
        from db.database import init_db
        await init_db()
    yield


app = FastAPI(
    title="CognitiveMesh API",
    description="Multi-Agent AI Debate System — Built by Sai Rushitha Bhimavarapu",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debate.router, prefix="/api/debate", tags=["debate"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/")
async def root():
    return {
        "project": "CognitiveMesh",
        "author": "Sai Rushitha Bhimavarapu",
        "github": "https://github.com/sairushitha/cognitivemesh",
        "status": "live",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
