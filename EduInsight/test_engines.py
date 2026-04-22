import sys, json
sys.path.insert(0, 'scripts')
import analysis_engine as ae
import recommendation_engine as re_engine

print('--- SUMMARY ---')
s = ae.get_institution_summary()
print(f"total_students={s['total_students']}, avg_cgpa={s['avg_cgpa']}, avg_att={s['avg_attendance_pct']}")
print(f"conclusions: {s['analysis']['conclusion'][:1]}")

print('\n--- DEPARTMENTS ---')
d = ae.get_department_summary()
print(f"{len(d)} departments OK")
for dept in d:
    print(f"  {dept['dept_code']}: cgpa={dept['avg_cgpa']}, att={dept['avg_attendance']}")

print('\n--- YOY TRENDS ---')
t = ae.get_yoy_trends()
print(f"  {len(t['trends'])} trend rows, analysis: {t['analysis']['conclusion'][:1]}")

print('\n--- SUBJECTS ---')
subj = ae.get_subject_trends()
print(f"  {len(subj['subjects'])} subjects, top: {subj['top_performers'][0]['course_name']}")

print('\n--- ATTENDANCE IMPACT ---')
att = ae.get_attendance_impact()
print(f"  {len(att['bands'])} bands: {[b['attendance_band'] for b in att['bands']]}")

print('\n--- RISK SUMMARY ---')
r = re_engine.get_risk_summary()
print(json.dumps(r, indent=2))

print('\n--- AT RISK STUDENTS (top 5) ---')
students = re_engine.get_at_risk_students(limit=20)
for st in students[:5]:
    print(f"  [{st['risk_level']}] {st['full_name']} CGPA={st['cgpa']} Att={st['avg_attendance']}%")
    print(f"    Recs: {st['recommendations'][0]}")

print('\nALL ENGINE CHECKS PASSED')
