import face_recognition
import cv2
import numpy as np

def generate_face_encoding(image_path):
    """
    Reads an image and generates a 128-d face encoding.
    Returns the encoding array or None if no face is found.
    """
    # Load the image using face_recognition
    image = face_recognition.load_image_file(image_path)
    
    # Find all face encodings in the image
    encodings = face_recognition.face_encodings(image)
    
    if len(encodings) > 0:
        return encodings[0]
    return None

def match_face(known_encoding, frame_rgb, tolerance=0.6):
    """
    Compares a live frame against a known encoding.
    Returns True if a match is found.
    """
    if known_encoding is None:
        return False
        
    # Find face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(frame_rgb)
    
    if not face_locations:
        return False
        
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
    
    # Compare each extracted face encoding against the known encoding
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=tolerance)
        if matches[0]:
            return True
            
    return False
