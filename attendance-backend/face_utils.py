import os

try:
    os.environ["TF_USE_LEGACY_KERAS"] = "0"  # force modern tf.keras
    from deepface import DeepFace
    import numpy as np
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    DeepFace = None
    import numpy as np

def extract_face_embedding(image_path: str):
    if not DEEPFACE_AVAILABLE:
        raise ImportError(
            "DeepFace not available. Please use Python 3.11 or compatible TensorFlow version."
        )

    detection_backends = ['retinaface', 'mtcnn', 'opencv']
    last_error = None

    for backend in detection_backends:
        try:
            result = DeepFace.represent(
                img_path=image_path,
                model_name="ArcFace",
                enforce_detection=True,
                detector_backend=backend
            )
            return result[0]["embedding"]
        except Exception as e:
            last_error = str(e)
            continue

    # If all backends fail
    raise ValueError(
        "No face detected. Please upload a clear, front-facing face image with good lighting."
    )

