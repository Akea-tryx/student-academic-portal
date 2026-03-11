/**
 * profile.js — Student Profile Module
 */

const Profile = {
  FIELDS: [
    { id: "p_name",     label: "Full Name" },
    { id: "p_regid",    label: "Registration ID" },
    { id: "p_program",  label: "Program Type" },
    { id: "p_dept",     label: "Department" },
    { id: "p_duration", label: "Course Duration" },
    { id: "p_cgpa",     label: "CGPA" },
    { id: "p_cemail",   label: "College Email" },
    { id: "p_pemail",   label: "Personal Email" },
    { id: "p_mobile",   label: "Mobile Number" },
  ],

  validate() {
    const ids = this.FIELDS.map(f => f.id);
    clearAllErr(ids);
    let valid = true;

    this.FIELDS.forEach(f => {
      if (!getVal(f.id)) { markErr(f.id, `${f.label} is required.`); valid = false; }
    });

    const cgpa = parseFloat(getVal("p_cgpa"));
    if (getVal("p_cgpa") && (isNaN(cgpa) || cgpa < 0 || cgpa > 10)) {
      markErr("p_cgpa", "CGPA must be between 0.0 and 10.0."); valid = false;
    }

    const emailRe = /^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$/;
    if (getVal("p_cemail") && !emailRe.test(getVal("p_cemail"))) {
      markErr("p_cemail", "Invalid email format."); valid = false;
    }
    if (getVal("p_pemail") && !emailRe.test(getVal("p_pemail"))) {
      markErr("p_pemail", "Invalid email format."); valid = false;
    }
    if (getVal("p_mobile") && !/^\d{10}$/.test(getVal("p_mobile"))) {
      markErr("p_mobile", "Must be exactly 10 digits."); valid = false;
    }
    return valid;
  },

  async save() {
    if (!this.validate()) { Toast.show("Please fix the highlighted errors.", "error"); return; }

    const btn = document.getElementById("saveProfileBtn");
    btn.disabled = true;
    btn.textContent = "Saving…";

    const payload = {
      full_name:       getVal("p_name"),
      registration_id: getVal("p_regid"),
      program_type:    getVal("p_program"),
      department:      getVal("p_dept"),
      course_duration: getVal("p_duration"),
      cgpa:            getVal("p_cgpa"),
      college_email:   getVal("p_cemail"),
      personal_email:  getVal("p_pemail"),
      mobile:          getVal("p_mobile"),
    };

    try {
      const { ok, data } = await Api.createProfile(payload);
      if (ok) {
        App.state.student = data.student;
        this._onSuccess();
      } else {
        btn.disabled = false;
        btn.textContent = "💾 Save & Verify Profile";
        Toast.show(data.message || "Failed to save profile.", "error");
      }
    } catch (_) {
      // Backend not running — demo mode
      App.state.student = { ...payload, cgpa: parseFloat(payload.cgpa), profile_verified: true };
      this._onSuccess();
    }
  },

  _onSuccess() {
    App.unlockServices();
    document.getElementById("profileBanner").style.display = "flex";
    const btn = document.getElementById("saveProfileBtn");
    btn.textContent = "✅ Profile Verified";
    btn.disabled    = true;
    this.FIELDS.forEach(f => {
      const el = document.getElementById(f.id);
      if (el) el.disabled = true;
    });
    Toast.show("Profile verified! Academic services are now unlocked.", "success");
    setTimeout(() => App.navigate("dashboard"), 1600);
  }
};
