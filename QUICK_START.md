# Quick Start Guide

## Start the System

### 1. Start Backend + Database
```bash
cd "/Users/basiljoy/VS code/Facial Recognition Based Attendance System"
docker compose -f compose.yml up --build
```

Wait until you see:
- `PostgreSQL is up - running migrations...`
- `INFO:     Uvicorn running on http://0.0.0.0:8000`

### 2. Start Frontend (in a new terminal)
```bash
cd "/Users/basiljoy/VS code/Facial Recognition Based Attendance System/attendance-frontend"
npm install
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `ChangeMe123!`

### Create User Accounts
1. Login as admin
2. Go to **Admin** tab
3. Fill in user details and create user
4. Upload face image to enroll
5. User can login with their **Roll No** as username

## Troubleshooting

### Backend won't start
- Check Docker logs: `docker compose logs backend`
- Ensure PostgreSQL is healthy: `docker compose ps`
- Verify environment variables are set correctly

### "Failed to fetch" in frontend
- Ensure backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Verify API_BASE_URL in frontend (defaults to http://localhost:8000)

### Database connection errors
- Wait for PostgreSQL to be fully ready (healthcheck passes)
- Check POSTGRES_* environment variables match in compose.yml


