import random
import csv
import os
from pathlib import Path

random.seed(42)

BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data" / "mock"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NUM_STUDENTS = 500

DEPARTMENTS = [
    {"dept_id": 1, "dept_code": "CSE",  "dept_name": "Computer Science & Engineering"},
    {"dept_id": 2, "dept_code": "ECE",  "dept_name": "Electronics & Communication Engineering"},
    {"dept_id": 3, "dept_code": "ME",   "dept_name": "Mechanical Engineering"},
    {"dept_id": 4, "dept_code": "CIVIL","dept_name": "Civil Engineering"},
    {"dept_id": 5, "dept_code": "IT",   "dept_name": "Information Technology"},
]

SEMESTERS = [
    {"semester_id": 1, "semester_num": 1, "academic_year": "2022-23", "term": "ODD",  "start_date": "2022-07-15", "end_date": "2022-11-30"},
    {"semester_id": 2, "semester_num": 2, "academic_year": "2022-23", "term": "EVEN", "start_date": "2023-01-05", "end_date": "2023-05-20"},
    {"semester_id": 3, "semester_num": 3, "academic_year": "2023-24", "term": "ODD",  "start_date": "2023-07-15", "end_date": "2023-11-30"},
    {"semester_id": 4, "semester_num": 4, "academic_year": "2023-24", "term": "EVEN", "start_date": "2024-01-05", "end_date": "2024-05-20"},
]

COURSES = [
   
    {"course_id":  1, "course_code": "CS101", "course_name": "Programming Fundamentals",           "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id":  2, "course_code": "CS102", "course_name": "Digital Logic Design",               "dept_id": 1, "credits": 3, "course_type": "Theory"},
    {"course_id":  3, "course_code": "CS201", "course_name": "Data Structures & Algorithms",       "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id":  4, "course_code": "CS202", "course_name": "Computer Organisation",              "dept_id": 1, "credits": 3, "course_type": "Theory"},
    {"course_id":  5, "course_code": "CS301", "course_name": "Database Management Systems",        "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id":  6, "course_code": "CS302", "course_name": "Operating Systems",                  "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id":  7, "course_code": "CS401", "course_name": "Software Engineering",               "dept_id": 1, "credits": 3, "course_type": "Theory"},
    {"course_id":  8, "course_code": "CS402", "course_name": "Machine Learning",                   "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id":  9, "course_code": "CS103L","course_name": "Programming Lab",                    "dept_id": 1, "credits": 2, "course_type": "Lab"},
    {"course_id": 10, "course_code": "CS201L","course_name": "DSA Lab",                            "dept_id": 1, "credits": 2, "course_type": "Lab"},
  
    {"course_id": 11, "course_code": "EC101", "course_name": "Basic Electronics",                  "dept_id": 2, "credits": 3, "course_type": "Theory"},
    {"course_id": 12, "course_code": "EC201", "course_name": "Signals & Systems",                  "dept_id": 2, "credits": 4, "course_type": "Theory"},
    {"course_id": 13, "course_code": "EC301", "course_name": "VLSI Design",                        "dept_id": 2, "credits": 4, "course_type": "Theory"},
    {"course_id": 14, "course_code": "EC401", "course_name": "Digital Communication",              "dept_id": 2, "credits": 4, "course_type": "Theory"},
    {"course_id": 15, "course_code": "EC101L","course_name": "Electronics Lab",                    "dept_id": 2, "credits": 2, "course_type": "Lab"},
   
    {"course_id": 16, "course_code": "ME101", "course_name": "Engineering Mechanics",              "dept_id": 3, "credits": 4, "course_type": "Theory"},
    {"course_id": 17, "course_code": "ME201", "course_name": "Thermodynamics",                     "dept_id": 3, "credits": 4, "course_type": "Theory"},
    {"course_id": 18, "course_code": "ME301", "course_name": "Fluid Mechanics",                    "dept_id": 3, "credits": 4, "course_type": "Theory"},
    {"course_id": 19, "course_code": "ME401", "course_name": "Manufacturing Technology",           "dept_id": 3, "credits": 3, "course_type": "Theory"},
    {"course_id": 20, "course_code": "ME101L","course_name": "Workshop Lab",                       "dept_id": 3, "credits": 2, "course_type": "Lab"},
  
    {"course_id": 21, "course_code": "CV101", "course_name": "Engineering Drawing",                "dept_id": 4, "credits": 3, "course_type": "Theory"},
    {"course_id": 22, "course_code": "CV201", "course_name": "Structural Analysis",                "dept_id": 4, "credits": 4, "course_type": "Theory"},
    {"course_id": 23, "course_code": "CV301", "course_name": "Geo-technical Engineering",          "dept_id": 4, "credits": 3, "course_type": "Theory"},
    {"course_id": 24, "course_code": "CV401", "course_name": "Transportation Engineering",         "dept_id": 4, "credits": 3, "course_type": "Theory"},
    {"course_id": 25, "course_code": "CV101L","course_name": "Surveying Lab",                      "dept_id": 4, "credits": 2, "course_type": "Lab"},
  
    {"course_id": 26, "course_code": "IT101", "course_name": "Computer Networks",                  "dept_id": 5, "credits": 4, "course_type": "Theory"},
    {"course_id": 27, "course_code": "IT201", "course_name": "Web Technologies",                   "dept_id": 5, "credits": 3, "course_type": "Theory"},
    {"course_id": 28, "course_code": "IT301", "course_name": "Cloud Computing",                    "dept_id": 5, "credits": 3, "course_type": "Theory"},
    {"course_id": 29, "course_code": "IT401", "course_name": "Cyber Security",                     "dept_id": 5, "credits": 4, "course_type": "Theory"},
    {"course_id": 30, "course_code": "IT101L","course_name": "Networking Lab",                     "dept_id": 5, "credits": 2, "course_type": "Lab"},

    {"course_id": 31, "course_code": "MA101", "course_name": "Engineering Mathematics I",          "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id": 32, "course_code": "MA201", "course_name": "Engineering Mathematics II",         "dept_id": 1, "credits": 4, "course_type": "Theory"},
    {"course_id": 33, "course_code": "PH101", "course_name": "Engineering Physics",               "dept_id": 1, "credits": 3, "course_type": "Theory"},
    {"course_id": 34, "course_code": "EN101", "course_name": "Communication Skills",               "dept_id": 1, "credits": 2, "course_type": "Theory"},
]

DEPT_SEMESTER_COURSES = {
    1: { 
        1: [1,  2,  9,  31, 33, 34],
        2: [3,  4,  10, 32],
        3: [5,  6],
        4: [7,  8],
    },
    2: {  
        1: [11, 31, 33, 34, 15],
        2: [12, 32],
        3: [13],
        4: [14],
    },
    3: {  
        1: [16, 31, 33, 34, 20],
        2: [17, 32],
        3: [18],
        4: [19],
    },
    4: { 
        1: [21, 31, 33, 34, 25],
        2: [22, 32],
        3: [23],
        4: [24],
    },
    5: {  
        1: [26, 31, 33, 34, 30],
        2: [27, 32],
        3: [28],
        4: [29],
    },
}

FIRST_NAMES = [
    "Aarav","Aditya","Akash","Amit","Ananya","Anjali","Arjun","Aryan","Deepak","Deepika",
    "Divya","Gaurav","Harsha","Ishaan","Isha","Kabir","Kiran","Kritika","Kunal","Lakshmi",
    "Manish","Meera","Mohit","Neeraj","Neha","Nikhil","Nikita","Piyush","Pooja","Priya",
    "Rahul","Raj","Rajesh","Ravi","Riya","Rohit","Sachin","Sanjay","Shruti","Sneha",
    "Srishti","Suresh","Swati","Tanvi","Tarun","Uday","Vani","Vikas","Vikram","Vishal",
    "Yash","Zara","Aisha","Bhavya","Chetan","Dhruv","Ekta","Farhan","Garima","Hemant",
    "Ishita","Jai","Kavya","Lalit","Madhuri","Nidhi","Omkar","Pallavi","Parth","Renu",
    "Shivam","Tejas","Urvi","Varun","Waqar","Yadav","Yukta","Zaid","Abhinav","Bharat",
    "Chirag","Disha","Esha","Girish","Harsh","Indu","Jatin","Komal"
]

LAST_NAMES = [
    "Sharma","Verma","Singh","Kumar","Gupta","Patel","Mehta","Joshi","Mishra","Yadav",
    "Agarwal","Tiwari","Pandey","Srivastava","Rao","Nair","Reddy","Iyer","Pillai","Menon",
    "Khan","Ansari","Shaikh","Syed","Shah","Desai","Trivedi","Bhatt","Parekh","Modi",
    "Jain","Bansal","Goel","Kapoor","Chopra","Malhotra","Khanna","Bhatia","Sethi","Kohli"
]

GENDER_POOL = ["Male"] * 55 + ["Female"] * 43 + ["Other"] * 2


def weighted_gauss(mean, std, low=0, high=100):
    """Clipped Gaussian."""
    val = random.gauss(mean, std)
    return round(max(low, min(high, val)), 1)

def marks_for_profile(profile, sem_num):
    """
    Generate internal (0-30) and external (0-70) marks.
    profile: 'strong' | 'average' | 'weak'
    Slight degradation is added for later semesters for weak students.
    """
    decay = (sem_num - 1) * (3 if profile == "weak" else 0)
    if profile == "strong":
        internal = weighted_gauss(25,  3,  14, 30)
        external = weighted_gauss(55,  7,  35, 70)
    elif profile == "average":
        internal = weighted_gauss(19,  4,   8, 28)
        external = weighted_gauss(40, 10,  18, 63)
    else:  # weak
        internal = weighted_gauss(14,  5,   0, 24)
        external = weighted_gauss(28, 10,   0, 45)
    internal = max(0, min(30, internal - decay * 0.3))
    external = max(0, min(70, external - decay))
    return round(internal, 1), round(external, 1)

def attendance_for_profile(profile):
    if profile == "strong":
        return random.randint(80, 100), random.randint(75, 96)
    elif profile == "average":
        return random.randint(65, 95), random.randint(55, 88)
    else:
        return random.randint(40, 78), random.randint(35, 70)

def generate_students():
    students = []
    enrollment_id_counter = 1
    enrollments  = []
    attendance_rows = []
    grade_rows   = []

    profiles = (["strong"] * 200 + ["average"] * 200 + ["weak"] * 100)
    random.shuffle(profiles)

    students_per_dept = NUM_STUDENTS // len(DEPARTMENTS)  

    student_id = 1
    used_names = set()

    for dept in DEPARTMENTS:
        dept_id = dept["dept_id"]
        dept_code = dept["dept_code"]

        for i in range(students_per_dept):
            while True:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in used_names:
                    used_names.add(name)
                    break

            gender = random.choice(GENDER_POOL)
            roll   = f"{dept_code}2022{student_id:03d}"
            email  = f"{name.split()[0].lower()}.{student_id:03d}@university.edu.in"
            profile = profiles[student_id - 1]

            students.append({
                "student_id":     student_id,
                "roll_number":    roll,
                "full_name":      name,
                "dept_id":        dept_id,
                "admission_year": 2022,
                "gender":         gender,
                "email":          email,
                "profile":        profile,  
            })

            for sem in SEMESTERS:
                sem_id  = sem["semester_id"]
                sem_num = sem["semester_num"]
                course_ids = DEPT_SEMESTER_COURSES.get(dept_id, {}).get(sem_num, [])

                for c_id in course_ids:
                    enrollments.append({
                        "enrollment_id": enrollment_id_counter,
                        "student_id":    student_id,
                        "course_id":     c_id,
                        "semester_id":   sem_id,
                    })

                    internal, external = marks_for_profile(profile, sem_num)
                    grade_rows.append({
                        "grade_id":       enrollment_id_counter,
                        "enrollment_id":  enrollment_id_counter,
                        "internal_marks": internal,
                        "external_marks": external,
                    })

                    total, attended = attendance_for_profile(profile)
                    attended = min(attended, total)
                    attendance_rows.append({
                        "attendance_id":    enrollment_id_counter,
                        "enrollment_id":    enrollment_id_counter,
                        "total_classes":    total,
                        "classes_attended": attended,
                    })

                    enrollment_id_counter += 1

            student_id += 1

    return students, enrollments, grade_rows, attendance_rows


def write_csv(filename, rows, fieldnames):
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {filename:<35} ({len(rows):>6,} rows)")

def main():
    print("\n🎓 EduInsight Mock Data Generator")
    print("=" * 45)
    print("Generating data …\n")

    write_csv("departments.csv", DEPARTMENTS,
              ["dept_id","dept_code","dept_name"])
    write_csv("semesters.csv",   SEMESTERS,
              ["semester_id","semester_num","academic_year","term","start_date","end_date"])

    write_csv("courses.csv", COURSES,
              ["course_id","course_code","course_name","dept_id","credits","course_type"])

    students, enrollments, grades, attendance = generate_students()

    student_rows = [{k: v for k, v in s.items() if k != "profile"} for s in students]
    write_csv("students.csv",    student_rows,
              ["student_id","roll_number","full_name","dept_id","admission_year","gender","email"])
    write_csv("enrollments.csv", enrollments,
              ["enrollment_id","student_id","course_id","semester_id"])
    write_csv("grades.csv",      grades,
              ["grade_id","enrollment_id","internal_marks","external_marks"])
    write_csv("attendance.csv",  attendance,
              ["attendance_id","enrollment_id","total_classes","classes_attended"])

    print(f"\n✅ All files saved to: {DATA_DIR}")
    print("\nSummary:")
    print(f"  • Departments : {len(DEPARTMENTS)}")
    print(f"  • Students    : {len(student_rows)}")
    print(f"  • Courses     : {len(COURSES)}")
    print(f"  • Semesters   : {len(SEMESTERS)}")
    print(f"  • Enrollments : {len(enrollments)}")
    print(f"  • Grade rows  : {len(grades)}")
    print(f"  • Attendance  : {len(attendance)}")

if __name__ == "__main__":
    main()
