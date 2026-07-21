-- Database Schema for HTML Online Examination System

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    father_name TEXT,
    father_contact TEXT,
    mother_name TEXT,
    mother_contact TEXT,
    alt_contact_name TEXT,
    alt_contact_number TEXT,
    utr_number TEXT,
    payment_time TEXT,
    payment_receipt_path TEXT
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy', 'Medium', 'Hard'))
);

-- Options table
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL CHECK(is_correct IN (0, 1)),
    FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Exam Sessions table
CREATE TABLE IF NOT EXISTS exam_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_submitted BOOLEAN DEFAULT 0 CHECK(is_submitted IN (0, 1)),
    submitted_at TIMESTAMP,
    random_seed INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Exam Question Order table
CREATE TABLE IF NOT EXISTS exam_question_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    display_order INTEGER NOT NULL,
    FOREIGN KEY(session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Exam Option Order table
CREATE TABLE IF NOT EXISTS exam_option_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    display_order INTEGER NOT NULL,
    FOREIGN KEY(session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY(option_id) REFERENCES options(id) ON DELETE CASCADE
);

-- Student Answers table
CREATE TABLE IF NOT EXISTS student_answers (
    session_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option_id INTEGER,
    marked_for_review BOOLEAN DEFAULT 0 CHECK(marked_for_review IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(session_id, question_id),
    FOREIGN KEY(session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY(selected_option_id) REFERENCES options(id) ON DELETE SET NULL
);

-- Results table
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER UNIQUE NOT NULL,
    student_id INTEGER NOT NULL,
    score REAL NOT NULL,
    percentage REAL NOT NULL,
    correct_answers INTEGER NOT NULL,
    incorrect_answers INTEGER NOT NULL,
    unanswered_questions INTEGER NOT NULL,
    pass_status TEXT NOT NULL CHECK(pass_status IN ('Pass', 'Fail')),
    time_taken_seconds INTEGER NOT NULL,
    FOREIGN KEY(session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Violations table
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    violation_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    warning_number INTEGER NOT NULL,
    FOREIGN KEY(session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE
);

-- Exam Settings table
CREATE TABLE IF NOT EXISTS exam_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
