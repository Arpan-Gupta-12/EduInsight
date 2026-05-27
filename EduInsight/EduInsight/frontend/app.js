


const API = window.location.origin + "/api";
let currentRole = "admin";
let allRiskStudents = [];
let charts = {};

Chart.defaults.color = "#6b5c46";
Chart.defaults.borderColor = "rgba(44,24,16,0.1)";
Chart.defaults.font.family = "'Inter', sans-serif";

const C = {
  primary:  "#8B2500",    
  accent:   "#b08d2b",    
  success:  "#2d6a4f",    
  danger:   "#8B2500",    
  warning:  "#b08d2b",    
  info:     "#1d4e6b",     
  purple:   "#6b3a5c",  
  pink:     "#a05060",    
  palette:  ["#8B2500","#b08d2b","#2d6a4f","#1d4e6b","#6b3a5c","#a05060","#7a5c30","#4a5e6b"],
};

const $  = (id) => document.getElementById(id);
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls)  e.className   = cls;
  if (html) e.innerHTML   = html;
  return e;
};

async function apiFetch(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`API ${path} → ${r.status}`);
  return r.json();
}

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const main    = $("main-content");
  if (window.innerWidth <= 900) {
    sidebar.classList.toggle("mobile-open");
  } else {
    sidebar.classList.toggle("collapsed");
    main.classList.toggle("expanded");
  }
}

const tabMeta = {
  overview:        { title: "Dashboard Overview",       sub: "Institution-wide academic performance at a glance" },
  departments:     { title: "Department Analysis",      sub: "Per-department CGPA, attendance, and performance metrics" },
  trends:          { title: "Year-on-Year Trends",      sub: "Semester-wise SGPA and attendance trajectories" },
  subjects:        { title: "Subject Performance",      sub: "Course-level analysis, failure rates, and insights" },
  attendance:      { title: "Attendance Impact",        sub: "How attendance affects academic outcomes" },
  atrisk:          { title: "At-Risk Students",         sub: "Students flagged for immediate faculty intervention" },
  monitor:         { title: "Student Monitor",          sub: "Full student directory — search, filter, and track all 500 students" },
  recommendations: { title: "Recommendations",          sub: "Data-driven strategies for faculty and management" },
};



function switchRole(role) {
  currentRole = role;
  document.querySelectorAll(".role-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.role === role);
  });
  applyRoleFilter(role);
}

function applyRoleFilter(role) {

  const manOnly = ["atrisk"];
  if (role === "faculty") {
    document.querySelector("[data-tab='atrisk']").style.display = "";
  } else {
    document.querySelector("[data-tab='atrisk']").style.display = "";
  }
}

function openModal(html) {
  $("modal-body").innerHTML = html;
  $("modal-overlay").classList.add("open");
}
function closeModal() {
  $("modal-overlay").classList.remove("open");
}

async function loadOverview() {
  const [summary, risk] = await Promise.all([
    apiFetch("/summary"),
    apiFetch("/risk-summary"),
  ]);

  const kpis = [
    { icon:"🎓", val: summary.total_students,     label:"Total Students",    color:"#8B2500" },
    { icon:"🏛️", val: summary.total_departments,  label:"Departments",       color:"#b08d2b" },
    { icon:"📊", val: summary.avg_cgpa,            label:"Avg CGPA / 10",    color:"#2d6a4f" },
    { icon:"🗓️", val: summary.avg_attendance_pct + "%", label:"Avg Attendance", color:"#1d4e6b" },
    { icon:"🔴", val: risk.critical_students,      label:"Critical Students", color:"#8B2500" },
    { icon:"🟡", val: risk.borderline_students,    label:"At-Risk Students",  color:"#b08d2b" },
    { icon:"🟢", val: risk.good_standing,          label:"Good Standing",     color:"#2d6a4f" },
    { icon:"📉", val: summary.low_attendance_count,label:"Low Attendance",    color:"#7a5c30" },
  ];
  const grid = $("kpi-grid");
  grid.innerHTML = "";
  kpis.forEach(k => {
    const card = el("div", "kpi-card");
    card.style.setProperty("--kpi-color", k.color);
    card.innerHTML = `
      <div class="kpi-icon">${k.icon}</div>
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-label">${k.label}</div>`;
    grid.appendChild(card);
  });

  const gd    = summary.grade_distribution;
  const order = ["O","A+","A","B+","B","C","P","F"];
  const labels = order.filter(g => gd.find(x => x.letter_grade === g));
  const vals   = labels.map(g => (gd.find(x => x.letter_grade === g) || {}).cnt || 0);
  const colors = labels.map(g => ({
    O:"#2d6a4f","A+":"#3a8a62",A:"#1d4e6b",
    "B+":"#4a6e8b",B:"#b08d2b",C:"#a05060",P:"#7a5c30",F:"#8B2500"
  }[g] || "#888"));

  destroyChart("gradeDistChart");
  charts.gradeDistChart = new Chart($("gradeDistChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{ data: vals, backgroundColor: colors, borderRadius: 6, borderSkipped: false }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false }, tooltip: { callbacks: {
        label: ctx => ` ${ctx.parsed.y.toLocaleString()} students`
      }}},
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: "rgba(44,24,16,0.07)" }, beginAtZero: true },
      },
    },
  });

  destroyChart("riskDonutChart");
  charts.riskDonutChart = new Chart($("riskDonutChart"), {
    type: "doughnut",
    data: {
      labels: ["Critical","At-Risk","Good Standing"],
      datasets: [{
        data: [risk.critical_students, risk.borderline_students, risk.good_standing],
        backgroundColor: ["#8B2500","#b08d2b","#2d6a4f"],
        borderWidth: 0, hoverOffset: 8,
      }],
    },
    options: {
      responsive: true, cutout: "70%",
      plugins: {
        legend: { position: "bottom", labels: { padding: 16, font: { size: 12 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed} students` }},
      },
    },
  });

  const analysis = summary.analysis;
  renderInsight("overview-insight-body", analysis.conclusion, analysis.suggestions);
}

async function loadDepartments() {
  const depts = await apiFetch("/departments");

  destroyChart("deptCgpaChart");
  charts.deptCgpaChart = new Chart($("deptCgpaChart"), {
    type: "bar",
    data: {
      labels: depts.map(d => d.dept_code),
      datasets: [
        {
          label: "Avg CGPA",
          data: depts.map(d => d.avg_cgpa),
          backgroundColor: C.palette.slice(0,5),
          borderRadius: 8, borderSkipped: false,
          barThickness: 40,
        },
      ],
    },
    options: {
      responsive: true, indexAxis: "x",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` CGPA: ${ctx.parsed.y}/10` }},
      },
      scales: {
        x: { grid: { display: false } },
        y: { min: 0, max: 10, grid: { color: "rgba(44,24,16,0.07)" } },
      },
    },
  });

  destroyChart("deptPassFailChart");
  charts.deptPassFailChart = new Chart($("deptPassFailChart"), {
    type: "bar",
    data: {
      labels: depts.map(d => d.dept_code),
      datasets: [
        { label:"Distinction (≥8)",    data: depts.map(d => d.distinction_count), backgroundColor: C.success, borderRadius: 6 },
        { label:"Failing (<5 CGPA)",   data: depts.map(d => d.fail_count),         backgroundColor: C.danger,  borderRadius: 6 },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position:"bottom" } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: "rgba(44,24,16,0.07)" }, beginAtZero: true },
      },
    },
  });

  const grid = $("dept-cards-grid");
  grid.innerHTML = "";
  depts.forEach((d, i) => {
    const cgpaStatus = d.avg_cgpa >= 7.5 ? "green" : d.avg_cgpa >= 6 ? "yellow" : "red";
    const cgpaLabel  = d.avg_cgpa >= 7.5 ? "High Performer" : d.avg_cgpa >= 6 ? "Average" : "Needs Attention";
    const attPct     = d.avg_attendance;
    const failPct    = ((d.fail_count / d.total_students) * 100).toFixed(1);
    const distPct    = ((d.distinction_count / d.total_students)*100).toFixed(1);
    const color      = C.palette[i % C.palette.length];

    const card = el("div","dept-card");
    card.innerHTML = `
      <div class="dept-card-header">
        <div class="dept-card-name">${d.dept_code} – ${d.dept_name.split("&")[0].trim()}</div>
        <div class="dept-badge ${cgpaStatus}">${cgpaLabel}</div>
      </div>
      <div class="dept-stats">
        <div class="dept-stat"><div class="dept-stat-val" style="color:${color}">${d.avg_cgpa}</div><div class="dept-stat-lbl">Avg CGPA</div></div>
        <div class="dept-stat"><div class="dept-stat-val" style="color:${C.info}">${attPct}%</div><div class="dept-stat-lbl">Attendance</div></div>
        <div class="dept-stat"><div class="dept-stat-val" style="color:${C.success}">${d.distinction_count}</div><div class="dept-stat-lbl">Distinction</div></div>
        <div class="dept-stat"><div class="dept-stat-val" style="color:${C.danger}">${d.fail_count}</div><div class="dept-stat-lbl">Failing</div></div>
      </div>
      <div class="dept-bar-wrap">
        <div class="dept-bar-label"><span>CGPA Progress</span><span>${d.avg_cgpa}/10</span></div>
        <div class="dept-bar"><div class="dept-bar-fill" style="width:${d.avg_cgpa*10}%;background:${color}"></div></div>
      </div>
      <div class="dept-bar-wrap">
        <div class="dept-bar-label"><span>Attendance</span><span>${attPct}%</span></div>
        <div class="dept-bar"><div class="dept-bar-fill" style="width:${attPct}%;background:${C.info}"></div></div>
      </div>
      <div class="dept-analysis">
        <div class="dept-conclusion">${(d.analysis.conclusion || []).map(c=>`<p>• ${c}</p>`).join("")}</div>
        ${(d.analysis.suggestions||[]).map(s=>`<div class="dept-suggestion">${s}</div>`).join("")}
      </div>`;
    grid.appendChild(card);
  });
}

async function loadTrends() {
  const data = await apiFetch("/trends");
  const trends = data.trends;

  const depts = [...new Set(trends.map(t => t.dept_code))];
  const sems   = [...new Set(trends.map(t => `Sem ${t.semester_num}\n${t.academic_year}`))];

  destroyChart("trendLineChart");
  charts.trendLineChart = new Chart($("trendLineChart"), {
    type: "line",
    data: {
      labels: sems,
      datasets: depts.map((dept, i) => {
        const pts = trends.filter(t => t.dept_code === dept);
        return {
          label: dept,
          data: pts.map(t => t.avg_sgpa),
          borderColor: C.palette[i],
          backgroundColor: C.palette[i]+"33",
          tension: 0.4, fill: false, pointRadius: 5, pointHoverRadius: 8,
        };
      }),
    },
    options: {
      responsive: true,
      plugins: { legend: { position:"bottom" }, tooltip: { mode:"index" } },
      scales: {
        x: { grid: { color:"rgba(44,24,16,0.07)" } },
        y: { min: 4, max: 10, grid: { color:"rgba(44,24,16,0.07)" },
             title: { display:true, text:"SGPA (out of 10)" } },
      },
    },
  });

  destroyChart("attTrendChart");
  charts.attTrendChart = new Chart($("attTrendChart"), {
    type: "line",
    data: {
      labels: sems,
      datasets: depts.map((dept, i) => {
        const pts = trends.filter(t => t.dept_code === dept);
        return {
          label: dept,
          data: pts.map(t => t.avg_attendance),
          borderColor: C.palette[i],
          backgroundColor: C.palette[i]+"22",
          tension: 0.4, fill: true, borderDash: [4,3],
          pointRadius: 4,
        };
      }),
    },
    options: {
      responsive: true,
      plugins: { legend: { position:"bottom" } },
      scales: {
        x: { grid: { color:"rgba(44,24,16,0.07)" } },
        y: { min:50, max:100, grid:{ color:"rgba(44,24,16,0.07)" },
             title: { display:true, text:"Attendance %" } },
      },
    },
  });

  renderInsight("trend-insight-body", data.analysis.conclusion, data.analysis.suggestions);
}
async function loadSubjects() {
  const data = await apiFetch("/subjects");
  const subs  = data.subjects;

  destroyChart("subjectBarChart");
  charts.subjectBarChart = new Chart($("subjectBarChart"), {
    type: "bar",
    data: {
      labels: subs.map(s => s.course_code),
      datasets: [{
        label: "Avg Grade Point",
        data: subs.map(s => s.avg_grade_point),
        backgroundColor: subs.map(s => s.avg_grade_point >= 7 ? C.success+"bb" : s.avg_grade_point >= 5 ? C.primary+"bb" : C.danger+"bb"),
        borderRadius: 6, borderSkipped: false,
      }],
    },
    options: {
      responsive: true, indexAxis: "x",
      plugins: { legend:{display:false}, tooltip:{ callbacks:{
        label: ctx => ` GP: ${ctx.parsed.y}/10`
      }}},
      scales: {
        x: { grid:{display:false} },
        y: { min:0, max:10, grid:{ color:"rgba(44,24,16,0.07)" } },
      },
    },
  });

  const top3 = data.top_performers;
  const bot3 = data.needs_attention;
  destroyChart("subjectRadarChart");
  charts.subjectRadarChart = new Chart($("subjectRadarChart"), {
    type: "radar",
    data: {
      labels: [...top3.map(s=>s.course_code), ...bot3.map(s=>s.course_code)],
      datasets: [
        { label:"Top Subjects",    data:[...top3.map(s=>s.avg_grade_point), ...bot3.map(()=>0)], borderColor:C.success, backgroundColor:C.success+"22", pointBackgroundColor:C.success },
        { label:"Low Subjects",    data:[...top3.map(()=>0), ...bot3.map(s=>s.avg_grade_point)], borderColor:C.danger,  backgroundColor:C.danger+"22",  pointBackgroundColor:C.danger  },
      ],
    },
    options: {
      responsive:true,
      scales:{ r:{ min:0, max:10, ticks:{ stepSize:2, backdropColor:"transparent" }, grid:{ color:"rgba(44,24,16,0.10)" } } },
      plugins:{ legend:{ position:"bottom" } },
    },
  });

  const hl = $("subject-highlights");
  hl.innerHTML = "";

  const makeHLCard = (title, list, kind) => {
    const card = el("div","sh-card");
    card.innerHTML = `<h4 class="${kind}">${title}</h4>` +
      list.slice(0,5).map((s,i) => `
        <div class="sh-row">
          <div class="sh-rank ${kind}">${i+1}</div>
          <div class="sh-info">
            <div class="sh-name">${s.course_name}</div>
            <div class="sh-meta">${s.course_code} · ${s.course_type} · Fail rate: ${s.fail_pct}%</div>
          </div>
          <div class="sh-gp" style="color:${kind==='top'?C.success:C.danger}">${s.avg_grade_point}</div>
        </div>`).join("");
    return card;
  };

  hl.appendChild(makeHLCard("🏆 Top Performing Subjects", subs.sort((a,b)=>b.avg_grade_point-a.avg_grade_point), "top"));
  hl.appendChild(makeHLCard("⚡ Subjects Needing Attention", subs.sort((a,b)=>a.avg_grade_point-b.avg_grade_point), "bottom"));
}

async function loadAttendance() {
  const data  = await apiFetch("/attendance-impact");
  const bands = data.bands;

  destroyChart("attImpactChart");
  charts.attImpactChart = new Chart($("attImpactChart"), {
    type: "bar",
    data: {
      labels: bands.map(b => b.attendance_band),
      datasets: [
        { label:"Avg Grade Point", data:bands.map(b=>b.avg_grade_point), backgroundColor:[C.success,C.primary,C.warning,C.danger], borderRadius:8, borderSkipped:false, yAxisID:"y" },
        { label:"Avg Marks",       data:bands.map(b=>b.avg_marks),       backgroundColor:[C.success+"55",C.primary+"55",C.warning+"55",C.danger+"55"], borderRadius:6, borderSkipped:false, yAxisID:"y1" },
      ],
    },
    options: {
      responsive:true,
      plugins:{ legend:{ position:"bottom" }, tooltip:{ mode:"index" } },
      scales:{
        x:{ grid:{ display:false } },
        y:{ min:0, max:10, position:"left",  title:{display:true, text:"Avg Grade Point"},  grid:{ color:"rgba(44,24,16,0.07)" } },
        y1:{ min:0, max:100, position:"right", title:{display:true, text:"Avg Total Marks"}, grid:{ display:false } },
      },
    },
  });

  destroyChart("attDistChart");
  charts.attDistChart = new Chart($("attDistChart"), {
    type: "doughnut",
    data: {
      labels: bands.map(b => b.attendance_band),
      datasets:[{
        data: bands.map(b=>b.count),
        backgroundColor:[C.success,C.primary,C.warning,C.danger],
        borderWidth:0, hoverOffset:8,
      }],
    },
    options:{
      responsive:true, cutout:"65%",
      plugins:{ legend:{ position:"bottom" }, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed} records` } } },
    },
  });

  renderInsight("att-insight-body", data.analysis.conclusion, data.analysis.suggestions);
}

async function loadAtRisk() {
  const [riskData, summaryData] = await Promise.all([
    apiFetch("/students/at-risk?limit=300"),
    apiFetch("/risk-summary"),
  ]);
  allRiskStudents = riskData;

  const bar = $("risk-summary-bar");
  bar.innerHTML = "";
  [
    { label:"Critical (CGPA<5 or Att<60%)", val:summaryData.critical_students, color:C.danger  },
    { label:"At-Risk (borderline)", val:summaryData.borderline_students, color:C.warning },
    { label:"Low Attendance (<75%)", val:summaryData.low_attendance, color:C.accent   },
    { label:"Flagged in table",      val:riskData.length,      color:C.primary  },
  ].forEach(k => {
    const d = el("div","risk-kpi");
    d.innerHTML = `<div class="risk-kpi-val" style="color:${k.color}">${k.val}</div><div class="risk-kpi-lbl">${k.label}</div>`;
    bar.appendChild(d);
  });

  const deptSel = $("dept-filter");
  const depts = [...new Set(riskData.map(s=>s.dept_code))].sort();
  depts.forEach(d => {
    const opt = document.createElement("option");
    opt.value = opt.textContent = d;
    deptSel.appendChild(opt);
  });

  renderRiskTable(riskData);
}

function renderRiskTable(rows) {
  const tbody = $("risk-tbody");
  tbody.innerHTML = "";
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:30px">No students found.</td></tr>`;
    return;
  }
  rows.forEach(s => {
    const trend = s.cgpa_trend > 0 ? "up" : s.cgpa_trend < 0 ? "down" : "flat";
    const trendIcon = trend==="up"?"▲ +":trend==="down"?"▼ ":"→ ";
    const riskLabel = s.risk_level==="critical"?"🔴 Critical":"🟡 At-Risk";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code style="font-size:12px;color:var(--brick)">${s.roll_number}</code></td>
      <td style="font-weight:600;color:var(--text)">${s.full_name}</td>
      <td>${s.dept_code}</td>
      <td style="font-weight:700;color:${s.cgpa<5?C.danger:s.cgpa<6.5?C.warning:C.success}">${s.cgpa}/10</td>
      <td style="color:${s.avg_attendance<60?C.danger:s.avg_attendance<75?C.warning:C.success}">${s.avg_attendance}%</td>
      <td><span class="trend-mini ${trend}">${trendIcon}${Math.abs(s.cgpa_trend)}</span></td>
      <td><span class="risk-chip ${s.risk_level}">${riskLabel}</span></td>
      <td><button class="btn-detail" onclick="openStudentModal(${s.student_id})">View</button></td>`;
    tbody.appendChild(tr);
  });
}

function filterRiskTable() {
  const q     = $("risk-search").value.toLowerCase();
  const level = $("risk-level-filter").value;
  const dept  = $("dept-filter").value;
  const filtered = allRiskStudents.filter(s => {
    const matchQ = !q || s.full_name.toLowerCase().includes(q) || s.roll_number.toLowerCase().includes(q);
    const matchL = !level || s.risk_level === level;
    const matchD = !dept  || s.dept_code  === dept;
    return matchQ && matchL && matchD;
  });
  renderRiskTable(filtered);
}

function openStudentModal(id) {
  const s = allRiskStudents.find(x => x.student_id === id);
  if (!s) return;
  const sgpaHtml = s.sgpa_history.map((g,i)=>`<span style="margin-right:10px">Sem ${i+1}: <b style="color:var(--brick)">${g}</b></span>`).join("");
  const recHtml  = s.recommendations.map(r=>`<li style="padding:5px 0;border-bottom:1px solid var(--bg2);font-size:13px;color:var(--text-dim)">${r}</li>`).join("");
  const lowHtml  = s.low_subjects.length ? s.low_subjects.map(c=>`<span style="background:#fdf0ec;color:var(--brick);padding:2px 8px;border-radius:2px;font-size:12px;margin-right:4px;border:1px solid #e0b8a8">${c}</span>`).join("") : "<em style='color:var(--text-muted)'>None</em>";

  let daaHtml = "";
  if (s.bfs_mentor) {
    const m = s.bfs_mentor;
    const distText = m.network_distance === 1 ? "1st Degree (Direct Classmate)" : m.network_distance === 2 ? "2nd Degree (Mutual Classmate)" : "3rd Degree Connection";
    daaHtml = `
      <div style="background: linear-gradient(135deg, #1d4e6b, #123246); color: white; padding: 14px; border-radius: 6px; margin-bottom: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border-left: 4px solid #b08d2b;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h4 style="margin: 0; font-size: 14px; display: flex; align-items: center; gap: 6px;">
            <span>🤝 Optimal Peer Mentor Match</span>
          </h4>
          <span style="background: rgba(255,255,255,0.2); font-size: 10px; padding: 2px 8px; border-radius: 12px; letter-spacing: 0.5px;text-transform:uppercase;">DAA BFS Algorithm</span>
        </div>
        <p style="font-size: 12px; margin: 0 0 10px 0; max-width: 90%; color: #e2e8f0; line-height: 1.4;">
          Algorithm traversed the classmate network graph to find the closest high-performing peer in <b>${m.subject}</b>.
        </p>
        <div style="display: flex; flex-direction: column; gap: 8px; background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 4px; margin-bottom: 4px;">
          <div style="font-size: 13px; font-weight: 600;">👤 ${m.mentor_name}</div>
          <div style="display: flex; gap: 15px;">
            <div style="font-size: 12px;">🎯 Scored: <b style="color: #4ade80;">${m.marks_in_subject}/100</b></div>
            <div style="font-size: 12px;">🔗 Network Distance: <b>${distText}</b></div>
          </div>
        </div>
      </div>
    `;
  }

  openModal(`
    <div style="border-bottom:2px solid var(--stone);padding-bottom:14px;margin-bottom:18px">
      <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:var(--text)">${s.full_name}</div>
      <div style="color:var(--text-muted);font-size:13px;margin-top:4px">${s.roll_number} · ${s.dept_name}</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px">
      <div style="background:#fdf8f0;border:1px solid var(--stone);border-radius:4px;padding:14px;text-align:center">
        <div style="font-size:30px;font-weight:800;font-family:'Playfair Display',serif;color:${s.cgpa<5?'#8B2500':s.cgpa<6.5?'#b08d2b':'#2d6a4f'}">${s.cgpa}</div>
        <div style="font-size:10px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px">CGPA / 10</div>
      </div>
      <div style="background:#fdf8f0;border:1px solid var(--stone);border-radius:4px;padding:14px;text-align:center">
        <div style="font-size:30px;font-weight:800;font-family:'Playfair Display',serif;color:${s.avg_attendance<60?'#8B2500':s.avg_attendance<75?'#b08d2b':'#2d6a4f'}">${s.avg_attendance}%</div>
        <div style="font-size:10px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px">Avg Attendance</div>
      </div>
    </div>
    <p style="font-size:10px;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700">SGPA History</p>
    <div style="margin-bottom:16px;font-size:13px;background:#fdf8f0;padding:10px;border-radius:3px">${sgpaHtml}</div>
    <p style="font-size:10px;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700">Weak Subjects</p>
    <div style="margin-bottom:16px">${lowHtml}</div>
    ${daaHtml}
    <p style="font-size:10px;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700">Recommendations</p>
    <ul style="list-style:none">${recHtml}</ul>`);
}

async function loadRecommendations() {
  const [summary, depts, trends, subjects, attendance, risk] = await Promise.all([
    apiFetch("/summary"),
    apiFetch("/departments"),
    apiFetch("/trends"),
    apiFetch("/subjects"),
    apiFetch("/attendance-impact"),
    apiFetch("/risk-summary"),
  ]);

  const recCards = [
    {
      icon:"📊", color:"#6366f1",
      title:"Institution-wide",
      subtitle:"Overall academic health",
      items: [
        ...(summary.analysis.conclusion||[]),
        ...(summary.analysis.suggestions||[]),
      ],
    },
    {
      icon:"🏛️", color:"#a855f7",
      title:"Department Strategy",
      subtitle:"Department-specific actions",
      items: depts.flatMap(d => [
        ...(d.analysis.conclusion||[]).slice(0,1),
        ...(d.analysis.suggestions||[]),
      ]).slice(0,6),
    },
    {
      icon:"📈", color:"#38bdf8",
      title:"Trend Interventions",
      subtitle:"Based on YoY performance",
      items: [
        ...(trends.analysis.conclusion||[]),
        ...(trends.analysis.suggestions||[]),
      ],
    },
    {
      icon:"📚", color:"#10b981",
      title:"Subject Improvements",
      subtitle:"Course-level recommendations",
      items: subjects.needs_attention.flatMap(s =>
        (s.analysis.suggestions||[]).map(r => `[${s.course_code}] ${r}`)
      ).slice(0,6),
    },
    {
      icon:"🗓️", color:"#f59e0b",
      title:"Attendance Policy",
      subtitle:"Attendance management",
      items: [
        ...(attendance.analysis.conclusion||[]),
        ...(attendance.analysis.suggestions||[]),
      ],
    },
    {
      icon:"⚠️", color:"#ef4444",
      title:"At-Risk Student Actions",
      subtitle:"Immediate interventions",
      items: [
        `${risk.critical_students} students are in critical condition – immediate counselling required.`,
        `${risk.low_attendance} students have attendance below 75% – risk of exam barment.`,
        "Assign dedicated faculty mentors to all at-risk students.",
        "Conduct monthly parent-teacher meetings for flagged students.",
        "Set up a helpdesk with academic and mental health support resources.",
        "Introduce a 'buddy system' pairing top performers with struggling peers.",
      ],
    },
    {
      icon:"💼", color:"#ec4899",
      title:"Management Strategies",
      subtitle:"Institutional policy recommendations",
      items: [
        "Publish a monthly academic performance report for all HODs.",
        "Integrate EduInsight data into the annual accreditation report.",
        "Set CGPA improvement targets per department for the next academic year.",
        "Introduce a student excellence award to incentivize top performers.",
        "Review and update syllabi of high-failure courses.",
        "Invest in faculty development programs focusing on modern pedagogy.",
      ],
    },
    {
      icon:"🔬", color:"#fb923c",
      title:"Research & Data",
      subtitle:"Data quality & analytics",
      items: [
        "Ensure data entry pipelines are audited at semester end.",
        "Expand data collection to include co-curricular and extracurricular performance.",
        "Explore predictive ML models for early-warning detection.",
        "Benchmark institution metrics against top universities nationally.",
      ],
    },
  ];

  const grid = $("rec-grid");
  grid.innerHTML = "";
  recCards.forEach(c => {
    if (!c.items || c.items.length === 0) return;
    const card = el("div","rec-card");
    card.innerHTML = `
      <div class="rec-card-header">
        <div class="rec-icon" style="background:${c.color}22;color:${c.color}">${c.icon}</div>
        <div><div class="rec-title">${c.title}</div><div class="rec-subtitle">${c.subtitle}</div></div>
      </div>
      <ul class="rec-items">${c.items.slice(0,6).map(i=>`<li>${i}</li>`).join("")}</ul>`;
    grid.appendChild(card);
  });
}

// Reusable render block for the AI insight panels
function renderInsight(targetId, conclusions, suggestions) {
  $(targetId).innerHTML = `
    <div class="insight-col">
      <h4>📝 Conclusions</h4>
      <ul>${(conclusions||[]).map(c=>`<li>${c}</li>`).join("")}</ul>
    </div>
    <div class="insight-col">
      <h4>💡 Improvement Suggestions</h4>
      <ul>${(suggestions||[]).map(s=>`<li>${s}</li>`).join("")}</ul>
    </div>`;
}

// ── Student Monitor ─────────────────────────────────────────────
let allMonitorStudents = [];

async function loadMonitor() {
  const students = await apiFetch("/students?limit=500");
  allMonitorStudents = students;

  // Populate dept filter
  const deptSel = $("monitor-dept-filter");
  const depts = [...new Set(students.map(s => s.dept_code))].sort();
  depts.forEach(d => {
    const opt = document.createElement("option");
    opt.value = opt.textContent = d;
    deptSel.appendChild(opt);
  });

  // Stats bar
  const critical = students.filter(s => s.risk_level === "critical").length;
  const atRisk   = students.filter(s => s.risk_level === "at_risk").length;
  const good     = students.filter(s => s.risk_level === "good").length;
  const stats = $("monitor-stats");
  stats.innerHTML = [
    { label: "Total Students",  val: students.length,  color: C.info    },
    { label: "Critical",        val: critical,          color: C.danger  },
    { label: "At-Risk",         val: atRisk,            color: C.warning },
    { label: "Good Standing",   val: good,              color: C.success },
  ].map(k => `
    <div class="risk-kpi">
      <div class="risk-kpi-val" style="color:${k.color}">${k.val}</div>
      <div class="risk-kpi-lbl">${k.label}</div>
    </div>`).join("");

  filterMonitorTable();
}

function filterMonitorTable() {
  const q      = ($("monitor-search").value || "").toLowerCase();
  const dept   = $("monitor-dept-filter").value;
  const risk   = $("monitor-risk-filter").value;
  const sortBy = $("monitor-sort").value;

  let rows = allMonitorStudents.filter(s => {
    const matchQ = !q || s.full_name.toLowerCase().includes(q) || s.roll_number.toLowerCase().includes(q);
    const matchD = !dept || s.dept_code === dept;
    const matchR = !risk || s.risk_level === risk;
    return matchQ && matchD && matchR;
  });

  rows = [...rows].sort((a, b) => {
    if (sortBy === "cgpa_asc")  return a.cgpa - b.cgpa;
    if (sortBy === "cgpa_desc") return b.cgpa - a.cgpa;
    if (sortBy === "att_asc")   return a.avg_attendance - b.avg_attendance;
    if (sortBy === "att_desc")  return b.avg_attendance - a.avg_attendance;
    if (sortBy === "name")      return a.full_name.localeCompare(b.full_name);
    return 0;
  });

  renderMonitorTable(rows);
}

function renderMonitorTable(rows) {
  const tbody = $("monitor-tbody");
  tbody.innerHTML = "";
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:var(--text-muted);padding:30px">No students found matching your criteria.</td></tr>`;
    return;
  }
  rows.forEach((s, idx) => {
    const trend     = s.cgpa_trend > 0 ? "up" : s.cgpa_trend < 0 ? "down" : "flat";
    const trendIcon = trend === "up" ? "▲ +" : trend === "down" ? "▼ " : "→ ";
    const riskLabel = s.risk_level === "critical" ? "🔴 Critical" : s.risk_level === "at_risk" ? "🟡 At-Risk" : "🟢 Good";
    const cgpaColor = s.cgpa < 5 ? C.danger : s.cgpa < 6.5 ? C.warning : C.success;
    const attColor  = s.avg_attendance < 60 ? C.danger : s.avg_attendance < 75 ? C.warning : C.success;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="color:var(--text-muted);font-size:11px">${idx + 1}</td>
      <td><code style="font-size:11px;color:var(--brick)">${s.roll_number}</code></td>
      <td style="font-weight:600;color:var(--text)">${s.full_name}</td>
      <td><span style="font-size:11px;background:#f0e9d8;padding:2px 7px;border-radius:2px;border:1px solid var(--stone);font-weight:600">${s.dept_code}</span></td>
      <td style="font-weight:700;color:${cgpaColor}">${s.cgpa}/10</td>
      <td style="color:${attColor}">${s.avg_attendance}%</td>
      <td><span class="trend-mini ${trend}">${trendIcon}${Math.abs(s.cgpa_trend)}</span></td>
      <td><span class="risk-chip ${s.risk_level}">${riskLabel}</span></td>
      <td><button class="btn-detail" onclick="openMonitorStudentModal(${s.student_id})">View</button></td>`;
    tbody.appendChild(tr);
  });
}

function openMonitorStudentModal(id) {
  const s = allMonitorStudents.find(x => x.student_id === id);
  if (!s) return;
  const sgpaHtml = (s.sgpa_history || []).map((g, i) => `<span style="margin-right:10px">Sem ${i+1}: <b style="color:var(--brick)">${g}</b></span>`).join("");
  const cgpaColor = s.cgpa < 5 ? "#8B2500" : s.cgpa < 6.5 ? "#b08d2b" : "#2d6a4f";
  const attColor  = s.avg_attendance < 60 ? "#8B2500" : s.avg_attendance < 75 ? "#b08d2b" : "#2d6a4f";
  const riskBadge = s.risk_level === "critical"
    ? `<span style="background:#fdf0ec;color:#8B2500;padding:4px 12px;border-radius:2px;font-size:11px;font-weight:700;border:1px solid #e0b8a8;text-transform:uppercase;letter-spacing:1px">🔴 Critical</span>`
    : s.risk_level === "at_risk"
    ? `<span style="background:#faf3e0;color:#b08d2b;padding:4px 12px;border-radius:2px;font-size:11px;font-weight:700;border:1px solid #e0cc80;text-transform:uppercase;letter-spacing:1px">🟡 At-Risk</span>`
    : `<span style="background:#e8f4ef;color:#2d6a4f;padding:4px 12px;border-radius:2px;font-size:11px;font-weight:700;border:1px solid #b7d9c8;text-transform:uppercase;letter-spacing:1px">🟢 Good Standing</span>`;
  const trend = s.cgpa_trend > 0 ? `<span style="color:#2d6a4f">▲ Improving (+${s.cgpa_trend})</span>` : s.cgpa_trend < 0 ? `<span style="color:#8B2500">▼ Declining (${s.cgpa_trend})</span>` : `<span style="color:var(--text-muted)">→ Stable</span>`;

  openModal(`
    <div style="border-bottom:2px solid var(--stone);padding-bottom:14px;margin-bottom:18px">
      <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:var(--text)">${s.full_name}</div>
      <div style="color:var(--text-muted);font-size:13px;margin-top:4px">${s.roll_number} · ${s.dept_name} · Admitted ${s.admission_year} · ${s.gender || ""}</div>
      <div style="margin-top:10px">${riskBadge}</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:18px">
      <div style="background:#fdf8f0;border:1px solid var(--stone);border-radius:4px;padding:14px;text-align:center">
        <div style="font-size:28px;font-weight:800;font-family:'Playfair Display',serif;color:${cgpaColor}">${s.cgpa}</div>
        <div style="font-size:10px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px">CGPA / 10</div>
      </div>
      <div style="background:#fdf8f0;border:1px solid var(--stone);border-radius:4px;padding:14px;text-align:center">
        <div style="font-size:28px;font-weight:800;font-family:'Playfair Display',serif;color:${attColor}">${s.avg_attendance}%</div>
        <div style="font-size:10px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px">Avg Attendance</div>
      </div>
      <div style="background:#fdf8f0;border:1px solid var(--stone);border-radius:4px;padding:14px;text-align:center">
        <div style="font-size:18px;font-weight:800;margin-top:5px">${trend}</div>
        <div style="font-size:10px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px">CGPA Trend</div>
      </div>
    </div>
    <p style="font-size:10px;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700">Semester-wise SGPA History</p>
    <div style="margin-bottom:16px;font-size:13px;background:#fdf8f0;padding:10px;border-radius:3px;line-height:2">${sgpaHtml || '<em style="color:var(--text-muted)">No SGPA data available</em>'}</div>`);
}


const loaders = {
  overview:        loadOverview,
  departments:     loadDepartments,
  trends:          loadTrends,
  subjects:        loadSubjects,
  attendance:      loadAttendance,
  atrisk:          loadAtRisk,
  monitor:         loadMonitor,
  recommendations: loadRecommendations,
};
const loaded = {};

function switchTab(tab) {
  document.querySelectorAll(".tab-content").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => {
    n.classList.toggle("active", n.dataset.tab === tab);
  });
  $(`tab-${tab}`).classList.add("active");
  $("page-title").textContent = tabMeta[tab].title;
  $("page-sub").textContent   = tabMeta[tab].sub;

  if (!loaded[tab] && loaders[tab]) {
    loaded[tab] = true;
    loaders[tab]().catch(err => {
      console.error(`Error loading ${tab}:`, err);
    });
  }
}

async function init() {
  try {
    $("loading-overlay").classList.remove("hidden");
    await loadOverview();
    loaded["overview"] = true;
    $("loading-overlay").classList.add("hidden");
    $("status-text").textContent = "Live Data";
    $("status-pill").querySelector(".pulse").style.background = "var(--success)";
  } catch (err) {
    $("loading-overlay").innerHTML = `
      <div style="text-align:center">
        <div style="font-size:48px;margin-bottom:16px">⚠️</div>
        <h2 style="color:#ef4444;margin-bottom:8px">API Connection Failed</h2>
        <p style="color:var(--text-muted);font-size:14px">Make sure the EduInsight API is running:</p>
        <code style="background:rgba(255,255,255,0.05);padding:10px 20px;border-radius:8px;display:inline-block;margin-top:12px;font-size:13px">
          cd c:\\Codes\\EduInsight && uvicorn api.main:app --port 8000
        </code>
        <br/><button onclick="location.reload()" style="margin-top:20px;padding:10px 24px;background:#6366f1;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px">Retry</button>
      </div>`;
    $("status-text").textContent = "Offline";
    $("status-pill").querySelector(".pulse").style.background = "#ef4444";
    console.error(err);
  }
}

window.addEventListener("DOMContentLoaded", init);
