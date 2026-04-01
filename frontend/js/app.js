/**
 * app.js — Application State, Navigation, Toast, Modal, Dashboard
 */

// ── OFFLINE FACULTY DATA (fallback when backend is not running) ──
const OFFLINE_FACULTY = {
  CSE: [
    { id: "CSE01", name: "Dr. Anand Krishnamurthy",  designation: "Professor" },
    { id: "CSE02", name: "Dr. Priya Venkataraman",   designation: "Associate Professor" },
    { id: "CSE03", name: "Prof. Ramesh Babu",         designation: "Assistant Professor" },
  ],
  CCE: [
    { id: "CCE01", name: "Dr. Meenakshi Sundaram",   designation: "Professor" },
    { id: "CCE02", name: "Prof. Karthik Selvam",      designation: "Associate Professor" },
    { id: "CCE03", name: "Dr. Lakshmi Narayanan",    designation: "Assistant Professor" },
  ],
  ECE: [
    { id: "ECE01", name: "Dr. Suresh Rajan",          designation: "Professor" },
    { id: "ECE02", name: "Dr. Divya Chandrasekaran",  designation: "Associate Professor" },
    { id: "ECE03", name: "Prof. Arjun Pillai",        designation: "Assistant Professor" },
  ],
};

// ── APP STATE ────────────────────────────────────────────────────
const App = {
  state: {
    student:      null,
    applications: [],
  },

  navigate(page) {
    const locked = ["lor", "bonafide", "internship", "history"];
    if (locked.includes(page) && !App.state.student) {
      Toast.show("Complete your profile first to access this service.", "warning");
      App.navigate("profile");
      return;
    }

    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

    const pageEl = document.getElementById("page-" + page);
    const navEl  = document.getElementById("nav-"  + page);
    if (pageEl) pageEl.classList.add("active");
    if (navEl)  navEl.classList.add("active");

    if (page === "dashboard") Dashboard.refresh();
    if (page === "lor")        LOR.init();
    if (page === "internship") Internship.init();
    if (page === "bonafide")  Bonafide.init();
    if (page === "history")   History.render();
  },

  unlockServices() {
    ["lor", "bonafide", "internship", "history"].forEach(s => {
      const nav  = document.getElementById("nav-"  + s);
      const lock = document.getElementById("lock-" + s);
      if (nav)  nav.classList.remove("locked");
      if (lock) lock.style.display = "none";
    });
    const pill = document.getElementById("userPill");
    if (pill) {
      pill.textContent = "✅ " + App.state.student.full_name;
      pill.classList.add("verified");
    }
  },
};

// ── TOAST ────────────────────────────────────────────────────────
const Toast = {
  _timer: null,
  show(msg, type = "info") {
    const el = document.getElementById("toast");
    if (!el) return;
    const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
    el.innerHTML = `<span>${icons[type] || ""}</span> ${msg}`;
    el.className = `t-${type}`;
    el.classList.add("show");
    if (this._timer) clearTimeout(this._timer);
    this._timer = setTimeout(() => el.classList.remove("show"), 4200);
  }
};

// ── MODAL ────────────────────────────────────────────────────────
const Modal = {
  open(title, rows) {
    document.getElementById("modalTitle").textContent = title;
    document.getElementById("modalBody").innerHTML = rows
      .map(([k, v]) => `<tr><td>${k}</td><td><strong>${v || "—"}</strong></td></tr>`)
      .join("");
    document.getElementById("appModal").classList.add("open");
  },
  close() {
    document.getElementById("appModal").classList.remove("open");
  }
};

// ── FORM HELPERS ─────────────────────────────────────────────────
function getVal(id)       { return (document.getElementById(id)?.value || "").trim(); }
function setErr(id, msg)  { const e = document.getElementById("err_" + id); if (e) e.textContent = msg; }
function clearErr(id)     { setErr(id, ""); document.getElementById(id)?.classList.remove("is-error"); }
function markErr(id, msg) { setErr(id, msg); document.getElementById(id)?.classList.add("is-error"); }
function clearAllErr(ids) { ids.forEach(clearErr); }

function randId()   { return Math.random().toString(36).substr(2, 6).toUpperCase(); }
function todayStr() {
  return new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
    + ", " + new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

// ── DASHBOARD ────────────────────────────────────────────────────
const Dashboard = {
  refresh() {
    const s = App.state.student;
    document.getElementById("dashLockBanner").style.display = s ? "none"  : "block";
    document.getElementById("dashUnlocked").style.display   = s ? "block" : "none";
    if (!s) return;

    document.getElementById("dashHero").innerHTML = `
      <div class="hero-avatar">${s.full_name.charAt(0).toUpperCase()}</div>
      <div class="hero-info">
        <h3>${s.full_name}</h3>
        <p>${s.registration_id} &bull; ${s.college_email}</p>
        <div class="hero-tags">
          <span class="hero-tag">${s.program_type}</span>
          <span class="hero-tag">${s.department}</span>
          <span class="hero-tag">CGPA: ${s.cgpa}</span>
          <span class="hero-tag">${s.course_duration}</span>
        </div>
      </div>`;

    const apps = App.state.applications;
    document.getElementById("statTotal").textContent    = apps.length;
    document.getElementById("statPending").textContent  = apps.filter(a => a.status === "Pending").length;
    document.getElementById("statApproved").textContent = apps.filter(a => a.status === "Approved").length;

    const recent = [...apps].reverse().slice(0, 4);
    const el = document.getElementById("recentApps");
    el.innerHTML = recent.length
      ? `<div class="app-list">${recent.map(a => History.cardHTML(a)).join("")}</div>`
      : `<div class="empty-state"><div class="es-icon">📂</div><p>No applications yet. Use Quick Actions to get started.</p></div>`;
  }
};
