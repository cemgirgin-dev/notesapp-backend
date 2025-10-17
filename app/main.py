from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, notes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes App API", version="0.1.0")

# Allow SwiftUI client development from localhost and iOS simulators.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
