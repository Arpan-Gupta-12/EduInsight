
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import analysis_engine    as ae
import recommendation_engine as re_engine

BASE_DIR     = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="EduInsight API",
    description="Institutional Academic Performance & Strategy Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/summary", tags=["Overview"])
def institution_summary():
    """Institution-wide KPIs: avg CGPA, attendance, grade distribution, conclusions."""
    return ae.get_institution_summary()


@app.get("/api/departments", tags=["Departments"])
def department_summary():
    """Per-department breakdown with CGPA, attendance, pass/fail counts, and recommendations."""
    return ae.get_department_summary()


@app.get("/api/trends", tags=["Trends"])
def yoy_trends():
    """Year-on-Year semester SGPA and attendance trends per department."""
    return ae.get_yoy_trends()


@app.get("/api/subjects", tags=["Subjects"])
def subject_performance():
    """Subject-wise average marks, grade points, failure rates, and analysis."""
    return ae.get_subject_trends()


@app.get("/api/attendance-impact", tags=["Attendance"])
def attendance_impact():
    """Impact of attendance bands on grade point outcomes."""
    return ae.get_attendance_impact()


@app.get("/api/risk-summary", tags=["Risk"])
def risk_summary():
    """Count of critical, at-risk, and good-standing students."""
    return re_engine.get_risk_summary()


@app.get("/api/students/at-risk", tags=["Risk"])
def at_risk_students(limit: int = Query(default=100, le=500)):
    """List of at-risk students with SGPA history, risk level, and recommendations."""
    return re_engine.get_at_risk_students(limit=limit)



@app.get("/", include_in_schema=False)
def serve_root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/style.css", include_in_schema=False)
def serve_css():
    return FileResponse(str(FRONTEND_DIR / "style.css"), media_type="text/css")

@app.get("/app.js", include_in_schema=False)
def serve_js():
    return FileResponse(str(FRONTEND_DIR / "app.js"), media_type="application/javascript")

@app.get("/hero.png", include_in_schema=False)
def serve_hero():
    return FileResponse(str(FRONTEND_DIR / "hero.png"), media_type="image/png")

@app.get("/uni_logo.jpeg", include_in_schema=False)
def serve_uni_logo():
    return FileResponse(str(FRONTEND_DIR / "uni_logo.jpeg"), media_type="image/jpeg")

@app.get("/uni_logo.png", include_in_schema=False)
def serve_uni_logo_png():
    return FileResponse(str(FRONTEND_DIR / "uni_logo.png"), media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
