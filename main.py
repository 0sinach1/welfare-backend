# main.py
# The entry point of the entire FastAPI application
# This is the file you run to start the backend server

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import packages, pickup, admin, notifications

# Create all database tables if they don't exist yet
# Since we already created them in Supabase, this just verifies they exist
Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(
    title="Welfare Portal API",
    description="Backend API for Landmark University Welfare Package Management System",
    version="1.0.0"
)

# CORS — allows your Next.js frontend to talk to this backend
# Without this, the browser would block all requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",        # Next.js dev server
        "https://*.vercel.app",         # your deployed Vercel frontend
        "*"                             # allow all during development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
# Each router brings in its own group of endpoints
app.include_router(packages.router)
app.include_router(pickup.router)
app.include_router(admin.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    """Health check — visiting the root URL confirms the API is running"""
    return {
        "message": "Welfare Portal API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }