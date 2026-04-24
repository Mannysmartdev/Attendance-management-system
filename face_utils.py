from deepface import DeepFace
import cv2
import numpy as np
import tempfile
import os

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

def get_face_encodings_from_frame(frame_bgr):
    """
    Extracts face encodings from a live BGR frame (numpy array from cv2).
    Writes the frame to a temp file so DeepFace processes it identically
    to registration (file-path based), ensuring consistent embeddings.
    Returns a list of encodings (empty if no faces found).
    """
    tmp_path = None
    try:
        # Save frame to a temporary file so DeepFace processes it
        # via the same file-read path used during registration.
        fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        cv2.imwrite(tmp_path, frame_bgr)

        result = DeepFace.represent(
            img_path=tmp_path,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=True
        )
        return [np.array(r["embedding"]) for r in result]
    except Exception:
        return []
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def match_face(known_encoding, frame_bgr, tolerance=0.6):
    """
    Compares a live BGR frame against a known encoding using cosine distance.
    Returns True if a match is found.
    """
    if known_encoding is None:
        return False

    encodings = get_face_encodings_from_frame(frame_bgr)
    if not encodings:
        return False

    for encoding in encodings:
        a = known_encoding
        b = encoding
        distance = 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        if distance < tolerance:
            return True

    return False
