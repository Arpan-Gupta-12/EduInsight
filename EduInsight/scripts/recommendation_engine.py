
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "eduinsight.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _bfs_peer_mentor_matcher(cur, student_id, failing_subjects):
   
    if not failing_subjects:
        return None
        
    from collections import deque
    
    cur.execute("SELECT student_id, course_id FROM enrollments")
    enrollments_data = cur.fetchall()
    
    student_to_courses = {}
    course_to_students = {}
    for r in enrollments_data:
        sid, cid = r[0], r[1]
        student_to_courses.setdefault(sid, set()).add(cid)
        course_to_students.setdefault(cid, set()).add(sid)
        
    def get_neighbors(sid):
        neighbors = set()
        for cid in student_to_courses.get(sid, []):
            neighbors.update(course_to_students.get(cid, []))
        neighbors.discard(sid)
        return neighbors

    target_course_id = failing_subjects[0]['course_id']
    target_course_name = failing_subjects[0]['course_name']
    
    cur.execute( (target_course_id,))
    
    valid_mentors = {r[0]: {"name": r[1], "marks": r[2]} for r in cur.fetchall()}
    
    if not valid_mentors:
        return None

    queue = deque([(student_id, 0)])
    visited = {student_id}
    
    while queue:
        curr, dist = queue.popleft()
        
        if curr in valid_mentors and curr != student_id:
            return {
                "mentor_name": valid_mentors[curr]["name"],
                "marks_in_subject": valid_mentors[curr]["marks"],
                "subject": target_course_name,
                "network_distance": dist
            }
            
        if dist >= 3: 
            continue
            
        for neighbor in get_neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
                
    return None


def _risk_label(cgpa, attendance, cgpa_trend):
    
    if cgpa < 5.0 or attendance < 60:
        return "critical"
    elif cgpa < 6.5 or attendance < 75 or cgpa_trend < -0.5:
        return "at_risk"
    return "good"


def _build_recommendations(student, cgpa_trend, low_subjects):
    recs = []
    att  = student["avg_attendance"]

    if att < 60:
        recs.append("🚨 Attendance critically low – immediate counselling and parental notification required.")
    elif att < 75:
        recs.append("⚠️ Attendance below 75% threshold – student may be barred from exams. Escalate to department HOD.")

    if student["cgpa"] < 5.0:
        recs.append("📉 CGPA below 5.0 – enrol student in remedial/supplementary coaching immediately.")
    elif student["cgpa"] < 6.5:
        recs.append("📊 CGPA borderline – assign a faculty mentor for regular academic check-ins.")

    if cgpa_trend < -0.5:
        recs.append(f"📉 SGPA declining trend detected (Δ = {round(cgpa_trend,2)}) – investigate root cause (personal/academic).")

    for subj in low_subjects:
        recs.append(f"📚 Weak in '{subj}' – suggest targeted practice tests and tutorial sessions.")

    if not recs:
        recs.append("✅ Student is in good standing. Continue monitoring.")

    return recs


def get_at_risk_students(limit=200):
    conn = get_conn()
    cur  = conn.cursor()

   
    cur.execute("""
        SELECT
            s.student_id,
            s.roll_number,
            s.full_name,
            d.dept_name,
            d.dept_code,
            s.admission_year,
            vc.cgpa,
            ROUND(va.avg_attendance_pct,2) AS avg_attendance
        FROM students s
        JOIN departments d          ON d.dept_id    = s.dept_id
        JOIN v_student_cgpa vc      ON vc.student_id = s.student_id
        JOIN (
            SELECT student_id, ROUND(AVG(avg_attendance_pct),2) AS avg_attendance_pct
            FROM v_attendance_summary GROUP BY student_id
        ) va ON va.student_id = s.student_id
        ORDER BY vc.cgpa ASC
        LIMIT ?
    """, (limit,))
    base_list = [dict(r) for r in cur.fetchall()]

    results = []
    for student in base_list:
        sid = student["student_id"]

        cur.execute("""
            SELECT sgpa FROM v_semester_gpa
            WHERE student_id = ? ORDER BY semester_id
        """, (sid,))
        sgpas = [r[0] for r in cur.fetchall()]

        if len(sgpas) >= 2:
            cgpa_trend = sgpas[-1] - sgpas[0]
        else:
            cgpa_trend = 0.0

        cur.execute("""
            SELECT c.course_id, c.course_name
            FROM grades g
            JOIN enrollments e ON e.enrollment_id = g.enrollment_id
            JOIN courses c     ON c.course_id     = e.course_id
            WHERE e.student_id = ? AND g.grade_point < 5
        """, (sid,))
        
        failing_subjects = [{"course_id": r[0], "course_name": r[1]} for r in cur.fetchall()]
        low_subjects = [s["course_name"] for s in failing_subjects[:3]]
        bfs_mentor = _bfs_peer_mentor_matcher(cur, sid, failing_subjects)

        risk = _risk_label(student["cgpa"], student["avg_attendance"], cgpa_trend)
        recs = _build_recommendations(student, cgpa_trend, low_subjects)

        results.append({
            **student,
            "sgpa_history":    sgpas,
            "cgpa_trend":      round(cgpa_trend, 2),
            "risk_level":      risk,
            "low_subjects":    low_subjects,
            "recommendations": recs,
            "bfs_mentor":      bfs_mentor,
        })

    conn.close()

    flagged = [r for r in results if r["risk_level"] in ("critical","at_risk")]
    flagged.sort(key=lambda x: (0 if x["risk_level"]=="critical" else 1, x["cgpa"]))
    return flagged


def get_risk_summary():
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM v_student_cgpa WHERE cgpa < 5.0")
    critical = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT student_id) FROM v_attendance_summary
        WHERE avg_attendance_pct < 75
    """)
    low_att = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM v_student_cgpa
        WHERE cgpa >= 5.0 AND cgpa < 6.5
    """)
    borderline = cur.fetchone()[0]

    conn.close()
    return {
        "total_students":     total,
        "critical_students":  critical,
        "low_attendance":     low_att,
        "borderline_students":borderline,
        "good_standing":      total - critical - borderline,
    }


if __name__ == "__main__":
    import json
    print("\n⚠️  EduInsight Recommendation Engine")
    print("=" * 40)
    summary = get_risk_summary()
    print(json.dumps(summary, indent=2))
    students = get_at_risk_students(50)
    print(f"\nFlagged {len(students)} at-risk students (showing first 3):")
    for s in students[:3]:
        print(f"\n  [{s['risk_level'].upper()}] {s['full_name']} ({s['roll_number']})")
        print(f"    CGPA: {s['cgpa']}  Attendance: {s['avg_attendance']}%")
        for r in s["recommendations"]:
            print(f"    → {r}")
