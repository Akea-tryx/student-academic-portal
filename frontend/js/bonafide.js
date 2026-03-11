/**
 * bonafide.js — Bonafide Certificate Module + Application History
 */

// ── BONAFIDE ─────────────────────────────────────────────────────
const Bonafide = {
  init() {
    const s = App.state.student;
    const locked = !s;
    document.getElementById("bonGate").style.display = locked ? "block" : "none";
    document.getElementById("bonForm").style.display = locked ? "none"  : "block";
  },

  validate() {
    clearAllErr(["bon_purpose", "bon_reason"]);
    let valid = true;
    if (!getVal("bon_purpose")) { markErr("bon_purpose", "Please select a purpose."); valid = false; }
    if (!getVal("bon_reason"))  { markErr("bon_reason",  "Reason is required.");       valid = false; }
    if (getVal("bon_reason").length > 0 && getVal("bon_reason").length < 10) {
      markErr("bon_reason", "Reason must be at least 10 characters."); valid = false;
    }
    return valid;
  },

  clear() {
    ["bon_purpose", "bon_reason"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    clearAllErr(["bon_purpose", "bon_reason"]);
  },

  async submit() {
    if (!this.validate()) { Toast.show("Fix highlighted errors.", "error"); return; }

    const s   = App.state.student;
    const btn = document.getElementById("bonSubmitBtn");
    btn.disabled = true; btn.textContent = "Submitting…";

    const payload = {
      registration_id: s.registration_id,
      purpose:         getVal("bon_purpose"),
      reason:          getVal("bon_reason"),
    };

    try {
      const { ok, data } = await Api.applyBonafide(payload);
      if (ok) {
        App.state.applications.push(data.application);
        Toast.show(`Bonafide request ${data.application.application_id} submitted!`, "success");
        this.clear();
        setTimeout(() => App.navigate("history"), 1400);
      } else {
        Toast.show(data.message || "Submission failed.", "error");
      }
    } catch (_) {
      this._offlineSubmit(payload);
    } finally {
      btn.disabled = false; btn.textContent = "✉️ Submit Request";
    }
  },

  _offlineSubmit(payload) {
    const s     = App.state.student;
    const appId = `BON-${new Date().toISOString().slice(0,10).replace(/-/g,"")}-${randId()}`;
    App.state.applications.push({
      application_id:  appId,
      registration_id: s.registration_id,
      student_name:    s.full_name,
      department:      s.department,
      program_type:    s.program_type,
      purpose:         payload.purpose,
      reason:          payload.reason,
      status:          "Pending",
      submitted_on:    todayStr(),
      type:            "Bonafide",
    });
    Toast.show(`Bonafide request ${appId} submitted (demo mode)!`, "success");
    this.clear();
    setTimeout(() => App.navigate("history"), 1400);
  }
};

// ── APPLICATION HISTORY ───────────────────────────────────────────
const History = {
  cardHTML(a) {
    const detail = a.type === "LOR"
      ? `Faculty: ${a.faculty_name} &bull; ${a.purpose}`
      : `Purpose: ${a.purpose}`;
    const rowsJson = JSON.stringify(History._modalRows(a)).replace(/'/g, "&#39;");
    return `
      <div class="app-card" onclick='Modal.open("Application Details", ${rowsJson})'>
        <div class="app-card-left">
          <span class="app-type-badge app-type-${a.type}">${a.type}</span>
          <div class="app-card-id">${a.application_id}</div>
          <div class="app-card-name">${a.student_name}</div>
          <div class="app-card-meta">${detail}</div>
          <div class="app-card-meta" style="margin-top:3px;color:#999;font-size:0.75rem;">📅 ${a.submitted_on}</div>
        </div>
        <div class="app-card-right">
          <span class="status-pill status-${a.status}">${a.status}</span>
        </div>
      </div>`;
  },

  _modalRows(a) {
    const rows = [
      ["Application ID", a.application_id],
      ["Type",           a.type],
      ["Status",         a.status],
      ["Submitted On",   a.submitted_on],
      ["Department",     a.department],
    ];
    if (a.type === "LOR") {
      rows.push(["Faculty", a.faculty_name]);
      rows.push(["Purpose", a.purpose]);
      if (a.additional_details) rows.push(["Details", a.additional_details]);
    } else {
      rows.push(["Purpose", a.purpose]);
      rows.push(["Reason",  a.reason]);
    }
    return rows;
  },

  async render() {
    const s = App.state.student;
    document.getElementById("historyGate").style.display    = s ? "none"  : "block";
    document.getElementById("historyContent").style.display = s ? "block" : "none";
    if (!s) return;

    try {
      const { ok, data } = await Api.getApplications(s.registration_id);
      if (ok) App.state.applications = data.applications;
    } catch (_) { /* use local state */ }

    const container = document.getElementById("appHistoryList");
    const apps      = [...App.state.applications].reverse();
    container.innerHTML = apps.length
      ? apps.map(a => History.cardHTML(a)).join("")
      : `<div class="empty-state"><div class="es-icon">📋</div><p>No applications submitted yet.</p></div>`;
  }
};
