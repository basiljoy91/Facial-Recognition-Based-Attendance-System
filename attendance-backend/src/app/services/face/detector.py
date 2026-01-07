from typing import List, Tuple

import torch
from facenet_pytorch import MTCNN
from PIL import Image


class FaceDetector:
    """
    Separate detection from recognition to allow swapping detectors.
    """

    def __init__(self, device: str | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.detector = MTCNN(keep_all=True, device=self.device, post_process=True)

    def detect(self, image: Image.Image) -> List[Image.Image]:
        boxes, _ = self.detector.detect(image)
        if boxes is None:
            return []
        faces: List[Image.Image] = []
        for box in boxes:
            x1, y1, x2, y2 = [int(b) for b in box]
            faces.append(image.crop((x1, y1, x2, y2)))
        return faces

