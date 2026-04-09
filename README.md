# Lecture Attendance Management System

This web application allows lecturers to mark student attendance automatically using either QR Code scanning or Facial Recognition. It was built using Flask, SQLite, OpenCV, and modern Vanilla web technologies.

## Features

- **Role-based Dashboards**: Admin, Lecturer, and Student accounts.
- **Course & Session Management**: Lecturers can create lectures/sessions for their assigned courses.
- **QR Code Attendance**: Students generate a unique QR code which is scanned by the Lecturer's device webcam (`html5-qrcode`).
- **Facial Recognition Attendance**: Students upload a photo containing their face. The system generates a 128-d face encoding. The Lecturer's device webcam captures frames in-browser, sends them to the backend, and the backend verifies the face against the course students using `face_recognition` and OpenCV.
  - **Optimized Matching Engine**: Calculates high-accuracy best-match distances to quickly identify the exact face among all users preventing false positives and processing lag.
  - **Refined Scanner UI**: Features a tailored circular camera UI, clearly visible alerts, and auto-redirects post-scan for a seamless user experience.
- **Reports**: Lecturers and Admins can download a CSV report of attendance for any session.

## Output Structure

```
attendance_system/
├── app.py                   # Main Flask app initializer
├── models.py                # Database models (User, Course, Session, Attendance)
├── routes.py                # All Flask routes & endpoints
├── face_utils.py            # OpenCV/face_recognition wrapper utilities
├── qr_utils.py              # QR Code generation utilities
├── requirements.txt         # Project dependencies
├── static/
│   ├── css/styles.css       # Clean, modern custom UI styles
│   ├── qrcodes/             # Generated student QR codes
│   └── uploads/             # Uploaded student face images
└── templates/               # Jinja HTML templates
    ├── base.html            # Parent layout
    ├── login.html           # Unified login portal
    ├── admin_dashboard.html # Create users & courses
    ├── lecturer_dashboard.html # Create sessions, start scanners
    ├── student_dashboard.html  # View attendance, upload face, get QR
    └── scanner.html         # Camera UI for QR and Face scanning
```

## How to Run Locally

### 1. Requirements

- **Python 3.12.8** — Required. Do NOT use Python 3.13 or 3.14 as several dependencies (`dlib`, `opencv`, `numpy`) are not yet compatible with those versions.
  - Download: https://www.python.org/downloads/release/python-3128/
  - During install, check ✅ **"Add Python to PATH"**

---

### 2. Install Dependencies

#### Step 1 — Create and activate a virtual environment

```bash
cd attendance_system

py -3.12 -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate
```

#### Step 2 — Upgrade pip, setuptools, and wheel first

```bash
python -m pip install --upgrade pip setuptools wheel
```

#### Step 3 — Install dlib manually (required before installing requirements)

`dlib` has no prebuilt wheel on PyPI for Windows. You must download and install it manually.

1. Go to: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/releases
2. Download: `dlib-19.24.1-cp312-cp312-win_amd64.whl`
   - `cp312` = Python 3.12 (must match your Python version)
   - `win_amd64` = 64-bit Windows
3. Install it:

```bash
pip install C:\path\to\downloads\dlib-19.24.99-cp312-cp312-win_amd64.whl
```

#### Step 4 — Install face_recognition_models from GitHub

```bash
pip install git+https://github.com/ageitgey/face_recognition_models
```

> ⚠️ This package is ~100MB. It may take a few minutes depending on your internet speed. Wait for `Successfully installed face-recognition-models-0.3.0` before moving on.

#### Step 5 — Downgrade setuptools for pkg_resources compatibility

```bash
pip install "setuptools<70"
```

#### Step 6 — Install remaining requirements

```bash
pip install -r requirements.txt
```

> ⚠️ If `Pillow` or `numpy` fail to build from source, install them as prebuilt binaries:
> ```bash
> pip install Pillow --only-binary=:all:
> pip install "numpy<2" --only-binary=:all:
> ```
> Then rerun `pip install -r requirements.txt`

#### Step 7 — Verify face_recognition works

```bash
python -c "import face_recognition; print('OK')"
```

You should see `OK`. If you see a deprecation warning about `pkg_resources`, that is harmless.

---

### 3. Initialize & Run

The database (`database.db`) is automatically created on first startup. Run the app:

```bash
python app.py
```

### 4. Access the Application

Open your browser and navigate to:
**http://127.0.0.1:5000**

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

### 5. Quick Start Flow

1. Login with **admin** credentials. Add a Lecturer and a Student. Add a Course and assign the Lecturer to it.
2. Logout, then login as the **Student**. Click "Generate QR Code" and upload a clear photo of your face.
3. Logout, then login as the **Lecturer**. Click "Create Session" under the assigned course.
4. Click **Scan QR** or **Scan Face** next to the session to begin accepting attendance via webcam. Allow camera permissions in your browser.

---

### Troubleshooting

| Error | Fix |
|-------|-----|
| `Getting requirements to build wheel` failed | Run `pip install <package> --only-binary=:all:` |
| `dlib` build fails / CMake not found | Install dlib manually using the `.whl` file in Step 3 |
| `numpy.core.multiarray failed to import` | Run `pip install "numpy<2"` |
| `No module named 'pkg_resources'` | Run `pip install "setuptools<70"` |
| `Could not build url for endpoint 'login'` | Change `url_for('login')` to `url_for('main.login')` in all templates |
| `cannot import name 'url_decode' from werkzeug` | Run `pip install --upgrade flask-login` |