#  Student Academic Services Portal

A full-stack web application for managing university academic service requests
at **Manipal University Jaipur (MUJ)**.
Built with **Flask (Python)** backend and **HTML / CSS / Vanilla JS** frontend.

---

##  What's New in v2

| Enhancement | Description |
|---|---|
|  Internship Approval Module | Students can submit internship details for university approval |
|  Admin Panel | Faculty/Admin can approve or reject all applications with remarks |
|  MUJ Email Validation | College email strictly enforced as `name.enrollmentid@muj.manipal.edu` |
|  Internship Email Reminders | Automated email sent to both addresses on internship submission |
|  Admin Dashboard | Live stats — total students, pending, approved, rejected counts |

---

##  Features

| Feature | Description |
|---|---|
|  Mandatory Profile Verification | All services locked until student profile is submitted and validated |
|  LOR Application | Department-filtered faculty selection, purpose, status tracking |
|  Bonafide Certificate | Purpose-driven request with status tracking |
|  Internship Approval | Submit internship details for university approval |
|  Admin Panel | Approve / Reject applications with remarks, view all students |
|  Email Notifications | Non-blocking SMTP reminders to both student email IDs |
|  RESTful API | Clean Flask Blueprint architecture — 5 route groups |
|  MySQL-Ready Store | In-memory store with DAO pattern for easy DB migration |

---

##  Project Structure
```
student-academic-portal/
├── backend/
│   ├── app.py                   ← Flask entry point (v2 — 5 blueprints)
│   ├── config.py                ← App config (SMTP, MUJ email domain, admin creds)
│   ├── models.py                ← Data models — Profile, LOR, Bonafide, Internship
│   ├── pyrightconfig.json       ← Suppresses VS Code import warnings
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── student.py           ← Profile APIs
│   │   ├── lor.py               ← LOR APIs
│   │   ├── bonafide.py          ← Bonafide APIs
│   │   ├── internship.py        ← Internship APIs (NEW in v2)
│   │   └── admin.py             ← Admin Panel APIs (NEW in v2)
│   ├── services/
│   │   ├── email_service.py     ← SMTP email (non-blocking thread)
│   │   └── validation.py        ← Input validators (MUJ email enforced)
│   └── data/
│       └── store.py             ← In-memory store (DAO pattern)
├── frontend/
│   ├── index.html               ← Main student portal UI
│   ├── admin.html               ← Admin Panel UI (NEW in v2)
│   ├── css/
│   │   └── style.css            ← Orange & white theme
│   └── js/
│       ├── api.js               ← HTTP client
│       ├── app.js               ← Navigation, state, dashboard
│       ├── profile.js           ← Profile module (MUJ email validation)
│       ├── lor.js               ← LOR module
│       ├── bonafide.js          ← Bonafide + History modules
│       └── internship.js        ← Internship module (NEW in v2)
└── README.md
```

---

##  Quick Start

### Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional — for email and admin credentials)
cp .env.example .env

# Run the server
python app.py
```

Backend runs at: **http://localhost:5000**

### Student Portal
Double-click `frontend/index.html` to open in your browser.

### Admin Panel
Double-click `frontend/admin.html` — login with `admin` / `admin123`

> **Demo Mode:** If the backend is not running, the frontend automatically
> switches to local in-memory mode so all UI features still work.

---

##  API Endpoints

| Method | Endpoint | Description |
|---|---|---|
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
| POST | `/api/internship/apply` | Submit Internship request *(v2)* |
| GET  | `/api/internship/<app_id>` | Get Internship details *(v2)* |
| POST | `/api/admin/login` | Admin login *(v2)* |
| POST | `/api/admin/logout` | Admin logout *(v2)* |
| GET  | `/api/admin/dashboard` | Admin stats *(v2)* |
| GET  | `/api/admin/applications` | All applications with filters *(v2)* |
| GET  | `/api/admin/students` | All registered students *(v2)* |
| POST | `/api/admin/review` | Approve / Reject application *(v2)* |

---

##  MUJ Email Validation

College email is strictly validated on both frontend and backend:

- **Accepted:** `name.enrollmentid@muj.manipal.edu`
- **Example:** `antriksh.2428010079@muj.manipal.edu`
- **Rejected:** Any other domain (`@gmail.com`, `@manipal.edu`, etc.)

---

##  Email Setup (Optional)

Edit `backend/.env`:
```
SMTP_ENABLED=True
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

For Gmail use an **App Password** — Google Account → Security → App Passwords.

---

##  Admin Panel

Open `frontend/admin.html` and login with:
- **Username:** `admin`
- **Password:** `admin123`

Change credentials in `backend/.env`:
```
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
```

---

##  Future Enhancements

- MySQL integration via SQLAlchemy (DAO layer already structured for this)
- JWT-based student authentication
- Scheduled follow-up email reminders (APScheduler)
- PDF certificate generation (ReportLab)
- Audit log trail

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (Orange & White), Vanilla JS |
| Backend | Python 3.10+, Flask 3.x, Flask-CORS |
| Email | Python smtplib + threading |
| Storage | In-memory (MySQL-ready DAO pattern) |

---

##  License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.