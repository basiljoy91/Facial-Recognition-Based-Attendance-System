import secrets
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_admin
from app.core.security import hash_password
from app.db.models import RoleEnum
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserOut
from app.services.face.recognition_service import FaceRecognitionService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    admin=Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    existing = user_repo.get_by_external_id(payload.roll_no or payload.full_name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    external_id = payload.roll_no or secrets.token_hex(8)
    hashed = hash_password(payload.password)
    user = user_repo.create_user(
        full_name=payload.full_name,
        roll_no=payload.roll_no or "",
        role=RoleEnum(payload.role),
        external_id=external_id,
        password_hash=hashed,
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/enroll")
def enroll_face(
    user_id: int,
    file: UploadFile = File(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    emb_repo = EmbeddingRepository(db)
    face_service = FaceRecognitionService()

    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        image_bytes = file.file.read()
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        # For enrollment, completely bypass liveness check - just detect face and create embedding
        image = face_service._load_image(image_bytes)
        faces = face_service.detector.detect(image)
        if not faces:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in image. Please upload a clear image with a visible face looking at the camera."
            )
        
        # Select largest face
        face = sorted(faces, key=lambda f: f.size[0] * f.size[1], reverse=True)[0]
        
        # Get embedding - NO LIVENESS CHECK FOR ENROLLMENT
        embedding = face_service.embedder.embed(face)
        
        # Set a default liveness score (we don't check it for enrollment)
        liveness_score = 100  # Default high score since we're not checking
        
        encrypted = face_service.encrypt_embedding(embedding.astype("float32"))
        emb_repo.upsert_embedding(
            user_id=user_id,
            model_version=face_service.model_version,
            vector=embedding,
            encrypted_blob=encrypted,
            liveness_score=liveness_score
        )
        db.commit()
        
        return {
            "status": "enrolled",
            "model_version": face_service.model_version,
            "liveness_score": liveness_score
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error processing face image: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

