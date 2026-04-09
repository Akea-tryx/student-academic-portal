/**
 * api.js — API Client Module
 * All HTTP communication with the Flask backend.
 */

const API_BASE = "http://localhost:5000/api";

const Api = {
 async _request(method, path, body = null) {
 const opts = {
 method,
 headers: { "Content-Type": "application/json" },
 };
 if (body) opts.body = JSON.stringify(body);
 const res = await fetch(`${API_BASE}${path}`, opts);
 const data = await res.json();
 return { ok: res.ok, status: res.status, data };
 },

 // Student Profile 
 createProfile: (payload) => Api._request("POST", "/student/profile", payload),
 getProfile: (regId) => Api._request("GET", `/student/profile/${regId}`),
 getFaculty: (dept) => Api._request("GET", `/student/faculty/${dept}`),
 getApplications: (regId) => Api._request("GET", `/student/applications/${regId}`),
 getReferenceData: () => Api._request("GET", "/student/reference"),

 // LOR 
 applyLOR: (payload) => Api._request("POST", "/lor/apply", payload),
 getLOR: (appId) => Api._request("GET", `/lor/${appId}`),

 // Bonafide 
 applyBonafide: (payload) => Api._request("POST", "/bonafide/apply", payload),
 getBonafide: (appId) => Api._request("GET", `/bonafide/${appId}`),
};

 // Internship 
 applyInternship: (payload) => Api._request("POST", "/internship/apply", payload),
 getInternship: (appId) => Api._request("GET", `/internship/${appId}`),

 // Admin 
 adminLogin: (payload) => Api._request("POST", "/admin/login", payload),
 adminLogout: () => Api._request("POST", "/admin/logout"),
 adminDashboard: () => Api._request("GET", "/admin/dashboard"),
 adminApps: (params) => Api._request("GET", `/admin/applications${params || ""}`),
 adminStudents: () => Api._request("GET", "/admin/students"),
 adminReview: (payload) => Api._request("POST", "/admin/review", payload),
