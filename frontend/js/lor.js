/**
 * lor.js — Letter of Recommendation Module
 */

const LOR = {
  async init() {
    const s = App.state.student;
    const locked = !s;
    document.getElementById("lorGate").style.display = locked ? "block" : "none";
    document.getElementById("lorForm").style.display = locked ? "none"  : "block";
    if (!s) return;

    const select = document.getElementById("lor_faculty");
    select.innerHTML = `<option value="">-- Select Faculty --</option>`;

    try {
      const { ok, data } = await Api.getFaculty(s.department);
      if (ok) {
        data.faculty.forEach(f => {
          const opt = document.createElement("option");
          opt.value = f.id;
          opt.textContent = `${f.name} — ${f.designation}`;
          select.appendChild(opt);
        });
        return;
      }
    } catch (_) {}

    // Offline fallback
    (OFFLINE_FACULTY[s.department] || []).forEach(f => {
      const opt = document.createElement("option");
      opt.value = f.id;
      opt.textContent = `${f.name} — ${f.designation}`;
      select.appendChild(opt);
    });
  },

  validate() {
    clearAllErr(["lor_faculty", "lor_purpose"]);
    let valid = true;
    if (!getVal("lor_faculty")) { markErr("lor_faculty", "Please select a faculty member."); valid = false; }
    if (!getVal("lor_purpose")) { markErr("lor_purpose", "Please select a purpose.");        valid = false; }
    return valid;
  },

  clear() {
    ["lor_faculty", "lor_purpose", "lor_details"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    clearAllErr(["lor_faculty", "lor_purpose"]);
  },

  async submit() {
    if (!this.validate()) { Toast.show("Fix highlighted errors.", "error"); return; }

    const s   = App.state.student;
    const btn = document.getElementById("lorSubmitBtn");
    btn.disabled = true; btn.textContent = "Submitting…";

    const payload = {
      registration_id:    s.registration_id,
      faculty_id:         getVal("lor_faculty"),
      purpose:            getVal("lor_purpose"),
      additional_details: getVal("lor_details"),
    };

    try {
      const { ok, data } = await Api.applyLOR(payload);
      if (ok) {
        App.state.applications.push(data.application);
        Toast.show(`LOR application ${data.application.application_id} submitted!`, "success");
        this.clear();
        setTimeout(() => App.navigate("history"), 1400);
      } else {
        Toast.show(data.message || "Submission failed.", "error");
      }
    } catch (_) {
      this._offlineSubmit(payload);
    } finally {
      btn.disabled = false; btn.textContent = "✉️ Submit LOR Application";
    }
  },

  _offlineSubmit(payload) {
    const s = App.state.student;
    const sel  = document.getElementById("lor_faculty");
    const name = sel.options[sel.selectedIndex]?.text.split(" — ")[0] || "Faculty";
    const appId = `LOR-${new Date().toISOString().slice(0,10).replace(/-/g,"")}-${randId()}`;
    App.state.applications.push({
      application_id:     appId,
      registration_id:    s.registration_id,
      student_name:       s.full_name,
      department:         s.department,
      faculty_id:         payload.faculty_id,
      faculty_name:       name,
      purpose:            payload.purpose,
      additional_details: payload.additional_details,
      status:             "Pending",
      submitted_on:       todayStr(),
      type:               "LOR",
    });
    Toast.show(`LOR application ${appId} submitted (demo mode)!`, "success");
    this.clear();
    setTimeout(() => App.navigate("history"), 1400);
  }
};
