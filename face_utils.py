from deepface import DeepFace
import cv2
import numpy as np

def generate_face_encoding(image_path: str):
    """
    Reads an image and generates a face embedding using DeepFace (Facenet).
    Returns the embedding array or None if no face is found.
    """
    try:
        result = DeepFace.represent(
            img_path=image_path,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=True
        )
        return np.array(result[0]["embedding"])
    except Exception:
        return None

def get_face_encodings(frame_rgb):
    """
    Extracts face encodings from a live frame (RGB numpy array).
    Returns a list of encodings (empty if no faces found).
    """
    try:
        bgr_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        result = DeepFace.represent(
            img_path=bgr_frame,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=True
        )
        return [np.array(r["embedding"]) for r in result]
    except Exception:
        return []

def match_face(known_encoding, frame_rgb, tolerance=0.6):
    """
    Compares a live frame against a known encoding using cosine distance.
    Returns True if a match is found.
    """
    if known_encoding is None:
        return False

    encodings = get_face_encodings(frame_rgb)
    if not encodings:
        return False

    for encoding in encodings:
        a = known_encoding
        b = encoding
        distance = 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        if distance < tolerance:
            return True

    return False
