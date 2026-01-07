from fastapi import HTTPException, status


class FaceNotDetected(HTTPException):
    def __init__(self, message: str = "Face not detected"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class SpoofDetected(HTTPException):
    def __init__(self, message: str = "Liveness check failed"):
        # Changed to 400 since this is a validation error, not authentication
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class UnauthorizedAction(HTTPException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class DuplicateAttendance(HTTPException):
    def __init__(self, message: str = "Duplicate attendance attempt"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class WindowViolation(HTTPException):
    def __init__(self, message: str = "Outside attendance window"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

