
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "eduinsight.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def get_institution_summary():
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT dept_id) FROM departments")
    total_depts = cur.fetchone()[0]

    cur.execute("""
        SELECT ROUND(AVG(cgpa),2) FROM v_student_cgpa
    """)
    avg_cgpa = cur.fetchone()[0]

    cur.execute("""
        SELECT ROUND(AVG(a.attendance_pct),2)
        FROM attendance a
    """)
    avg_attendance = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM v_student_cgpa WHERE cgpa < 5.0
    """)
    failing_students = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM v_attendance_summary
        WHERE avg_attendance_pct < 75
    """)
    low_attendance_count = cur.fetchone()[0]

    cur.execute("""
        SELECT letter_grade, COUNT(*) AS cnt
        FROM grades
        GROUP BY letter_grade
        ORDER BY grade_point DESC
    """)
    grade_dist = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "total_students":      total_students,
        "total_departments":   total_depts,
        "avg_cgpa":            avg_cgpa,
        "avg_attendance_pct":  avg_attendance,
        "failing_students":    failing_students,
        "low_attendance_count":low_attendance_count,
        "grade_distribution":  grade_dist,
        "analysis": _analyse_summary(avg_cgpa, avg_attendance, failing_students, total_students),
    }


def _analyse_summary(avg_cgpa, avg_att, failing, total):
    suggestions = []
    conclusion  = []

    if avg_cgpa >= 7.5:
        conclusion.append("Institution maintains a strong academic performance overall.")
    elif avg_cgpa >= 6.0:
        conclusion.append("Academic performance is moderate with room for improvement.")
    else:
        conclusion.append("Academic performance is below par; urgent intervention required.")

    if avg_att < 75:
        conclusion.append(f"Average attendance ({avg_att}%) is below the mandatory 75% threshold.")
        suggestions.append("Implement a strict attendance monitoring and early-warning notification system.")
    else:
        conclusion.append(f"Average attendance is healthy at {avg_att}%.")

    fail_pct = round(failing / total * 100, 1)
    if fail_pct > 10:
        conclusion.append(f"{fail_pct}% of students have CGPA below 5.0 – a critical concern.")
        suggestions.append("Launch remedial classes and personalised mentoring for at-risk students.")
    else:
        conclusion.append(f"Only {fail_pct}% students have CGPA below 5.0 – within acceptable limits.")

    suggestions += [
        "Introduce peer-learning programs to bridge the gap between top and bottom performers.",
        "Conduct faculty workshops focused on student-engagement improvement techniques.",
    ]
    return {"conclusion": conclusion, "suggestions": suggestions}



def get_department_summary():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            d.dept_name,
            d.dept_code,
            COUNT(DISTINCT s.student_id)                            AS total_students,
            ROUND(AVG(vc.cgpa), 2)                                  AS avg_cgpa,
            ROUND(AVG(va.avg_attendance_pct), 2)                    AS avg_attendance,
            SUM(CASE WHEN vc.cgpa >= 8.0 THEN 1 ELSE 0 END)        AS distinction_count,
            SUM(CASE WHEN vc.cgpa < 5.0  THEN 1 ELSE 0 END)        AS fail_count
        FROM departments d
        JOIN students s    ON s.dept_id   = d.dept_id
        JOIN v_student_cgpa vc ON vc.student_id = s.student_id
        JOIN v_attendance_summary va ON va.student_id = s.student_id
        GROUP BY d.dept_id
        ORDER BY avg_cgpa DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        r["analysis"] = _analyse_dept(r)
    return rows


def _analyse_dept(dept):
    suggestions = []
    conclusion  = []
    n = dept["total_students"]

    dist_pct = round(dept["distinction_count"] / n * 100, 1)
    fail_pct = round(dept["fail_count"]        / n * 100, 1)

    if dept["avg_cgpa"] >= 7.5:
        conclusion.append(f"{dept['dept_name']} is a top-performing department (avg CGPA {dept['avg_cgpa']}).")
    elif dept["avg_cgpa"] >= 6.0:
        conclusion.append(f"{dept['dept_name']} shows average performance (avg CGPA {dept['avg_cgpa']}).")
    else:
        conclusion.append(f"{dept['dept_name']} needs immediate attention (avg CGPA {dept['avg_cgpa']}).")
        suggestions.append("Review curriculum relevance and teaching methodology.")

    if dist_pct > 20:
        conclusion.append(f"{dist_pct}% students achieved distinction – excellent results.")
    if fail_pct > 10:
        conclusion.append(f"{fail_pct}% students are failing – intervention is critical.")
        suggestions.append("Conduct bi-weekly departmental review meetings with faculty.")

    if dept["avg_attendance"] < 75:
        suggestions.append("Introduce weekly attendance reports sent directly to parents/guardians.")

    return {"conclusion": conclusion, "suggestions": suggestions}



def get_yoy_trends():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            sm.academic_year,
            sm.semester_num,
            sm.term,
            d.dept_code,
            d.dept_name,
            ROUND(AVG(vg.sgpa),2)              AS avg_sgpa,
            ROUND(AVG(va.avg_attendance_pct),2) AS avg_attendance
        FROM semesters sm
        JOIN enrollments e   ON e.semester_id = sm.semester_id
        JOIN students s      ON s.student_id  = e.student_id
        JOIN departments d   ON d.dept_id     = s.dept_id
        JOIN v_semester_gpa vg ON vg.student_id = e.student_id AND vg.semester_id = e.semester_id
        JOIN v_attendance_summary va ON va.student_id = e.student_id AND va.semester_id = e.semester_id
        GROUP BY sm.semester_id, d.dept_id
        ORDER BY sm.semester_num, d.dept_code
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    analysis = _analyse_trends(rows)
    return {"trends": rows, "analysis": analysis}


def _analyse_trends(rows):
  
    from collections import defaultdict
    dept_trends = defaultdict(list)
    for r in rows:
        dept_trends[r["dept_code"]].append(r["avg_sgpa"])

    conclusion  = []
    suggestions = []
    for dept, sgpas in dept_trends.items():
        if len(sgpas) < 2:
            continue
        if sgpas[-1] > sgpas[0]:
            conclusion.append(f"{dept}: SGPA improved from {sgpas[0]} → {sgpas[-1]} over semesters.")
        else:
            diff = round(sgpas[0] - sgpas[-1], 2)
            conclusion.append(f"{dept}: SGPA declined by {diff} points – needs attention.")
            suggestions.append(f"Investigate curriculum progression difficulty in {dept}.")

    suggestions += [
        "Align course difficulty curves with student learning pace semester-on-semester.",
        "Use semester-transition workshops to prepare students for upcoming subjects.",
    ]
    return {"conclusion": conclusion, "suggestions": suggestions}


def get_subject_trends():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            c.course_code,
            c.course_name,
            c.course_type,
            d.dept_name,
            c.credits,
            ROUND(AVG(g.total_marks),2)      AS avg_marks,
            ROUND(AVG(g.grade_point),2)      AS avg_grade_point,
            SUM(CASE WHEN g.grade_point = 0 THEN 1 ELSE 0 END) AS fail_count,
            COUNT(g.grade_id)                AS attempted
        FROM grades g
        JOIN enrollments e ON e.enrollment_id = g.enrollment_id
        JOIN courses c     ON c.course_id     = e.course_id
        JOIN departments d ON d.dept_id       = c.dept_id
        GROUP BY c.course_id
        ORDER BY avg_grade_point DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        r["fail_pct"] = round(r["fail_count"] / r["attempted"] * 100, 1) if r["attempted"] else 0
        r["analysis"] = _analyse_subject(r)

    top3    = sorted(rows, key=lambda x: x["avg_grade_point"], reverse=True)[:3]
    bottom3 = sorted(rows, key=lambda x: x["avg_grade_point"])[:3]
    return {"subjects": rows, "top_performers": top3, "needs_attention": bottom3}


def _analyse_subject(s):
    conclusion  = []
    suggestions = []
    if s["avg_grade_point"] >= 8.0:
        conclusion.append(f"Strong performance in {s['course_name']} (avg GP {s['avg_grade_point']}).")
    elif s["avg_grade_point"] >= 6.0:
        conclusion.append(f"Moderate performance in {s['course_name']} (avg GP {s['avg_grade_point']}).")
    else:
        conclusion.append(f"{s['course_name']} is a high-failure subject (avg GP {s['avg_grade_point']}).")
        suggestions.append(f"Add supplementary tutorials and extra practice sessions for {s['course_name']}.")

    if s["fail_pct"] > 15:
        suggestions.append(f"Revise the examination pattern or internal evaluation for {s['course_name']}.")
    return {"conclusion": conclusion, "suggestions": suggestions}

def get_attendance_impact():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            CASE
                WHEN a.attendance_pct >= 90 THEN '90–100%'
                WHEN a.attendance_pct >= 75 THEN '75–89%'
                WHEN a.attendance_pct >= 60 THEN '60–74%'
                ELSE 'Below 60%'
            END                              AS attendance_band,
            ROUND(AVG(g.grade_point),2)      AS avg_grade_point,
            ROUND(AVG(g.total_marks),2)      AS avg_marks,
            COUNT(*)                         AS count
        FROM attendance a
        JOIN grades g ON g.enrollment_id = a.enrollment_id
        GROUP BY attendance_band
        ORDER BY avg_grade_point DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {
        "bands":    rows,
        "analysis": _analyse_attendance_impact(rows),
    }


def _analyse_attendance_impact(rows):
    conclusion  = []
    suggestions = []
    if len(rows) >= 2:
        top = rows[0]
        bot = rows[-1]
        gap = round(top["avg_grade_point"] - bot["avg_grade_point"], 2)
        conclusion.append(
            f"Students with {top['attendance_band']} attendance score avg GP {top['avg_grade_point']} "
            f"vs {bot['avg_grade_point']} for {bot['attendance_band']} — a gap of {gap} points."
        )
        if gap > 1.5:
            conclusion.append("Attendance has a HIGH IMPACT on academic outcomes.")
            suggestions.append("Make attendance tracking real-time via RFID/biometric integration.")
            suggestions.append("Send automated SMS/email alerts to students when attendance drops below 80%.")
        else:
            conclusion.append("Attendance impact on grades is moderate.")
    suggestions.append("Introduce attendance-linked scholarship incentives to boost participation.")
    return {"conclusion": conclusion, "suggestions": suggestions}


if __name__ == "__main__":
    import json

    print("\n📊 EduInsight Analysis Engine")
    print("=" * 40)

    print("\n[1] Institution Summary")
    print(json.dumps(get_institution_summary(), indent=2))

    print("\n[2] Department Breakdown")
    print(json.dumps(get_department_summary(), indent=2))

    print("\n[3] Year-on-Year Trends")
    print(json.dumps(get_yoy_trends(), indent=2))

    print("\n[4] Subject Performance")
    data = get_subject_trends()
    print(f"  Top 3 subjects    : {[s['course_name'] for s in data['top_performers']]}")
    print(f"  Needs attention   : {[s['course_name'] for s in data['needs_attention']]}")

    print("\n[5] Attendance Impact")
    print(json.dumps(get_attendance_impact(), indent=2))
