import qrcode
import os
import uuid

def generate_qr_for_user(user, qr_folder):
    """
    Generates a unique QR code for a student.
    We embed the user's ID and a unique UUID to prevent spoofing.
    """
    # Create a unique attendance token
    token = f"{user.id}-{uuid.uuid4().hex}"
    
    # Configure QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    filename = f"user_{user.id}_qr.png"
    filepath = os.path.join(qr_folder, filename)
    img.save(filepath)
    
    return filename, token
