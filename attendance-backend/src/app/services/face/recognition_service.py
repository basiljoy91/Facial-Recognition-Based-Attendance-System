import io
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image

from app.config import get_settings
from app.core.errors import FaceNotDetected, SpoofDetected
from app.core.security import decrypt_bytes, encrypt_bytes
from app.db.models import FaceEmbedding
from app.services.face.detector import FaceDetector
from app.services.face.embedder import FaceEmbedder
from app.services.face.liveness import LivenessResult, LivenessService


@dataclass
class MatchResult:
    user_id: int
    score: float
    liveness: Optional[LivenessResult]


class FaceRecognitionService:
    def __init__(self, detector: FaceDetector | None = None, embedder: FaceEmbedder | None = None, liveness: LivenessService | None = None):
        self.settings = get_settings()
        self.detector = detector or FaceDetector()
        self.embedder = embedder or FaceEmbedder()
        self.liveness = liveness or LivenessService()
        self.model_version = "facenet_v1"

    def _load_image(self, file_bytes: bytes) -> Image.Image:
        return Image.open(io.BytesIO(file_bytes)).convert("RGB")

    def register(self, file_bytes: bytes, strict_liveness: bool = True) -> tuple[np.ndarray, LivenessResult]:
        image = self._load_image(file_bytes)
        faces = self.detector.detect(image)
        if not faces:
            raise FaceNotDetected()
        # Select largest face
        face = sorted(faces, key=lambda f: f.size[0] * f.size[1], reverse=True)[0]
        live_result = self.liveness.evaluate(face)
        if strict_liveness and not live_result.is_live:
            raise SpoofDetected(live_result.reason)
        embedding = self.embedder.embed(face)
        return embedding, live_result

    def find_match(self, file_bytes: bytes, embeddings: list[FaceEmbedding]) -> MatchResult:
        image = self._load_image(file_bytes)
        faces = self.detector.detect(image)
        if not faces:
            raise FaceNotDetected()
        face = faces[0]
        live_result = self.liveness.evaluate(face)
        if not live_result.is_live:
            raise SpoofDetected(live_result.reason)
        query_embedding = self.embedder.embed(face)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        best_score = -1.0
        best_user_id = None
        for stored in embeddings:
            stored_vec = np.array(stored.vector)
            stored_vec = stored_vec / np.linalg.norm(stored_vec)
            score = float(np.dot(query_embedding, stored_vec))
            if score > best_score:
                best_score = score
                best_user_id = stored.user_id

        if best_user_id is None:
            raise FaceNotDetected("No embeddings available")

        return MatchResult(user_id=best_user_id, score=best_score, liveness=live_result)

    def encrypt_embedding(self, embedding: np.ndarray) -> bytes:
        return encrypt_bytes(embedding.tobytes())

    def decrypt_embedding(self, encrypted: bytes) -> np.ndarray:
        data = decrypt_bytes(encrypted)
        return np.frombuffer(data, dtype=np.float32)

