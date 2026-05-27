
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data" / "mock"
SCHEMA_SQL = BASE_DIR / "database" / "schema.sql"
DB_PATH    = BASE_DIR / "eduinsight.db"

def load_csvs():
    tables = ["departments","students","courses","semesters","enrollments","grades","attendance"]
    frames = {}
    for t in tables:
        path = DATA_DIR / f"{t}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing CSV: {path}. Run generate_mock_data.py first.")
        frames[t] = pd.read_csv(path)
        print(f"  📂 Loaded {t:<15} → {len(frames[t]):>6,} rows")
    return frames

def clean_students(df):
    df = df.dropna(subset=["student_id","roll_number","full_name","dept_id"])
    df["full_name"]  = df["full_name"].str.strip().str.title()
    df["email"]      = df["email"].str.strip().str.lower()
    df["gender"]     = df["gender"].fillna("Other")
    df["admission_year"] = df["admission_year"].astype(int)
    return df

def clean_grades(df):
    df = df.dropna(subset=["enrollment_id","internal_marks","external_marks"])
    df["internal_marks"] = df["internal_marks"].clip(0, 30).round(1)
    df["external_marks"] = df["external_marks"].clip(0, 70).round(1)
    return df

def clean_attendance(df):
    df = df.dropna(subset=["enrollment_id","total_classes","classes_attended"])
    df["total_classes"]    = df["total_classes"].astype(int).clip(lower=1)
    df["classes_attended"] = df["classes_attended"].astype(int).clip(lower=0)
    df["classes_attended"] = df.apply(
        lambda r: min(r["classes_attended"], r["total_classes"]), axis=1
    )
    return df

def clean_all(frames):
    frames["students"]   = clean_students(frames["students"])
    frames["grades"]     = clean_grades(frames["grades"])
    frames["attendance"] = clean_attendance(frames["attendance"])
    print("  ✓ Cleaning complete.")
    return frames


def init_db(conn):
    """Drop and re-create all tables using the schema.sql file."""
 
    drop_order = ["attendance","grades","enrollments","students","courses","semesters","departments"]
    drop_views  = ["v_semester_gpa","v_student_cgpa","v_attendance_summary"]
    cur = conn.cursor()
    for v in drop_views:
        cur.execute(f"DROP VIEW IF EXISTS {v}")
    for t in drop_order:
        cur.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()

    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    print("  ✓ Schema initialised (tables + views).")


def insert_frame(conn, df, table, cols):
    """Insert rows using executemany to respect generated columns."""
    placeholders = ", ".join(["?"] * len(cols))
    col_list     = ", ".join(cols)
    sql          = f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})"
    data         = [tuple(row) for row in df[cols].itertuples(index=False, name=None)]
    conn.executemany(sql, data)
    conn.commit()
    print(f"  ✓ Inserted {table:<15} → {len(data):>6,} rows")


def run_etl():
    print("\n🔄 EduInsight ETL Pipeline")
    print("=" * 40)

    print("\n[1/3] Ingesting CSVs …")
    frames = load_csvs()

    print("\n[2/3] Cleaning data …")
    frames = clean_all(frames)

    print("\n[3/3] Loading into SQLite …")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)

   
    insert_frame(conn, frames["departments"], "departments",
                 ["dept_id","dept_code","dept_name"])
    insert_frame(conn, frames["semesters"], "semesters",
                 ["semester_id","semester_num","academic_year","term","start_date","end_date"])
    insert_frame(conn, frames["courses"], "courses",
                 ["course_id","course_code","course_name","dept_id","credits","course_type"])
    insert_frame(conn, frames["students"], "students",
                 ["student_id","roll_number","full_name","dept_id","admission_year","gender","email"])
    insert_frame(conn, frames["enrollments"], "enrollments",
                 ["enrollment_id","student_id","course_id","semester_id"])
    
    insert_frame(conn, frames["grades"], "grades",
                 ["grade_id","enrollment_id","internal_marks","external_marks"])
    insert_frame(conn, frames["attendance"], "attendance",
                 ["attendance_id","enrollment_id","total_classes","classes_attended"])

    conn.close()
    
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    for tbl in ["departments","semesters","courses","students","enrollments","grades","attendance"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        count = cur.fetchone()[0]
        print(f"  • {tbl:<15}: {count:>6,} rows")

    cur.execute("SELECT grade_point, letter_grade, total_marks FROM grades LIMIT 1")
    row = cur.fetchone()
    print(f"\n  ✅ Generated cols sample → grade_point={row[0]}, letter={row[1]}, total={row[2]}")

    cur.execute("SELECT cgpa FROM v_student_cgpa LIMIT 1")
    cgpa = cur.fetchone()[0]
    print(f"  ✅ v_student_cgpa view   → cgpa sample = {cgpa}")

    conn.close()


if __name__ == "__main__":
    run_etl()
