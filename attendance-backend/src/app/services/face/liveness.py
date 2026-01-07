from dataclasses import dataclass
from typing import List

import cv2
import numpy as np
from PIL import Image


@dataclass
class LivenessResult:
    score: int
    is_live: bool
    reason: str


class LivenessService:
    """
    Basic texture-based liveness with clear extension hooks for advanced models.
    """

    def __init__(self, texture_threshold: float = 50.0, blur_threshold: float = 30.0):
        # Lowered thresholds to be less strict for enrollment
        self.texture_threshold = texture_threshold
        self.blur_threshold = blur_threshold

    def _variance_of_laplacian(self, gray: np.ndarray) -> float:
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def _lbp_histogram(self, gray: np.ndarray) -> np.ndarray:
        lbp = np.zeros_like(gray)
        padded = np.pad(gray, pad_width=1, mode="edge")
        for i in range(1, padded.shape[0] - 1):
            for j in range(1, padded.shape[1] - 1):
                center = padded[i, j]
                binary = (
                    (padded[i - 1, j - 1] > center) << 7
                    | (padded[i - 1, j] > center) << 6
                    | (padded[i - 1, j + 1] > center) << 5
                    | (padded[i, j + 1] > center) << 4
                    | (padded[i + 1, j + 1] > center) << 3
                    | (padded[i + 1, j] > center) << 2
                    | (padded[i + 1, j - 1] > center) << 1
                    | (padded[i, j - 1] > center)
                )
                lbp[i - 1, j - 1] = binary
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256), density=True)
        return hist

    def evaluate(self, frame: Image.Image) -> LivenessResult:
        gray = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2GRAY)
        blur = self._variance_of_laplacian(gray)
        texture_hist = self._lbp_histogram(gray)
        texture_score = float(np.var(texture_hist) * 1000)

        # More lenient: pass if either condition is met (OR instead of AND)
        is_live = blur > self.blur_threshold or texture_score > self.texture_threshold
        score = int(min(100, (blur / (self.blur_threshold + 1e-3)) * 40 + (texture_score / (self.texture_threshold + 1e-3)) * 60))
        reason = "pass" if is_live else f"blur={blur:.1f} (need>{self.blur_threshold}), texture={texture_score:.1f} (need>{self.texture_threshold})"
        return LivenessResult(score=score, is_live=is_live, reason=reason)

