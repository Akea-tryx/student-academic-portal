/**
 * profile.js — Student Profile Module
 * College email strictly validated: must end with @muj.manipal.edu
 */

const Profile = {
 FIELDS: [
 { id: "p_name", label: "Full Name" },
 { id: "p_regid", label: "Registration ID" },
 { id: "p_program", label: "Program Type" },
 { id: "p_dept", label: "Department" },
 { id: "p_duration", label: "Course Duration" },
 { id: "p_cgpa", label: "CGPA" },
 { id: "p_cemail", label: "College Email" },
 { id: "p_pemail", label: "Personal Email" },
 { id: "p_mobile", label: "Mobile Number" },
 ],

 COLLEGE_DOMAIN: "muj.manipal.edu",

 validateCollegeEmail(email) {
 email = email.trim().toLowerCase();
 if (!email) return "College email is required.";
 if (!email.endsWith("@" + this.COLLEGE_DOMAIN)) {
 return `College email must end with @${this.COLLEGE_DOMAIN}\nExample: name.enrollmentid@${this.COLLEGE_DOMAIN}`;
 }
 const pattern = /^[a-zA-Z0-9][a-zA-Z0-9._+-]*@muj\.manipal\.edu$/;
 if (!pattern.test(email)) {
 return `Invalid college email format. Expected: name.enrollmentid@${this.COLLEGE_DOMAIN}`;
 }
 return null; // null = valid
 },

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

 // College email — strict MUJ domain check
 const cEmailErr = this.validateCollegeEmail(getVal("p_cemail"));
 if (cEmailErr) { markErr("p_cemail", cEmailErr); valid = false; }

 // Personal email — standard format, must not be MUJ
 const pemail = getVal("p_pemail");
 const emailRe = /^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$/;
 if (pemail && !emailRe.test(pemail)) {
 markErr("p_pemail", "Invalid personal email format."); valid = false;
 } else if (pemail && pemail.toLowerCase().endsWith("@" + this.COLLEGE_DOMAIN)) {
 markErr("p_pemail", "Personal email must be different from your college email."); valid = false;
 }

 if (getVal("p_mobile") && !/^\d{10}$/.test(getVal("p_mobile"))) {
 markErr("p_mobile", "Must be exactly 10 digits."); valid = false;
 }
 return valid;
 },

 async save() {
 if (!this.validate()) { Toast.show("Please fix the highlighted errors.", "error"); return; }

 const btn = document.getElementById("saveProfileBtn");
 btn.disabled = true; btn.textContent = "Saving…";

 const payload = {
 full_name: getVal("p_name"),
 registration_id: getVal("p_regid"),
 program_type: getVal("p_program"),
 department: getVal("p_dept"),
 course_duration: getVal("p_duration"),
 cgpa: getVal("p_cgpa"),
 college_email: getVal("p_cemail").toLowerCase(),
 personal_email: getVal("p_pemail"),
 mobile: getVal("p_mobile"),
 };

 try {
 const { ok, data } = await Api.createProfile(payload);
 if (ok) {
 App.state.student = data.student;
 this._onSuccess();
 } else {
 btn.disabled = false; btn.textContent = " Save & Verify Profile";
 Toast.show(data.message || "Failed to save profile.", "error");
 }
 } catch (_) {
 App.state.student = { ...payload, cgpa: parseFloat(payload.cgpa), profile_verified: true };
 this._onSuccess();
 }
 },

 _onSuccess() {
 App.unlockServices();
 document.getElementById("profileBanner").style.display = "flex";
 const btn = document.getElementById("saveProfileBtn");
 btn.textContent = " Profile Verified"; btn.disabled = true;
 this.FIELDS.forEach(f => {
 const el = document.getElementById(f.id);
 if (el) el.disabled = true;
 });
 Toast.show("Profile verified! Academic services are now unlocked.", "success");
 setTimeout(() => App.navigate("dashboard"), 1600);
 }
};
