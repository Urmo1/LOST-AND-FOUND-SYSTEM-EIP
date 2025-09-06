from flask import Flask, render_template, request
import qrcode
import os
import socket
import csv
import uuid

app = Flask(__name__)

# ----------------------------
# Automatically get local IP
# ----------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()

# ----------------------------
# Prepare folders and CSV file
# ----------------------------
qr_folder = os.path.join("static", "qrcodes")
os.makedirs(qr_folder, exist_ok=True)

csv_file = "students.csv"
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "grade", "contact"])

# ----------------------------
# Helper function to read student data
# ----------------------------
def get_student_data(student_id):
    try:
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["student_id"] == student_id:
                    return {
                        "name": row["name"],
                        "grade": row["grade"],
                        "contact": row["contact"]
                    }
    except FileNotFoundError:
        return None
    return None

# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        grade = request.form["grade"]
        contact = request.form["contact"]

        # Unique student ID
        student_id = str(uuid.uuid4())

        # Save data to CSV
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([student_id, name, grade, contact])

        # Generate QR code
        profile_url = f"http://{LOCAL_IP}:5000/student/{student_id}"
        filename = f"{name}_{grade}_{student_id}.png".replace(" ", "_")
        filepath = os.path.join(qr_folder, filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(profile_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)

        # -----------------------------
        # No printing logic included
        # -----------------------------

        return render_template("result.html", filename=filename, name=name, grade=grade)

    return render_template("index.html")

@app.route("/student/<student_id>")
def student_page(student_id):
    data = get_student_data(student_id)
    if data:
        return render_template("student.html", data=data)
    else:
        return "Student not found!", 404

# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
