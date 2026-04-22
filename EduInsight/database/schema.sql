
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    dept_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_code   TEXT NOT NULL UNIQUE,         
    dept_name   TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    student_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number     TEXT NOT NULL UNIQUE,     
    full_name       TEXT NOT NULL,
    dept_id         INTEGER NOT NULL REFERENCES departments(dept_id),
    admission_year  INTEGER NOT NULL,         
    gender          TEXT CHECK(gender IN ('Male','Female','Other')),
    email           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS semesters (
    semester_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_num    INTEGER NOT NULL,        
    academic_year   TEXT NOT NULL,             
    term            TEXT NOT NULL CHECK(term IN ('ODD','EVEN')),
    start_date      DATE,
    end_date        DATE,
    UNIQUE(semester_num, academic_year)
);

CREATE TABLE IF NOT EXISTS courses (
    course_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code     TEXT NOT NULL UNIQUE,      
    course_name     TEXT NOT NULL,
    dept_id         INTEGER NOT NULL REFERENCES departments(dept_id),
    credits         INTEGER NOT NULL DEFAULT 3 CHECK(credits BETWEEN 1 AND 5),
    course_type     TEXT CHECK(course_type IN ('Theory','Lab','Elective','Project'))
);

CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER NOT NULL REFERENCES students(student_id),
    course_id       INTEGER NOT NULL REFERENCES courses(course_id),
    semester_id     INTEGER NOT NULL REFERENCES semesters(semester_id),
    UNIQUE(student_id, course_id, semester_id)
);

-- ── Attendance ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id       INTEGER NOT NULL REFERENCES enrollments(enrollment_id),
    total_classes       INTEGER NOT NULL DEFAULT 0,
    classes_attended    INTEGER NOT NULL DEFAULT 0,
    attendance_pct      REAL GENERATED ALWAYS AS
                            (ROUND(CAST(classes_attended AS REAL) / total_classes * 100, 2))
                            STORED,
    UNIQUE(enrollment_id)
);

-- ── Grades ─────────────────────────────────────────────────────
-- Indian University Grading: 10-point scale
--   O (Outstanding) = 10  → 91–100
--   A+ (Excellent)  =  9  → 81–90
--   A  (Very Good)  =  8  → 71–80
--   B+ (Good)       =  7  → 61–70
--   B  (Above Avg)  =  6  → 51–60
--   C  (Average)    =  5  → 45–50
--   P  (Pass)       =  4  → 40–44
--   F  (Fail)       =  0  → 0–39
CREATE TABLE IF NOT EXISTS grades (
    grade_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id   INTEGER NOT NULL REFERENCES enrollments(enrollment_id),
    internal_marks  REAL NOT NULL DEFAULT 0 CHECK(internal_marks BETWEEN 0 AND 30),
    external_marks  REAL NOT NULL DEFAULT 0 CHECK(external_marks BETWEEN 0 AND 70),
    total_marks     REAL GENERATED ALWAYS AS (internal_marks + external_marks) STORED,
    grade_point     REAL GENERATED ALWAYS AS (
                        CASE
                            WHEN (internal_marks + external_marks) >= 91 THEN 10.0
                            WHEN (internal_marks + external_marks) >= 81 THEN 9.0
                            WHEN (internal_marks + external_marks) >= 71 THEN 8.0
                            WHEN (internal_marks + external_marks) >= 61 THEN 7.0
                            WHEN (internal_marks + external_marks) >= 51 THEN 6.0
                            WHEN (internal_marks + external_marks) >= 45 THEN 5.0
                            WHEN (internal_marks + external_marks) >= 40 THEN 4.0
                            ELSE 0.0
                        END
                    ) STORED,
    letter_grade    TEXT GENERATED ALWAYS AS (
                        CASE
                            WHEN (internal_marks + external_marks) >= 91 THEN 'O'
                            WHEN (internal_marks + external_marks) >= 81 THEN 'A+'
                            WHEN (internal_marks + external_marks) >= 71 THEN 'A'
                            WHEN (internal_marks + external_marks) >= 61 THEN 'B+'
                            WHEN (internal_marks + external_marks) >= 51 THEN 'B'
                            WHEN (internal_marks + external_marks) >= 45 THEN 'C'
                            WHEN (internal_marks + external_marks) >= 40 THEN 'P'
                            ELSE 'F'
                        END
                    ) STORED,
    UNIQUE(enrollment_id)
);

-- ============================================================
-- Useful Views
-- ============================================================

-- CGPA per student per semester (credits-weighted)
CREATE VIEW IF NOT EXISTS v_semester_gpa AS
SELECT
    e.student_id,
    e.semester_id,
    SUM(g.grade_point * c.credits) / SUM(c.credits)  AS sgpa,
    SUM(c.credits)                                     AS total_credits
FROM enrollments e
JOIN grades g ON g.enrollment_id = e.enrollment_id
JOIN courses c ON c.course_id    = e.course_id
GROUP BY e.student_id, e.semester_id;

-- Overall CGPA per student
CREATE VIEW IF NOT EXISTS v_student_cgpa AS
SELECT
    s.student_id,
    s.roll_number,
    s.full_name,
    d.dept_name,
    s.admission_year,
    ROUND(SUM(g.grade_point * c.credits) / SUM(c.credits), 2) AS cgpa
FROM students s
JOIN enrollments e  ON e.student_id   = s.student_id
JOIN grades g       ON g.enrollment_id = e.enrollment_id
JOIN courses c      ON c.course_id     = e.course_id
JOIN departments d  ON d.dept_id       = s.dept_id
GROUP BY s.student_id;

-- Attendance summary per student per semester
CREATE VIEW IF NOT EXISTS v_attendance_summary AS
SELECT
    e.student_id,
    e.semester_id,
    ROUND(AVG(a.attendance_pct), 2) AS avg_attendance_pct,
    MIN(a.attendance_pct)           AS min_subject_attendance
FROM enrollments e
JOIN attendance a ON a.enrollment_id = e.enrollment_id
GROUP BY e.student_id, e.semester_id;
