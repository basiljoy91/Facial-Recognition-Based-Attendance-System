import io

import numpy as np
from PIL import Image

from app.db.models import FaceEmbedding
from app.services.face.recognition_service import FaceRecognitionService
from app.services.face.liveness import LivenessResult


class DummyDetector:
    def detect(self, image):
        return [image]


class DummyEmbedder:
    def embed(self, face):
        return np.ones(512, dtype=np.float32)


class DummyLiveness:
    def evaluate(self, frame):
        return LivenessResult(score=99, is_live=True, reason="pass")


def test_match_selection():
    img = Image.new("RGB", (160, 160), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    data = buf.getvalue()

    service = FaceRecognitionService(detector=DummyDetector(), embedder=DummyEmbedder(), liveness=DummyLiveness())
    embeddings = [
        FaceEmbedding(user_id=1, model_version="facenet_v1", vector=(np.ones(512, dtype=np.float32) * 0.9).tolist(), encrypted_blob=b"x"),
        FaceEmbedding(user_id=2, model_version="facenet_v1", vector=np.ones(512, dtype=np.float32).tolist(), encrypted_blob=b"x"),
    ]

    result = service.find_match(data, embeddings)
    assert result.user_id == 2
    assert result.score > 0.99

