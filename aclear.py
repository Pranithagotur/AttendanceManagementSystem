from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import qrcode
import MySQLdb.cursors
from io import BytesIO
import base64
from MySQLdb.cursors import DictCursor
import os
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)

# Database Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pranitha@6244'
app.config['MYSQL_DB'] = 'user_registration'
mysql = MySQL(app)

# Twilio Config (replace with your own credentials)
TWILIO_ACCOUNT_SID = 'your_twilio_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

QR_FOLDER = os.path.join('static', 'qrcodes')
os.makedirs(QR_FOLDER, exist_ok=True)

# Home Page with Buttons
@app.route('/')
def home():
    return render_template('Home.html')  # Should include the 4 buttons

# Register User
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    registration_id = None

    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        email = request.form['email']
        contact = request.form['contact']
        state = request.form['state']
        country = request.form['country']
        year = request.form['year_of_study']

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            message = "❌ Email already registered."
        else:
            # Get the next registration ID
            cur.execute("SELECT MAX(CAST(registration_id AS UNSIGNED)) FROM users")
            max_id = cur.fetchone()[0]
            registration_id = 1 if max_id is None else max_id + 1

            # Insert the user
            cur.execute("""
                INSERT INTO users (name, gender, email, phone, state, country, year_of_study, registration_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, gender, email, contact, state, country, year, str(registration_id)))

            mysql.connection.commit()
            message = f"✅ Registered successfully! Your Registration ID is {registration_id}"
        cur.close()

    return render_template('register.html', message=message)
# Update User
@app.route('/update', methods=['GET', 'POST'])
def update_user():
    message = None
    if request.method == 'POST':
        user_id = request.form['id']
        name = request.form['name']
        contact = request.form['contact']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET name=%s, contact=%s WHERE id=%s", (name, contact, user_id))
        mysql.connection.commit()
        cur.close()
        message = "✅ User updated successfully!"
    return render_template('update_user.html', message=message)

# Generate QR for Attendance
from datetime import date
@app.route('/qr-attendance', methods=['GET', 'POST'])
def qr_attendance():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    qr_code_base64 = None
    generated_user = None
    download_link = None

    if request.method == 'POST':
        user_id = int(request.form['user_id'])  # Ensure it's an integer
        # Fetch user
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if user:
            today = date.today()

            # Check if attendance already exists
            cur.execute("SELECT * FROM attendance WHERE user_id = %s AND date = %s", (user_id, today))
            existing = cur.fetchone()

            if not existing:
                # Insert into attendance table
                cur.execute(
                    "INSERT INTO attendance (user_id, date, status) VALUES (%s, %s, %s)",
                    (user_id, today, 'Present')
                )

                # ✅ Update user attendance column to "Present"
                cur.execute("UPDATE users SET attendance = 'Present' WHERE id = %s", (int(user_id),))

                mysql.connection.commit()

            # Generate QR code
            data = f"Name: {user['name']}\nEmail: {user['email']}\nID: {user['id']}"
            qr_img = qrcode.make(data)

            filename = f"user_{user['id']}.png"
            qr_path = os.path.join(QR_FOLDER, filename)
            qr_img.save(qr_path)

            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            download_link = url_for('static', filename=f'qrcodes/{filename}')
            generated_user = user

    # ✅ Always fetch updated users list
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()

    return render_template(
        'generatee_qr.html',
        users=users,
        qr_code=qr_code_base64,
        generated_user=generated_user,
        download_link=download_link
    )
# Mark Attendance + Send SMS
@app.route('/mark_attendance/<int:user_id>')
def mark_attendance(user_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO attendance (user_id) VALUES (%s)", (user_id,))
    mysql.connection.commit()

    # Send SMS
    cur.execute("SELECT contact, name FROM users WHERE id = %s", (user_id,))
    result = cur.fetchone()
    if result:
        contact, name = result
        try:
            client.messages.create(
                body=f"Hello {name}, your attendance was marked successfully ✅.",
                from_=TWILIO_PHONE_NUMBER,
                to=contact
            )
        except Exception as e:
            print("❌ Error sending SMS:", e)

    cur.close()
    return f"✅ Attendance marked for user ID: {user_id}"



# Attendance Percentage
@app.route('/attendance-percentage', methods=['GET'])
def attendance_percentage():
    cur = mysql.connection.cursor()
    
    # Get all users
    cur.execute("SELECT id, name FROM users")
    users = cur.fetchall()

    user_data = []

    # Total number of sessions (can also be dynamically counted if needed)
    cur.execute("SELECT COUNT(DISTINCT date) FROM attendance")
    total_sessions = cur.fetchone()[0] or 1  # Avoid division by zero

    for user in users:
        user_id, name = user
        # Count attendance for each user
        cur.execute("SELECT COUNT(*) FROM attendance WHERE user_id = %s", (user_id,))
        attended = cur.fetchone()[0]
        
        percentage = round((attended / total_sessions) * 100, 2) if total_sessions else 0

        user_data.append({
            'id': user_id,
            'name': name,
            'attended': attended,
            'percentage': percentage
        })

    cur.close()
    return render_template('attendance_marked.html', user_data=user_data)


if __name__ == "__main__":
    app.run(debug=True)
