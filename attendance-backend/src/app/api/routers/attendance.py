from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db_session
from app.config import get_settings
from app.core.errors import DuplicateAttendance, FaceNotDetected, SpoofDetected, WindowViolation
from app.db.models import AttendanceLog
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.schemas.attendance import AttendanceDecision, AttendanceLogOut
from app.services.attendance_service import AttendanceService
from app.services.face.recognition_service import FaceRecognitionService

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/mark", response_model=AttendanceDecision)
def mark_attendance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    face_service = FaceRecognitionService()
    emb_repo = EmbeddingRepository(db)
    attendance_service = AttendanceService(db)
    embeddings = list(emb_repo.list_embeddings())
    if not embeddings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No embeddings registered")

    file_bytes = file.file.read()
    try:
        match = face_service.find_match(file_bytes, embeddings)
    except (FaceNotDetected, SpoofDetected) as exc:
        raise exc

    if match.score < get_settings().similarity_threshold:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face not recognized")

    try:
        log: AttendanceLog = attendance_service.record(
            user_id=match.user_id,
            match_score=match.score,
            liveness_score=match.liveness.score if match.liveness else None,
        )
    except (DuplicateAttendance, WindowViolation) as exc:
        raise exc

    db.commit()
    return AttendanceDecision(
        status=log.type,
        confidence=match.score,
        liveness_score=match.liveness.score if match.liveness else None,
        user_id=match.user_id,
        timestamp=log.timestamp,
    )


@router.post("/manual", response_model=AttendanceDecision)
def manual_override(
    user_id: int,
    note: str,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    attendance_service = AttendanceService(db)
    log = attendance_service.record(user_id=user_id, match_score=1.0, liveness_score=None, manual_override=True, metadata={"note": note, "by": current_user.id})
    db.commit()
    return AttendanceDecision(status=log.type, confidence=1.0, liveness_score=None, user_id=user_id, timestamp=log.timestamp)


@router.get("/logs", response_model=list[AttendanceLogOut])
def list_logs(limit: int = 50, db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    repo = AttendanceRepository(db)
    return repo.get_recent_logs(limit=limit)

