# Rebuild Backend Instructions

The enrollment endpoint has been updated to completely bypass liveness checks. 
You MUST rebuild the Docker container for changes to take effect.

## Steps:

1. Stop the current containers:
```bash
cd "/Users/basiljoy/VS code/Facial Recognition Based Attendance System"
docker compose -f compose.yml down
```

2. Rebuild and start:
```bash
docker compose -f compose.yml up --build
```

3. Wait for backend to start (you should see "Uvicorn running on http://0.0.0.0:8000")

4. Try uploading a face image again in the admin panel

## What Changed:

- Enrollment now completely bypasses liveness checks
- Only face detection is required
- Liveness score is set to 100 by default for enrollments
- No more "blurred_or_flat_surface" errors during enrollment


