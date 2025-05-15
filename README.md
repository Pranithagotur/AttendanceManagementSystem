# 📲 QRTrack: Attendance Management System

**QRTrack** is a smart Attendance Management System that uses QR codes to simplify and automate attendance tracking. Built with Flask, MySQL, and Twilio, it provides a seamless experience for institutions to manage attendance efficiently.

---

## 🚀 Features

- User Registration with Unique ID
- Update User Information
- QR Code Generation for Attendance Marking
- Real-Time Attendance Logging and Prevention of Duplicate Entries
- Attendance Percentage Calculation and Display
- Responsive Web Interface built with Flask Templates
- Persistent Data Storage using MySQL

---

## 💻 Technologies Used

- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Python (Flask)
- **Database:** MySQL
- **QR Code Generation:** Python `qrcode` library
- **Development Tools:** Visual Studio Code, XAMPP

---

## 📂 Project Structure
/AttendanceManagementSystem
│
├── templates/ # HTML templates
│ ├── Home.html
│ ├── register.html
│ ├── update_user.html
│ ├── generatee_qr.html
│ └── attendance_marked.html
│
├── static/
│ └── qrcodes/ # Generated QR code images
│
├── aclear.py # Main Flask app with routes and logic
├── create_users_table.sql # Database schema and table creation script
├── lib.py # QR code helper functions
├── key.py # Secret key generation script
├── requirements.txt # Python dependencies
├── README.md # This file
└── .gitignore # Files to ignore in git
