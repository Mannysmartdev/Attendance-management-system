import os
from flask import render_template, redirect, url_for, flash, request, Blueprint, jsonify, current_app, Response
from flask_login import login_user, logout_user, login_required, current_user
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import csv
import io

from models import db, User, Course, Session, Attendance
from qr_utils import generate_qr_for_user
import face_utils

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'main.{current_user.role}_dashboard'))
            
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        from app import bcrypt
        if user and bcrypt.check_password_hash(user.password, password):
            if user.role == 'student':
                flash('Student login is not available. Contact your lecturer or admin.', 'danger')
                return render_template('login.html')
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect(url_for(f'main.{user.role}_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'main.{current_user.role}_dashboard'))
            
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        department = request.form.get('department')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username/Matric No already exists. Please login.', 'danger')
            return redirect(url_for('main.register'))
            
        from app import bcrypt
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_pw, role='student', name=name, department=department)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_user':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            name = request.form.get('name')
            dept = request.form.get('department')
            
            from app import bcrypt
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_pw, role=role, name=name, department=dept)
            db.session.add(new_user)
            db.session.commit()
            
            if role == 'student':
                current_user.registered_students.append(new_user)
                db.session.commit()

                # Handle optional photo upload for face encoding
                if 'photo' in request.files and request.files['photo'].filename != '':
                    file = request.files['photo']
                    filename = secure_filename(f"student_{new_user.id}_{file.filename}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    encoding = face_utils.generate_face_encoding(filepath)
                    if encoding is not None:
                        new_user.photo_path = filename
                        new_user.face_encoding = json.dumps(encoding.tolist())
                        db.session.commit()
                        flash(f'Student {name} registered with face enrolled!', 'success')
                    else:
                        flash(f'Student {name} registered but no face detected.', 'warning')
                else:
                    flash(f'User {name} added!', 'success')
            else:
                flash(f'User {name} added!', 'success')
            
        elif action == 'add_course':
            code = request.form.get('course_code')
            name = request.form.get('course_name')
            lecturer_id = request.form.get('lecturer_id')
            new_course = Course(course_code=code, course_name=name, lecturer_id=lecturer_id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course added!', 'success')
            
        elif action == 'delete_user':
            user_id = request.form.get('user_id')
            user_to_delete = User.query.get(user_id)
            if user_to_delete:
                if user_to_delete.id != current_user.id:
                    db.session.delete(user_to_delete)
                    db.session.commit()
                    flash(f'User {user_to_delete.name} deleted successfully!', 'success')
                else:
                    flash('You cannot delete yourself!', 'danger')
                    
        elif action == 'delete_course':
            course_id = request.form.get('course_id')
            course_to_delete = Course.query.get(course_id)
            if course_to_delete:
                db.session.delete(course_to_delete)
                db.session.commit()
                flash(f'Course {course_to_delete.course_code} deleted successfully!', 'success')
            
    users = User.query.all()
    courses = Course.query.all()
    lecturers = User.query.filter_by(role='lecturer').order_by(User.id.desc()).all()
    students = User.query.filter_by(role='student').order_by(User.id.desc()).all()
    return render_template('admin_dashboard.html', users=users, courses=courses, lecturers=lecturers, students=students)

@main.route('/lecturer', methods=['GET', 'POST'])
@login_required
def lecturer_dashboard():
    if current_user.role != 'lecturer':
        return redirect(url_for('main.login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_session':
            course_id = request.form.get('course_id')
            date_str = request.form.get('date')
            start_str = request.form.get('start_time')
            end_str = request.form.get('end_time')
            
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_obj = datetime.strptime(start_str, '%H:%M').time()
            end_obj = datetime.strptime(end_str, '%H:%M').time()
            
            new_session = Session(course_id=course_id, date=date_obj, start_time=start_obj, end_time=end_obj)
            db.session.add(new_session)
            db.session.commit()
            flash('Session created!', 'success')

        elif action == 'add_student':
            name = request.form.get('name')
            username = request.form.get('username')
            password = request.form.get('password')
            dept = request.form.get('department')

            existing = User.query.filter_by(username=username).first()
            if existing:
                if existing.role == 'student':
                    if existing in current_user.registered_students:
                        flash(f'Student {name} is already in your list.', 'info')
                    else:
                        current_user.registered_students.append(existing)
                        db.session.commit()
                        flash(f'Student {name} added to your list.', 'success')
                else:
                    flash('A non-student user with that Matric Number already exists.', 'danger')
            else:
                from app import bcrypt
                hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
                new_student = User(username=username, password=hashed_pw, role='student', name=name, department=dept)
                db.session.add(new_student)
                current_user.registered_students.append(new_student)
                db.session.commit()

                # Handle optional photo upload for face encoding
                if 'photo' in request.files and request.files['photo'].filename != '':
                    file = request.files['photo']
                    filename = secure_filename(f"student_{new_student.id}_{file.filename}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    encoding = face_utils.generate_face_encoding(filepath)
                    if encoding is not None:
                        new_student.photo_path = filename
                        new_student.face_encoding = json.dumps(encoding.tolist())
                        db.session.commit()
                        flash(f'Student {name} registered with face enrolled and added to your list!', 'success')
                    else:
                        flash(f'Student {name} registered but no face detected. Added to your list.', 'warning')
                else:
                    flash(f'Student {name} registered successfully and added to your list!', 'success')

        elif action == 'delete_student':
            student_id = request.form.get('student_id')
            student = User.query.get(student_id)
            if student and student.role == 'student':
                if student in current_user.registered_students:
                    current_user.registered_students.remove(student)
                    db.session.commit()
                    flash(f'Student {student.name} removed from your list.', 'success')
                else:
                    flash('You are not authorized to remove this student.', 'danger')

    courses = current_user.courses
    sessions = Session.query.join(Course).filter(Course.lecturer_id == current_user.id).order_by(Session.date.desc()).all()
    students = current_user.registered_students
    return render_template('lecturer_dashboard.html', courses=courses, sessions=sessions, students=students)

@main.route('/student', methods=['GET', 'POST'])
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('main.login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'generate_qr':
            filename, _ = generate_qr_for_user(current_user, current_app.config['QR_FOLDER'])
            current_user.qr_code_path = filename
            db.session.commit()
            flash('QR Code generated/updated successfully.', 'success')
            
        elif action == 'upload_photo':
            if 'photo' not in request.files:
                flash('No file part', 'danger')
            else:
                file = request.files['photo']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    encoding = face_utils.generate_face_encoding(filepath)
                    if encoding is not None:
                        current_user.photo_path = filename
                        current_user.face_encoding = json.dumps(encoding.tolist())
                        db.session.commit()
                        flash('Photo uploaded and face encoding generated successfully!', 'success')
                    else:
                        flash('Could not find a face in the image. Please try another.', 'danger')

    attendances = Attendance.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', attendances=attendances, user=current_user)

@main.route('/scanner/<type>/<int:session_id>')
@login_required
def scanner(type, session_id):
    if current_user.role != 'lecturer':
        return redirect(url_for('main.login'))
    
    session = Session.query.get_or_404(session_id)
    if session.course.lecturer_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.lecturer_dashboard'))
        
    return render_template('scanner.html', type=type, session=session)

@main.route('/api/mark_qr', methods=['POST'])
@login_required
def api_mark_qr():
    data = request.json
    token = data.get('token')
    session_id = data.get('session_id')
    
    if not token or not session_id:
        return jsonify({'success': False, 'message': 'Invalid data'})
        
    try:
        student_id_str = token.split('-')[0]
        student_id = int(student_id_str)
        student = User.query.get(student_id)
        
        if not student or student.role != 'student':
            return jsonify({'success': False, 'message': 'Invalid QR Code'})
            
        # Check duplicate
        exists = Attendance.query.filter_by(session_id=session_id, student_id=student.id).first()
        if exists:
            return jsonify({'success': False, 'message': f'Attendance already marked for {student.name}'})
            
        new_att = Attendance(session_id=session_id, student_id=student.id, method='QR Code')
        db.session.add(new_att)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Attendance marked for {student.name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main.route('/api/mark_face', methods=['POST'])
@login_required
def api_mark_face():
    # Receive base64 image or multipart form data
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'})
        
    session_id = request.form.get('session_id')
    file = request.files['image']
    
    import cv2
    import numpy as np
    
    # Read image — keep as BGR (OpenCV default), do NOT convert to RGB.
    # This matches how DeepFace reads images from file paths during registration.
    in_memory_file = file.read()
    nparr = np.frombuffer(in_memory_file, np.uint8)
    frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame_bgr is None:
        return jsonify({'success': False, 'message': 'Could not decode the image'})

    # Extract face encodings from the webcam frame ONCE
    # Pass BGR frame directly — get_face_encodings_from_frame writes it to a
    # temp file so DeepFace processes it via the exact same code path used
    # during registration, guaranteeing consistent embeddings.
    live_encodings = face_utils.get_face_encodings_from_frame(frame_bgr)
    if not live_encodings:
        return jsonify({'success': False, 'message': 'No face found in the image'})
        
    # Use the first face found in the frame
    live_encoding = live_encodings[0]

    # Get all students with face encodings
    students = User.query.filter(User.role == 'student', User.face_encoding.isnot(None)).all()
    if not students:
        return jsonify({'success': False, 'message': 'No registered student faces available'})
    
    known_encodings = []
    student_list = []
    for student in students:
        encoding = np.array(json.loads(student.face_encoding))
        known_encodings.append(encoding)
        student_list.append(student)
        
    matched_student = None
    if known_encodings:
        def cosine_distance(a, b):
            return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        distances = [cosine_distance(live_encoding, enc) for enc in known_encodings]
        best_match_index = np.argmin(distances)
        if distances[best_match_index] <= 0.5:
            matched_student = student_list[best_match_index]
            
    if matched_student:
        # Check duplicate
        exists = Attendance.query.filter_by(session_id=session_id, student_id=matched_student.id).first()
        if exists:
            return jsonify({'success': False, 'message': f'Attendance already marked for {matched_student.name}'})
            
        new_att = Attendance(session_id=session_id, student_id=matched_student.id, method='Facial Recognition')
        db.session.add(new_att)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Attendance marked for {matched_student.name}'})
    
    return jsonify({'success': False, 'message': 'No registered face matched'})

@main.route('/report/<int:session_id>')
@login_required
def download_report(session_id):
    if current_user.role != 'lecturer' and current_user.role != 'admin':
        return redirect(url_for('main.login'))
        
    session = Session.query.get_or_404(session_id)
    attendances = session.attendances
    
    # Generate CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name', 'Matric Number', 'Department', 'Time', 'Method'])
    for att in attendances:
        cw.writerow([att.student.name, att.student.username, att.student.department, att.timestamp.strftime('%Y-%m-%d %H:%M:%S'), att.method])
        
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = f"attachment; filename=attendance_session_{session_id}.csv"
    return output

@main.route('/print_report/<int:session_id>')
@login_required
def print_report(session_id):
    if current_user.role != 'lecturer' and current_user.role != 'admin':
        return redirect(url_for('main.login'))
        
    session = Session.query.get_or_404(session_id)
    attendances = session.attendances
    
    return render_template('print_report.html', session=session, attendances=attendances)

@main.route('/view_attendance/<int:session_id>')
@login_required
def view_attendance(session_id):
    if current_user.role != 'lecturer' and current_user.role != 'admin':
        return redirect(url_for('main.login'))
        
    session = Session.query.get_or_404(session_id)
    attendances = session.attendances
    
    return render_template('view_attendance.html', session=session, attendances=attendances)
