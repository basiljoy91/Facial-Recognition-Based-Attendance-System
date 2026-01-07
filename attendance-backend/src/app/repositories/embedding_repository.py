from typing import Iterable, Optional

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FaceEmbedding


class EmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_embedding(
        self,
        user_id: int,
        model_version: str,
        vector: np.ndarray,
        encrypted_blob: bytes,
        liveness_score: Optional[int],
    ) -> FaceEmbedding:
        existing = self.db.scalar(
            select(FaceEmbedding).where(
                FaceEmbedding.user_id == user_id,
                FaceEmbedding.model_version == model_version,
            )
        )
        if existing:
            existing.vector = vector.tolist()
            existing.encrypted_blob = encrypted_blob
            existing.liveness_score = liveness_score
            self.db.flush()
            return existing

        embedding = FaceEmbedding(
            user_id=user_id,
            model_version=model_version,
            vector=vector.tolist(),
            encrypted_blob=encrypted_blob,
            liveness_score=liveness_score,
        )
        self.db.add(embedding)
        self.db.flush()
        return embedding

    def list_embeddings(self) -> Iterable[FaceEmbedding]:
        stmt = select(FaceEmbedding)
        return self.db.scalars(stmt)

