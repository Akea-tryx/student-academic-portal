# 🎓 Student Academic Services Portal

A full-stack web application for managing university academic service requests.
Built with **Flask (Python)** backend and **HTML / CSS / Vanilla JS** frontend.

---

## 📁 Project Structure

```
student-academic-portal/
├── backend/
│   ├── app.py                  ← Flask entry point
│   ├── config.py               ← App config (SMTP, faculty, etc.)
│   ├── models.py               ← Data models (MySQL-ready)
│   ├── pyrightconfig.json      ← Suppresses VS Code import warnings
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── student.py          ← Profile APIs
│   │   ├── lor.py              ← LOR APIs
│   │   └── bonafide.py         ← Bonafide APIs
│   ├── services/
│   │   ├── email_service.py    ← SMTP email (non-blocking thread)
│   │   └── validation.py       ← Input validators
│   └── data/
│       └── store.py            ← In-memory store (DAO pattern)
├── frontend/
│   ├── index.html              ← Main portal UI
│   ├── css/
│   │   └── style.css           ← Orange & white theme
│   └── js/
│       ├── api.js              ← HTTP client
│       ├── app.js              ← Navigation, state, dashboard
│       ├── profile.js          ← Profile module
│       ├── lor.js              ← LOR module
│       └── bonafide.js         ← Bonafide + History modules
└── README.md
```

---

## 🚀 Quick Start

### Step 1 — Set up the backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure email
cp .env.example .env
# Edit .env and set SMTP_ENABLED=True with your credentials

# Run the server
python app.py
```

Backend runs at: **http://localhost:5000**

### Step 2 — Open the frontend

Simply **double-click** `frontend/index.html` to open in your browser.

> The frontend has a built-in **demo mode** — if the backend is not running,
> all features still work using local in-memory state.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/health` | Health check |
| POST | `/api/student/profile` | Create student profile |
| GET  | `/api/student/profile/<reg_id>` | Get student profile |
| GET  | `/api/student/faculty/<dept>` | Dept-filtered faculty list |
| GET  | `/api/student/applications/<reg_id>` | All student applications |
| GET  | `/api/student/reference` | All dropdown/reference data |
| POST | `/api/lor/apply` | Submit LOR application |
| GET  | `/api/lor/<app_id>` | Get LOR details |
| POST | `/api/bonafide/apply` | Submit Bonafide request |
| GET  | `/api/bonafide/<app_id>` | Get Bonafide details |

---

## 📧 Email Setup (Optional)

Edit `backend/.env`:

```
SMTP_ENABLED=True
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

For Gmail, use an **App Password** (not your regular password).
Go to: Google Account → Security → 2-Step Verification → App Passwords

---

## 🛣️ Future Enhancements

- MySQL integration via SQLAlchemy (DAO layer already structured for this)
- Admin panel for faculty to approve / reject applications
- JWT-based student authentication
- Scheduled follow-up email reminders (APScheduler)
- Internship approval module
- PDF certificate generation
- Audit log trail

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3 (Orange & White), Vanilla JS |
| Backend | Python 3.10+, Flask 3.x, Flask-CORS |
| Email | Python smtplib + threading |
| Storage | In-memory (MySQL-ready DAO pattern) |
