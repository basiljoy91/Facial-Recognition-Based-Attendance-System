# Facial Recognition Attendance Backend

Production-grade FastAPI service for biometric attendance with separate face detection, recognition, and liveness checks.

## Features
- ArcFace-like embeddings via `facenet-pytorch`, separate detection + embedding
- Texture-based liveness (blur + LBP) with hooks for advanced models
- Attendance rules: clock-in/out, windows, grace periods, duplicate cooldown, manual overrides
- pgvector for fast similarity search; encrypted embedding blobs for privacy
- JWT auth, admin-only enrollment, audit logs
- Alembic migrations, Dockerized, env-based configuration

## Quickstart
```bash
cd "Facial Recognition Based Attendance System"
docker-compose up --build
```
Backend runs on `http://localhost:8000`.

## Local (without Docker)
```bash
cd "Facial Recognition Based Attendance System/attendance-backend"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # update secrets and DB
alembic upgrade head
uvicorn app.main:app --reload
```

## Running tests
```bash
cd "Facial Recognition Based Attendance System/attendance-backend"
pytest
```

## API overview
- `POST /api/v1/auth/login` – obtain JWT (default admin: `admin` / `ChangeMe123!`)
- `POST /api/v1/users` – create user (admin)
- `POST /api/v1/users/{id}/enroll` – upload face for enrollment (admin)
- `POST /api/v1/attendance/mark` – mark attendance with face image (auth required)
- `POST /api/v1/attendance/manual` – manual override (auth required)
- `GET /api/v1/attendance/logs` – recent logs

## Notes on security & privacy
- Embeddings stored as vectors for search plus encrypted blobs (Fernet) to avoid plaintext storage of biometric templates.
- No raw images persisted; temporary buffers only in memory.
- Use strong `FERNET_KEY`, `JWT_SECRET`, rotate regularly, and prefer TLS in production.

