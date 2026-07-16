# NEMS: NxtWave Examination Management System

NEMS is a professional, secure, and modern online examination portal designed in alignment with Apple's premium design language. It enables secure online testing for HTML Programming, complete with WebRTC-based live webcam proctoring, strict anti-cheating overrides, and comprehensive administrative controls.

---

## 🎨 Visual Design Specifications
* **Apple Design Language**: Pure space obsidian backgrounds, crisp white glassmorphism container panels, and high-fidelity typography matching SF Pro.
* **Responsive Layouts**: Designed to adapt dynamically across mobile, tablet, and desktop viewports.
* **Theme Modes**: Supports both Apple Dark Mode (default Obsidian Space) and Apple Light Mode (Silver Gray) toggled instantly via client-side controls.
* **Transparent Branding**: Automatically processes and transparency-blends image assets across light and dark interfaces without block borders.

---

## 🔒 Security & Anti-Cheating Protocol
1. **Mandatory Live Webcam Proctoring**: Uses WebRTC `navigator.mediaDevices.getUserMedia` APIs to capture the student's camera stream in a floating mirrored picture-in-picture widget. If the student denies camera access or blocks the device, a security violation is logged, and the exam is auto-submitted instantly.
2. **Dynamic Canvas Snapshotting**: The student's browser samples webcam frames at a compressed `240x180` resolution and `50%` quality every 4 seconds, uploading them via background API requests to keep the server storage light.
3. **Fullscreen Enforcement**: Candidates must remain in fullscreen mode. Exiting fullscreen prompts a strike warning.
4. **Visibility & Focus Monitors**: Tracks browser tab switches (Page Visibility API) and focus loss blurs, logging alerts for any window swaps.
5. **Keystroke & Shortcut Blockers**: Overrides and blocks developer tools (`F12`, `Ctrl+Shift+I/J/C`), view source (`Ctrl+U`), print screens (`Ctrl+P`), page saves (`Ctrl+S`), text copy/cut/paste, selection, and page refresh commands.
6. **3-Strike Autosubmission**: Exceeding 2 security warnings logs the incident and auto-submits the candidate's exam paper immediately, locking the session.

---

## ⚙️ Core Technical Features
* **Randomized & Seeded Layouts**: Every student receives the 100-question syllabus in a randomized order with randomized options. Shuffling is locked to a session-specific seed, ensuring sequence persistence across refreshes.
* **Background Database Auto-save**: Every selected answer is automatically synced to the SQLite backend in the background. If a browser crashes or loses power, the candidate resumes exactly where they left off.
* **Admin Control Panel**:
  * **Interactive Dashboard**: Features score summaries, completion rates, audit log listings, and a **Real-Time Proctoring Monitor** grid showing live-refreshing webcam captures of all active candidates.
  * **Candidate Management**: Registered student roster controls, including registration additions, candidate deletions, and a **Re-allocate Exam** feature to reset a student's session and clear previous attempts.
  * **Question Bank Editor**: Supports search filters, difficulty updates, and bulk question loading via CSV file uploads.
  * **Settings Controls**: Adjust exam timers, active question quotas, passing mark thresholds, and negative marking penalty rates.

---

## 🛠️ Technology Stack
* **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla, WebRTC Media Streams)
* **Backend**: Python Flask (Session controls, secure route middleware, scoring algorithms)
* **Database**: SQLite (SQL query optimization with cascade delete constraints)

---

## 🚀 Setup & Execution Guide

### 1. Install Dependencies
Ensure you have Python installed, then install Flask and the Pillow library (used for automatic transparent asset processing):
```bash
pip install -r requirements.txt
```

### 2. Initialize and Seed the Database
Run the seeder script to build schemas, set up defaults, and populate the database with exactly 100 HTML questions:
```bash
python init_db.py
```

### 3. Start the Web Server
Launch the Flask development server:
```bash
python app.py
```
Open **`http://localhost:5000`** in your web browser.

---

## 🔑 Predefined Test Credentials

### 1. Administrative Portal
* **URL**: [http://localhost:5000/admin](http://localhost:5000/admin)
* **Username / Email**: `nithingowda@nxtwave.in`
* **Password**: `Halonix@2026`

### 2. Student Portals
* **URL**: [http://localhost:5000/](http://localhost:5000/)

#### Candidate 1 (Standard)
* **Student ID / Email**: `saishivani@nxtwave.in`
* **Password**: `saishivani@stu1869`

#### Candidate 2 (Demo Profile)
* **Student ID / Email**: `demo@nxtwave.in`
* **Password**: `demo123`
