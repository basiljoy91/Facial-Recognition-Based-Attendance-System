from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import uuid
from face_utils import extract_face_embedding
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date, datetime
from attendance_utils import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/attendance/list")
def get_attendance():
    # Join attendance with users to get names
    response = supabase.table("attendance") \
        .select("id, user_id, date, entry_time, exit_time, users(name, roll_no)") \
        .order("date", desc=True) \
        .order("entry_time", desc=True) \
        .execute()
    
    # Format the response to flatten the user data
    formatted_data = []
    for record in response.data:
        user_info = record.get("users", {})
        formatted_data.append({
            "id": record["id"],
            "user_id": record["user_id"],
            "name": user_info.get("name", "Unknown"),
            "roll_no": user_info.get("roll_no", "N/A"),
            "date": record["date"],
            "entry_time": record["entry_time"],
            "exit_time": record["exit_time"]
        })
    
    return formatted_data


@app.get("/")
def root():
    return {"status": "backend running"}

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/webp"
}

@app.post("/add-user")
def add_user(
    name: str = Form(...),
    roll_no: str = Form(...),
    file: UploadFile = File(...)
):
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Please upload an image file (JPEG, PNG, or WebP). Received: {file.content_type or 'unknown'}"
        )
    
    # Determine file extension from content type
    extension_map = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }
    extension = extension_map.get(file.content_type, ".jpg")
    
    # Save temp image
    image_path = f"temp_{uuid.uuid4()}{extension}"
    
    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract face embedding
        try:
            embedding = extract_face_embedding(image_path)
        except ImportError as e:
            # Clean up temp file before returning error
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=503,
                detail=str(e) + " The face recognition feature is currently unavailable."
            )
        except ValueError as e:
            # Face detection errors - provide user-friendly message
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            # Clean up temp file before returning error
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing face embedding: {str(e)}"
            )

        # Insert into Supabase
        try:
            supabase.table("users").insert({
                "name": name,
                "roll_no": roll_no,
                "face_embedding": list(embedding),
            }).execute()
        except Exception as e:
            # Clean up temp file before returning error
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error saving to database: {str(e)}"
            )

        # Remove temp image
        if os.path.exists(image_path):
            os.remove(image_path)

        return {"status": "success", "message": "User added successfully"}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up temp file in case of any other error
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.post("/mark-attendance")
def mark_attendance(file: UploadFile = File(...)):
    # Save temp image
    image_path = f"temp_{uuid.uuid4()}.jpg"

    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract face embedding
        current_embedding = extract_face_embedding(image_path)

        # Fetch all users
        users = supabase.table("users").select("id, face_embedding").execute().data

        if not users:
            raise HTTPException(status_code=404, detail="No users registered")

        best_match = None
        best_score = 0.0

        for user in users:
            stored_embedding = user.get("face_embedding")

            # Skip users without embeddings
            if stored_embedding is None:
                continue

            score = cosine_similarity(current_embedding, stored_embedding)

            if score > best_score:
                best_score = score
                best_match = user


        # Threshold check
        if best_score < 0.50:
            raise HTTPException(
                status_code=401,
                detail="Face not recognized"
            )

        user_id = best_match["id"]
        today = date.today().isoformat()

        # Check existing attendance
        attendance = supabase.table("attendance") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("date", today) \
            .execute() \
            .data

        now = datetime.utcnow().isoformat()

        if not attendance:
            # ENTRY
            supabase.table("attendance").insert({
                "user_id": user_id,
                "date": today,
                "entry_time": now
            }).execute()

            return {"status": "ENTRY", "confidence": best_score}

        elif attendance[0]["exit_time"] is None:
            # EXIT
            supabase.table("attendance") \
                .update({"exit_time": now}) \
                .eq("id", attendance[0]["id"]) \
                .execute()

            return {"status": "EXIT", "confidence": best_score}

        else:
            raise HTTPException(
                status_code=400,
                detail="Attendance already completed for today"
            )

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
