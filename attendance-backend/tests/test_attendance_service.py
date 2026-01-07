from datetime import timedelta, timezone, datetime, date

from app.core.security import hash_password
from app.db.models import AttendanceTypeEnum, User
from app.repositories.attendance_repository import AttendanceRepository
from app.services.attendance_service import AttendanceService


def test_attendance_clock_in_out(db_session):
    db = db_session
    user = User(full_name="Test User", roll_no="T1", role="STUDENT", external_id="t1", password_hash=hash_password("pass"))
    db.add(user)
    db.commit()

    service = AttendanceService(db)

    # First record -> CLOCK_IN
    log1 = service.record(user_id=user.id, match_score=0.9, liveness_score=95)
    assert log1.type == AttendanceTypeEnum.CLOCK_IN.value

    # Move time forward to avoid duplicate protection
    log1.timestamp = datetime.now(timezone.utc) - timedelta(minutes=10)
    db.commit()

    log2 = service.record(user_id=user.id, match_score=0.92, liveness_score=96)
    assert log2.type == AttendanceTypeEnum.CLOCK_OUT.value


def test_duplicate_prevention(db_session):
    db = db_session
    user = User(full_name="Test User", roll_no="T2", role="STUDENT", external_id="t2", password_hash=hash_password("pass"))
    db.add(user)
    db.commit()

    service = AttendanceService(db)
    service.record(user_id=user.id, match_score=0.9, liveness_score=90)
    try:
        service.record(user_id=user.id, match_score=0.91, liveness_score=91)
        assert False, "Expected duplicate prevention"
    except Exception:
        assert True

