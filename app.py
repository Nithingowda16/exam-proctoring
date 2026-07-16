import os
import random
import csv
import shutil
import sys
import subprocess
from io import StringIO
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# Automatically copy the uploaded NxtWave logo and make it transparent
logo_src = r"C:\Users\nithi\.gemini\antigravity-ide\brain\93f55d35-220c-4b35-849b-cf9f69761310\media__1784179501385.png"
logo_dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
logo_dest_path = os.path.join(logo_dest_dir, "logo.png")

os.makedirs(logo_dest_dir, exist_ok=True)
if os.path.exists(logo_src):
    try:
        shutil.copy(logo_src, logo_dest_path)
        
        # Self-install Pillow if not installed, then make logo transparent
        try:
            from PIL import Image
        except ImportError:
            print("Installing Pillow for transparent logo processing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
            from PIL import Image
            
        # Open image and convert to RGBA
        img = Image.open(logo_dest_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # If the pixel is white or off-white, make it transparent
            if item[0] > 230 and item[1] > 230 and item[2] > 230:
                newData.append((255, 255, 255, 0)) # Alpha = 0
            else:
                newData.append(item)
                
        img.putdata(newData)
        img.save(logo_dest_path, "PNG")
        print("Logo successfully converted to transparent PNG.")
    except Exception as e:
        print(f"Error processing transparent logo: {e}")

app = Flask(__name__)
app.secret_key = "secure_html_exam_key_apple_glassmorphism_2026"
app.permanent_session_lifetime = timedelta(hours=3)

# Auto-migrate: Add latest_frame column to exam_sessions if missing
conn = get_db_connection()
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE exam_sessions ADD COLUMN latest_frame TEXT;")
    conn.commit()
except Exception:
    pass
conn.close()

# ----------------- Database Helpers -----------------
def get_settings():
    """Retrieves all configuration settings from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM exam_settings;")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()
    
    # Defaults in case settings are missing
    return {
        "passing_marks": float(settings.get("passing_marks", 50)),
        "negative_marking": float(settings.get("negative_marking", 0)),
        "duration_minutes": int(settings.get("duration_minutes", 100)),
        "total_questions": int(settings.get("total_questions", 100))
    }

# ----------------- Middlewares -----------------
@app.before_request
def load_logged_in_user():
    """Loads logged-in student or admin details into flask.g context."""
    g.student = None
    g.admin = None
    
    if "student_id" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?;", (session["student_id"],))
        g.student = cursor.fetchone()
        conn.close()
        
    if "admin_id" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?;", (session["admin_id"],))
        g.admin = cursor.fetchone()
        conn.close()

# ----------------- Student Routes -----------------
@app.route("/", methods=["GET", "POST"])
def index():
    """Student Login & Registration portal."""
    if g.student:
        return redirect(url_for("instructions"))
        
    error = None
    success = None
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "login":
            student_id = request.form.get("student_id", "").strip()
            password = request.form.get("password", "")
            
            # Enforce access only to saishivani@nxtwave.in and demo@nxtwave.in
            if student_id not in ["saishivani@nxtwave.in", "demo@nxtwave.in"]:
                error = "Access restricted. Please contact the admin."
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id,))
                student = cursor.fetchone()
                conn.close()
                
                if student and check_password_hash(student["password_hash"], password):
                    session.clear()
                    session["student_id"] = student["id"]
                    session.permanent = True
                    return redirect(url_for("instructions"))
                else:
                    error = "Invalid Student ID or Password."
                
        elif action == "register":
            # Restrict student registrations entirely
            error = "Registration is restricted. Please contact the admin."
                        
    return render_template("index.html", error=error, success=success)

@app.route("/logout")
def logout():
    """Logs out the student or admin."""
    session.clear()
    return redirect(url_for("index"))

@app.route("/instructions")
def instructions():
    """Shows rules and instructions before starting the exam."""
    if not g.student:
        return redirect(url_for("index"))
        
    settings = get_settings()
    
    # Check if they have an ongoing active session
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM exam_sessions WHERE student_id = ? AND is_submitted = 0;",
        (g.student["id"],)
    )
    session_row = cursor.fetchone()
    
    # Check if they have a completed exam
    cursor.execute(
        "SELECT * FROM exam_sessions WHERE student_id = ? AND is_submitted = 1;",
        (g.student["id"],)
    )
    completed_session = cursor.fetchone()
    conn.close()
    
    # If completed, redirect to results directly
    if completed_session:
        return redirect(url_for("results"))
        
    return render_template(
        "exam_instructions.html",
        settings=settings,
        has_active_session=session_row is not None
    )

@app.route("/start_exam", methods=["POST"])
def start_exam():
    """Starts the exam, randomizes question/option ordering, and redirects to exam screen."""
    if not g.student:
        return redirect(url_for("index"))
        
    settings = get_settings()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for completed session
    cursor.execute(
        "SELECT id FROM exam_sessions WHERE student_id = ? AND is_submitted = 1;",
        (g.student["id"],)
    )
    if cursor.fetchone():
        conn.close()
        return redirect(url_for("results"))
        
    # Check for active session
    cursor.execute(
        "SELECT id, expires_at FROM exam_sessions WHERE student_id = ? AND is_submitted = 0;",
        (g.student["id"],)
    )
    session_row = cursor.fetchone()
    
    if not session_row:
        # Create a new session
        duration_minutes = settings["duration_minutes"]
        started_at = datetime.now()
        expires_at = started_at + timedelta(minutes=duration_minutes)
        random_seed = random.randint(1, 1000000)
        
        cursor.execute(
            "INSERT INTO exam_sessions (student_id, started_at, expires_at, is_submitted, random_seed) VALUES (?, ?, ?, 0, ?);",
            (g.student["id"], started_at.strftime("%Y-%m-%d %H:%M:%S"), expires_at.strftime("%Y-%m-%d %H:%M:%S"), random_seed)
        )
        session_id = cursor.lastrowid
        
        # Pull 100 questions (or as many as available up to setting limit)
        cursor.execute("SELECT id FROM questions;")
        question_rows = cursor.fetchall()
        all_q_ids = [row["id"] for row in question_rows]
        
        # Seed and shuffle questions
        rng = random.Random(random_seed)
        rng.shuffle(all_q_ids)
        
        limit = min(settings["total_questions"], len(all_q_ids))
        selected_q_ids = all_q_ids[:limit]
        
        # Insert question order
        for idx, q_id in enumerate(selected_q_ids, 1):
            cursor.execute(
                "INSERT INTO exam_question_order (session_id, question_id, display_order) VALUES (?, ?, ?);",
                (session_id, q_id, idx)
            )
            
            # Fetch options for this question and shuffle
            cursor.execute("SELECT id FROM options WHERE question_id = ?;", (q_id,))
            opt_rows = cursor.fetchall()
            opt_ids = [o["id"] for o in opt_rows]
            rng.shuffle(opt_ids)
            
            # Insert option order
            for opt_idx, opt_id in enumerate(opt_ids, 1):
                cursor.execute(
                    "INSERT INTO exam_option_order (session_id, question_id, option_id, display_order) VALUES (?, ?, ?, ?);",
                    (session_id, q_id, opt_id, opt_idx)
                )
        conn.commit()
    
    conn.close()
    return redirect(url_for("exam_window"))

@app.route("/exam")
def exam_window():
    """Main exam window."""
    if not g.student:
        return redirect(url_for("index"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for active session
    cursor.execute(
        "SELECT * FROM exam_sessions WHERE student_id = ? AND is_submitted = 0;",
        (g.student["id"],)
    )
    session_row = cursor.fetchone()
    
    if not session_row:
        conn.close()
        return redirect(url_for("instructions"))
        
    # Check if session is expired
    expires_at = datetime.strptime(session_row["expires_at"], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    
    if now >= expires_at:
        conn.close()
        # Trigger auto-submit
        return redirect(url_for("submit_exam_action"))
        
    remaining_seconds = int((expires_at - now).total_seconds())
    session_id = session_row["id"]
    
    # Load questions in display order
    cursor.execute(
        """
        SELECT q.id, q.question_text, q.category, q.difficulty, eqo.display_order 
        FROM exam_question_order eqo
        JOIN questions q ON eqo.question_id = q.id
        WHERE eqo.session_id = ?
        ORDER BY eqo.display_order ASC;
        """,
        (session_id,)
    )
    questions = cursor.fetchall()
    
    # Load options in randomized order for each question
    cursor.execute(
        """
        SELECT eoo.question_id, o.id as option_id, o.option_text 
        FROM exam_option_order eoo
        JOIN options o ON eoo.option_id = o.id
        WHERE eoo.session_id = ?
        ORDER BY eoo.question_id, eoo.display_order ASC;
        """,
        (session_id,)
    )
    all_options = cursor.fetchall()
    
    options_by_q = {}
    for opt in all_options:
        q_id = opt["question_id"]
        if q_id not in options_by_q:
            options_by_q[q_id] = []
        options_by_q[q_id].append(opt)
        
    # Load existing answers
    cursor.execute(
        "SELECT question_id, selected_option_id, marked_for_review FROM student_answers WHERE session_id = ?;",
        (session_id,)
    )
    saved_answers = {row["question_id"]: {"option_id": row["selected_option_id"], "marked": row["marked_for_review"]} for row in cursor.fetchall()}
    
    conn.close()
    
    settings = get_settings()
    
    return render_template(
        "exam.html",
        student=g.student,
        session_id=session_id,
        questions=questions,
        options_by_q=options_by_q,
        saved_answers=saved_answers,
        remaining_seconds=remaining_seconds,
        settings=settings
    )

# ----------------- Student API Routes (AJAX) -----------------
@app.route("/api/save_answer", methods=["POST"])
def save_answer():
    """Saves answer selections dynamically."""
    if not g.student:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    selected_option_id = data.get("selected_option_id") # Can be None if cleared
    
    if not session_id or not question_id:
        return jsonify({"success": False, "error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify session belongs to the current student and is active
    cursor.execute(
        "SELECT id, expires_at, is_submitted FROM exam_sessions WHERE id = ? AND student_id = ?;",
        (session_id, g.student["id"])
    )
    session_row = cursor.fetchone()
    
    if not session_row or session_row["is_submitted"] == 1:
        conn.close()
        return jsonify({"success": False, "error": "Session closed or invalid"}), 403
        
    expires_at = datetime.strptime(session_row["expires_at"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() >= expires_at:
        conn.close()
        return jsonify({"success": False, "error": "Time expired"}), 403
        
    # Insert or update
    cursor.execute(
        """
        INSERT INTO student_answers (session_id, question_id, selected_option_id, updated_at) 
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id, question_id) DO UPDATE SET 
            selected_option_id = excluded.selected_option_id,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (session_id, question_id, selected_option_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/api/mark_review", methods=["POST"])
def mark_review():
    """Toggles marked for review state of a question."""
    if not g.student:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    marked = 1 if data.get("marked") else 0
    
    if not session_id or not question_id:
        return jsonify({"success": False, "error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, is_submitted, expires_at FROM exam_sessions WHERE id = ? AND student_id = ?;",
        (session_id, g.student["id"])
    )
    session_row = cursor.fetchone()
    
    if not session_row or session_row["is_submitted"] == 1:
        conn.close()
        return jsonify({"success": False, "error": "Session closed"}), 403
        
    # Set marked flag. Ensure the row exists first
    cursor.execute(
        """
        INSERT INTO student_answers (session_id, question_id, marked_for_review, updated_at) 
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id, question_id) DO UPDATE SET 
            marked_for_review = excluded.marked_for_review,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (session_id, question_id, marked)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/log_violation", methods=["POST"])
def log_violation():
    """Logs browser cheating violations and submits exam on 3rd warning."""
    if not g.student:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    session_id = data.get("session_id")
    violation_type = data.get("violation_type")
    
    if not session_id or not violation_type:
        return jsonify({"success": False, "error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, is_submitted FROM exam_sessions WHERE id = ? AND student_id = ?;",
        (session_id, g.student["id"])
    )
    session_row = cursor.fetchone()
    
    if not session_row or session_row["is_submitted"] == 1:
        conn.close()
        return jsonify({"success": False, "error": "Session inactive"}), 403
        
    # Count current violations to calculate warning number
    cursor.execute("SELECT COUNT(*) FROM violations WHERE session_id = ?;", (session_id,))
    v_count = cursor.fetchone()[0]
    warning_number = v_count + 1
    
    # Log violation
    cursor.execute(
        "INSERT INTO violations (session_id, violation_type, warning_number) VALUES (?, ?, ?);",
        (session_id, violation_type, warning_number)
    )
    conn.commit()
    
    auto_submit = False
    if warning_number >= 3:
        # Submit the exam automatically
        auto_submit = True
        conn.close()
        submit_exam_processing(session_id, g.student["id"])
    else:
        conn.close()
        
    return jsonify({
        "success": True, 
        "warning_number": warning_number, 
        "auto_submit": auto_submit
    })

@app.route("/api/upload_frame", methods=["POST"])
def upload_frame():
    """Endpoint for students to upload their live webcam frames."""
    if not g.student:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    session_id = data.get("session_id")
    frame_data = data.get("frame")
    
    if not session_id or not frame_data:
        return jsonify({"success": False, "error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE exam_sessions SET latest_frame = ? WHERE id = ? AND student_id = ? AND is_submitted = 0;",
        (frame_data, session_id, g.student["id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/active_sessions", methods=["GET"])
def get_active_sessions():
    """Endpoint for admin to fetch all currently active sessions with their live webcam feeds."""
    if not g.admin:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            es.id as session_id,
            s.name as student_name,
            s.student_id as student_roll,
            es.started_at,
            es.expires_at,
            es.latest_frame,
            (SELECT COUNT(*) FROM violations WHERE session_id = es.id) as warning_count
        FROM exam_sessions es
        JOIN students s ON es.student_id = s.id
        WHERE es.is_submitted = 0;
    """)
    rows = cursor.fetchall()
    conn.close()
    
    sessions = [dict(row) for row in rows]
    return jsonify({"success": True, "sessions": sessions})

# ----------------- Submission & Results -----------------
@app.route("/submit_exam", methods=["POST"])
def submit_exam_action():
    """Manual submission handler."""
    if not g.student:
        return redirect(url_for("index"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM exam_sessions WHERE student_id = ? AND is_submitted = 0;",
        (g.student["id"],)
    )
    session_row = cursor.fetchone()
    conn.close()
    
    if session_row:
        submit_exam_processing(session_row["id"], g.student["id"])
        
    return redirect(url_for("results"))

def submit_exam_processing(session_id, student_id):
    """Processes grading, calculates result data, and commits to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure not submitted yet
    cursor.execute(
        "SELECT * FROM exam_sessions WHERE id = ? AND student_id = ? AND is_submitted = 0;",
        (session_id, student_id)
    )
    sess = cursor.fetchone()
    if not sess:
        conn.close()
        return
        
    now = datetime.now()
    submitted_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Set submitted state
    cursor.execute(
        "UPDATE exam_sessions SET is_submitted = 1, submitted_at = ? WHERE id = ?;",
        (submitted_at_str, session_id)
    )
    
    # Calculate Score
    # Fetch settings
    settings = get_settings()
    passing_marks = settings["passing_marks"]
    negative_marking = settings["negative_marking"]
    
    # Get all active questions in session order
    cursor.execute("SELECT question_id FROM exam_question_order WHERE session_id = ?;", (session_id,))
    questions_in_exam = [r["question_id"] for r in cursor.fetchall()]
    total_questions = len(questions_in_exam)
    
    # Get correct options for these questions
    cursor.execute(
        "SELECT question_id, id FROM options WHERE question_id IN ({}) AND is_correct = 1;".format(
            ",".join("?" * total_questions)
        ),
        questions_in_exam
    )
    correct_options = {r["question_id"]: r["id"] for r in cursor.fetchall()}
    
    # Get student answers
    cursor.execute(
        "SELECT question_id, selected_option_id FROM student_answers WHERE session_id = ?;",
        (session_id,)
    )
    student_selections = {r["question_id"]: r["selected_option_id"] for r in cursor.fetchall()}
    
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    
    for q_id in questions_in_exam:
        selected = student_selections.get(q_id)
        if selected is None:
            unanswered_count += 1
        elif selected == correct_options.get(q_id):
            correct_count += 1
        else:
            incorrect_count += 1
            
    # Calculate raw score (1 point per correct answer, subtract negative marks for incorrect answers)
    raw_score = correct_count * 1.0 - (incorrect_count * negative_marking)
    raw_score = max(0.0, raw_score) # Score cannot go below 0
    
    percentage = (raw_score / total_questions) * 100.0 if total_questions > 0 else 0.0
    pass_status = "Pass" if percentage >= passing_marks else "Fail"
    
    # Time taken
    started_at = datetime.strptime(sess["started_at"], "%Y-%m-%d %H:%M:%S")
    time_taken_seconds = int((now - started_at).total_seconds())
    
    # Insert results
    cursor.execute(
        """
        INSERT INTO results (
            session_id, student_id, score, percentage, correct_answers, 
            incorrect_answers, unanswered_questions, pass_status, time_taken_seconds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            score = excluded.score,
            percentage = excluded.percentage,
            correct_answers = excluded.correct_answers,
            incorrect_answers = excluded.incorrect_answers,
            unanswered_questions = excluded.unanswered_questions,
            pass_status = excluded.pass_status,
            time_taken_seconds = excluded.time_taken_seconds;
        """,
        (session_id, student_id, raw_score, percentage, correct_count, incorrect_count, unanswered_count, pass_status, time_taken_seconds)
    )
    
    conn.commit()
    conn.close()

@app.route("/results")
def results():
    """Displays the result scorecard for the current student."""
    if not g.student:
        return redirect(url_for("index"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load completed session and its score
    cursor.execute(
        """
        SELECT r.*, s.started_at, s.submitted_at 
        FROM results r
        JOIN exam_sessions s ON r.session_id = s.id
        WHERE r.student_id = ? AND s.is_submitted = 1
        ORDER BY s.submitted_at DESC LIMIT 1;
        """,
        (g.student["id"],)
    )
    result_row = cursor.fetchone()
    conn.close()
    
    if not result_row:
        # Check if they have an unsubmitted active exam
        return redirect(url_for("instructions"))
        
    # Convert time taken to MM:SS
    seconds = result_row["time_taken_seconds"]
    minutes = seconds // 60
    secs = seconds % 60
    time_taken_formatted = f"{minutes:02d}m {secs:02d}s"
    
    return render_template(
        "results.html",
        student=g.student,
        result=result_row,
        time_taken=time_taken_formatted
    )

# ----------------- Admin Routes -----------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin secure authentication portal."""
    if g.admin:
        return redirect(url_for("admin_dashboard"))
        
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Enforce access only to nithingowda@nxtwave.in
        if username != "nithingowda@nxtwave.in":
            error = "Access restricted. Please contact the admin."
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE username = ?;", (username,))
            admin = cursor.fetchone()
            conn.close()
            
            if admin and check_password_hash(admin["password_hash"], password):
                session.clear()
                session["admin_id"] = admin["id"]
                return redirect(url_for("admin_dashboard"))
            else:
                error = "Invalid Administrative Credentials."
            
    return render_template("admin_login.html", error=error)

@app.route("/admin")
@app.route("/admin/dashboard")
def admin_dashboard():
    """Administrative main landing dashboard."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate stats
    cursor.execute("SELECT COUNT(*) FROM students;")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exam_sessions WHERE is_submitted = 1;")
    exams_completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(percentage), AVG(score) FROM results;")
    avg_row = cursor.fetchone()
    avg_percentage = round(avg_row[0] or 0.0, 1)
    avg_score = round(avg_row[1] or 0.0, 1)
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE pass_status = 'Pass';")
    passed_exams = cursor.fetchone()[0]
    pass_rate = round((passed_exams / exams_completed * 100), 1) if exams_completed > 0 else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM violations;")
    total_violations = cursor.fetchone()[0]
    
    # Recent results
    cursor.execute(
        """
        SELECT r.*, s.name, s.student_id, es.submitted_at 
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN exam_sessions es ON r.session_id = es.id
        ORDER BY es.submitted_at DESC LIMIT 5;
        """
    )
    recent_results = cursor.fetchall()
    
    # High violation logs
    cursor.execute(
        """
        SELECT v.*, s.name, s.student_id, es.id as session_id 
        FROM violations v
        JOIN exam_sessions es ON v.session_id = es.id
        JOIN students s ON es.student_id = s.id
        ORDER BY v.timestamp DESC LIMIT 5;
        """
    )
    recent_violations = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        exams_completed=exams_completed,
        avg_percentage=avg_percentage,
        avg_score=avg_score,
        pass_rate=pass_rate,
        total_violations=total_violations,
        recent_results=recent_results,
        recent_violations=recent_violations
    )

@app.route("/admin/students", methods=["GET", "POST"])
def admin_students():
    """Allows managing and reviewing candidate details."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    error = None
    success = None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add":
            student_id = request.form.get("student_id", "").strip()
            name = request.form.get("name", "").strip()
            password = request.form.get("password", "")
            
            if not student_id or not name or not password:
                error = "All fields are required."
            else:
                cursor.execute("SELECT id FROM students WHERE student_id = ?;", (student_id,))
                if cursor.fetchone():
                    error = "Student ID already exists."
                else:
                    hashed_pw = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO students (student_id, name, password_hash) VALUES (?, ?, ?);",
                        (student_id, name, hashed_pw)
                    )
                    conn.commit()
                    success = f"Student {name} registered successfully."
                    
        elif action == "delete":
            target_id = request.form.get("student_db_id")
            if target_id:
                cursor.execute("DELETE FROM students WHERE id = ?;", (target_id,))
                conn.commit()
                success = "Student deleted successfully."
                
        elif action == "reallocate":
            target_id = request.form.get("student_db_id")
            if target_id:
                cursor.execute("DELETE FROM exam_sessions WHERE student_id = ?;", (target_id,))
                conn.commit()
                cursor.execute("SELECT name FROM students WHERE id = ?;", (target_id,))
                student = cursor.fetchone()
                s_name = student["name"] if student else "Student"
                success = f"Exam successfully re-allocated for {s_name}. All previous attempts and logs have been reset."
                
    # Search / list students
    search_query = request.args.get("search", "").strip()
    if search_query:
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE ? OR student_id LIKE ? ORDER BY name ASC;",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute("SELECT * FROM students ORDER BY name ASC;")
    students = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "admin_students.html",
        students=students,
        error=error,
        success=success,
        search_query=search_query
    )

@app.route("/admin/questions", methods=["GET", "POST"])
def admin_questions():
    """Allows viewing, editing, adding, and importing multiple-choice questions."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    error = None
    success = None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add":
            q_text = request.form.get("question_text", "").strip()
            category = request.form.get("category", "").strip()
            difficulty = request.form.get("difficulty", "Easy")
            
            opt1 = request.form.get("option_1", "").strip()
            opt2 = request.form.get("option_2", "").strip()
            opt3 = request.form.get("option_3", "").strip()
            opt4 = request.form.get("option_4", "").strip()
            correct_idx = int(request.form.get("correct_option", 1))
            
            if not q_text or not category or not opt1 or not opt2 or not opt3 or not opt4:
                error = "All question text and 4 options must be provided."
            else:
                cursor.execute(
                    "INSERT INTO questions (question_text, category, difficulty) VALUES (?, ?, ?);",
                    (q_text, category, difficulty)
                )
                q_id = cursor.lastrowid
                
                options = [opt1, opt2, opt3, opt4]
                for idx, opt_val in enumerate(options, 1):
                    cursor.execute(
                        "INSERT INTO options (question_id, option_text, is_correct) VALUES (?, ?, ?);",
                        (q_id, opt_val, 1 if idx == correct_idx else 0)
                    )
                conn.commit()
                success = "Question added successfully."
                
        elif action == "delete":
            q_id = request.form.get("question_id")
            if q_id:
                cursor.execute("DELETE FROM questions WHERE id = ?;", (q_id,))
                conn.commit()
                success = "Question deleted successfully."
                
        elif action == "import":
            # Bulk import from CSV
            csv_file = request.files.get("csv_file")
            if not csv_file or csv_file.filename == "":
                error = "Please select a valid CSV file."
            else:
                try:
                    stream = StringIO(csv_file.stream.read().decode("utf-8"), newline=None)
                    csv_reader = csv.reader(stream)
                    # Expected format: QuestionText,Category,Difficulty,Option1,Option2,Option3,Option4,CorrectOptionIndex(1-4)
                    header = next(csv_reader) # Skip header
                    imported_count = 0
                    
                    for row in csv_reader:
                        if len(row) < 8:
                            continue
                        q_t, cat, diff, o1, o2, o3, o4, corr_idx_str = [x.strip() for x in row[:8]]
                        corr_idx = int(corr_idx_str)
                        
                        cursor.execute(
                            "INSERT INTO questions (question_text, category, difficulty) VALUES (?, ?, ?);",
                            (q_t, cat, diff)
                        )
                        new_q_id = cursor.lastrowid
                        
                        opts = [o1, o2, o3, o4]
                        for idx, opt_v in enumerate(opts, 1):
                            cursor.execute(
                                "INSERT INTO options (question_id, option_text, is_correct) VALUES (?, ?, ?);",
                                (new_q_id, opt_v, 1 if idx == corr_idx else 0)
                            )
                        imported_count += 1
                        
                    conn.commit()
                    success = f"Successfully imported {imported_count} questions."
                except Exception as e:
                    error = f"Error reading CSV structure: {str(e)}"
                    
    # Read questions list
    search = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()
    
    query = """
        SELECT q.*, 
            MAX(CASE WHEN o.opt_num = 1 THEN o.option_text END) as option_1,
            MAX(CASE WHEN o.opt_num = 1 THEN o.is_correct END) as o1_correct,
            MAX(CASE WHEN o.opt_num = 2 THEN o.option_text END) as option_2,
            MAX(CASE WHEN o.opt_num = 2 THEN o.is_correct END) as o2_correct,
            MAX(CASE WHEN o.opt_num = 3 THEN o.option_text END) as option_3,
            MAX(CASE WHEN o.opt_num = 3 THEN o.is_correct END) as o3_correct,
            MAX(CASE WHEN o.opt_num = 4 THEN o.option_text END) as option_4,
            MAX(CASE WHEN o.opt_num = 4 THEN o.is_correct END) as o4_correct
        FROM questions q
        JOIN (
            SELECT question_id, option_text, is_correct,
                   ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY id) as opt_num
            FROM options
        ) o ON q.id = o.question_id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND q.question_text LIKE ?"
        params.append(f"%{search}%")
    if category_filter:
        query += " AND q.category = ?"
        params.append(category_filter)
    if difficulty_filter:
        query += " AND q.difficulty = ?"
        params.append(difficulty_filter)
        
    query += " GROUP BY q.id ORDER BY q.id DESC;"
    cursor.execute(query, params)
    questions = cursor.fetchall()
    
    # Get distinct categories for filtering list
    cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category ASC;")
    categories = [r["category"] for r in cursor.fetchall()]
    
    conn.close()
    
    return render_template(
        "admin_questions.html",
        questions=questions,
        categories=categories,
        error=error,
        success=success,
        search=search,
        selected_category=category_filter,
        selected_difficulty=difficulty_filter
    )

@app.route("/admin/logs")
def admin_logs():
    """Audit log visualizer showing cheating violations and exam completions."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search student logs
    search = request.args.get("search", "").strip()
    
    log_query = """
        SELECT v.*, s.name, s.student_id, es.started_at 
        FROM violations v
        JOIN exam_sessions es ON v.session_id = es.id
        JOIN students s ON es.student_id = s.id
        WHERE 1=1
    """
    params = []
    if search:
        log_query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    log_query += " ORDER BY v.timestamp DESC;"
    cursor.execute(log_query, params)
    violations = cursor.fetchall()
    
    # Active/Completed exam sessions
    session_query = """
        SELECT es.*, s.name, s.student_id, r.score, r.percentage, r.pass_status 
        FROM exam_sessions es
        JOIN students s ON es.student_id = s.id
        LEFT JOIN results r ON es.id = r.session_id
        WHERE 1=1
    """
    params_sess = []
    if search:
        session_query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
        params_sess.extend([f"%{search}%", f"%{search}%"])
    session_query += " ORDER BY es.started_at DESC;"
    cursor.execute(session_query, params_sess)
    sessions = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "admin_logs.html",
        violations=violations,
        sessions=sessions,
        search=search
    )

@app.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    """Configure exam parameters (passing mark, duration, negative grading)."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    success = None
    error = None
    
    if request.method == "POST":
        passing_marks = request.form.get("passing_marks", "").strip()
        negative_marking = request.form.get("negative_marking", "").strip()
        duration_minutes = request.form.get("duration_minutes", "").strip()
        total_questions = request.form.get("total_questions", "").strip()
        
        try:
            p_val = float(passing_marks)
            n_val = float(negative_marking)
            d_val = int(duration_minutes)
            q_val = int(total_questions)
            
            if p_val < 0 or p_val > 100 or n_val < 0 or n_val > 5 or d_val < 5 or q_val < 1:
                error = "Please provide logical positive constraint values."
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                settings_to_update = {
                    "passing_marks": str(p_val),
                    "negative_marking": str(n_val),
                    "duration_minutes": str(d_val),
                    "total_questions": str(q_val)
                }
                
                for key, val in settings_to_update.items():
                    cursor.execute(
                        "INSERT INTO exam_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value;",
                        (key, val)
                    )
                conn.commit()
                conn.close()
                success = "Exam settings updated successfully."
        except ValueError:
            error = "Invalid format: values must be numeric."
            
    settings = get_settings()
    return render_template("admin_settings.html", settings=settings, success=success, error=error)

@app.route("/admin/export")
def admin_export_results():
    """Export complete exam marks spreadsheet as a CSV download."""
    if not g.admin:
        return redirect(url_for("admin_login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.student_id, s.name, es.started_at, es.submitted_at, 
               r.score, r.percentage, r.correct_answers, r.incorrect_answers, 
               r.unanswered_questions, r.pass_status,
               (SELECT COUNT(*) FROM violations WHERE session_id = es.id) as total_violations
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN exam_sessions es ON r.session_id = es.id
        ORDER BY es.submitted_at DESC;
        """
    )
    records = cursor.fetchall()
    conn.close()
    
    # Generate CSV in memory
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow([
        "Student ID", "Candidate Name", "Started At", "Submitted At", 
        "Score Obtained", "Percentage (%)", "Correct", "Incorrect", 
        "Unanswered", "Pass/Fail Status", "Violations Recorded"
    ])
    
    for r in records:
        cw.writerow([
            r["student_id"], r["name"], r["started_at"], r["submitted_at"],
            r["score"], r["percentage"], r["correct_answers"], r["incorrect_answers"],
            r["unanswered_questions"], r["pass_status"], r["total_violations"]
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=html_exam_results_{}.csv".format(
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
