/**
 * internship.js — Internship Approval Module
 */

const Internship = {
  init() {
    const s = App.state.student;
    const locked = !s;
    document.getElementById("intGate").style.display = locked ? "block" : "none";
    document.getElementById("intForm").style.display = locked ? "none"  : "block";
  },

  validate() {
    clearAllErr(["int_company","int_role","int_type","int_start","int_end","int_desc"]);
    let valid = true;
    if (!getVal("int_company")) { markErr("int_company", "Company name is required.");   valid = false; }
    if (!getVal("int_role"))    { markErr("int_role",    "Internship role is required."); valid = false; }
    if (!getVal("int_type"))    { markErr("int_type",    "Please select internship type."); valid = false; }
    if (!getVal("int_start"))   { markErr("int_start",   "Start date is required.");     valid = false; }
    if (!getVal("int_end"))     { markErr("int_end",     "End date is required.");       valid = false; }
    if (!getVal("int_desc"))    { markErr("int_desc",    "Description is required.");    valid = false; }
    if (getVal("int_desc").length > 0 && getVal("int_desc").length < 20) {
      markErr("int_desc", "Description must be at least 20 characters."); valid = false;
    }
    if (getVal("int_start") && getVal("int_end") && getVal("int_start") > getVal("int_end")) {
      markErr("int_end", "End date must be after start date."); valid = false;
    }
    return valid;
  },

  clear() {
    ["int_company","int_role","int_type","int_start","int_end","int_stipend","int_desc"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    clearAllErr(["int_company","int_role","int_type","int_start","int_end","int_desc"]);
  },

  async submit() {
    if (!this.validate()) { Toast.show("Fix highlighted errors.", "error"); return; }

    const s   = App.state.student;
    const btn = document.getElementById("intSubmitBtn");
    btn.disabled = true; btn.textContent = "Submitting…";

    const payload = {
      registration_id:  s.registration_id,
      company_name:     getVal("int_company"),
      internship_role:  getVal("int_role"),
      internship_type:  getVal("int_type"),
      start_date:       getVal("int_start"),
      end_date:         getVal("int_end"),
      stipend:          getVal("int_stipend") || "Unpaid",
      description:      getVal("int_desc"),
    };

    try {
      const { ok, data } = await Api.applyInternship(payload);
      if (ok) {
        App.state.applications.push(data.application);
        Toast.show(`Internship application ${data.application.application_id} submitted!`, "success");
        this.clear();
        setTimeout(() => App.navigate("history"), 1400);
      } else {
        Toast.show(data.message || "Submission failed.", "error");
      }
    } catch (_) {
      this._offlineSubmit(payload);
    } finally {
      btn.disabled = false; btn.textContent = "✉️ Submit for Approval";
    }
  },

  _offlineSubmit(payload) {
    const s     = App.state.student;
    const appId = `INT-${new Date().toISOString().slice(0,10).replace(/-/g,"")}-${randId()}`;
    App.state.applications.push({
      application_id:  appId,
      registration_id: s.registration_id,
      student_name:    s.full_name,
      department:      s.department,
      program_type:    s.program_type,
      company_name:    payload.company_name,
      internship_role: payload.internship_role,
      internship_type: payload.internship_type,
      start_date:      payload.start_date,
      end_date:        payload.end_date,
      stipend:         payload.stipend,
      description:     payload.description,
      status:          "Pending",
      submitted_on:    todayStr(),
      type:            "Internship",
    });
    Toast.show(`Internship application ${appId} submitted (demo mode)!`, "success");
    this.clear();
    setTimeout(() => App.navigate("history"), 1400);
  }
};
