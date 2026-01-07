from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routers import attendance, auth, users
from app.config import get_settings
from app.core.logging_config import setup_logging
from app.core.security import hash_password
from app.db.models import RoleEnum, User
from app.db.session import Base, SessionLocal, engine
from app.repositories.user_repository import UserRepository

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title="Facial Recognition Attendance", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")


@app.on_event("startup")
def startup_event():
    # Ensure extensions exist
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    # Seed admin if missing
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if not repo.get_admin():
            admin = repo.create_user(
                full_name="System Admin",
                roll_no="ADMIN",
                role=RoleEnum.ADMIN,
                external_id="admin",
                password_hash=hash_password("ChangeMe123!"),
            )
            db.commit()
            db.refresh(admin)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}

