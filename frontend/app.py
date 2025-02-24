from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_from_directory
import csv
import os
import base64
import cv2
import numpy as np
import re
import requests
from datetime import datetime
from deepface import DeepFace
from backend.register import save_employee_data
from backend.face_recognition import recognize_employee

app = Flask(__name__)
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True  # Make sure debug mode is enabled
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.secret_key = os.urandom(24)

EMPLOYEE_CSV = "attendance.csv"
FACE_DATA_FOLDER = "face_data"
ELEVEN_LABS_API_KEY = "sk_a40b0352886320729512b1b7821edaf0004859c98ae2d96d" 

if not os.path.exists(EMPLOYEE_CSV):
    with open(EMPLOYEE_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Employee ID", "Action", "Timestamp"])

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)

if not os.path.exists("frontend/static"):
    os.makedirs("frontend/static")

def sanitize_filename(email):
    return re.sub(r'[^\w\-_]', '_', email) + ".jpg"


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


def speak_message(text):
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/H6QPv2pQZDcGqLwDTIJQ"
        headers = {
            "xi-api-key": ELEVEN_LABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "stability": 0.5,
            "similarity_boost": 0.7,
            "style": 0.8,
            "use_speaker_boost": True
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            speech_path = "frontend/static/speech.mp3"

            os.makedirs(os.path.dirname(speech_path), exist_ok=True)

            with open(speech_path, "wb") as f:
                f.write(response.content)

            print(f"Speech generated and saved at: {speech_path}")
            return url_for('static', filename='speech.mp3')  

        else:
            print(" Error generating speech:", response.json())
            return None
    except Exception as e:
        print("Eleven Labs API Error:", e)
        return None

@app.route("/employee_check", methods=["GET", "POST"])
def employee_check():
    if request.method == "POST":
        try:
            if request.content_type != "application/json":
                return jsonify({"message": "Unsupported Media Type. Use 'application/json'"}), 415

            data = request.get_json()
            if not data:
                return jsonify({"message": "No JSON data received!"}), 400

            image_data = data.get("captured_image")
            if not image_data:
                return jsonify({"message": "No image provided!"}), 400

            print("Received Image Data Successfully")  

            employee_id = recognize_employee(image_data)

            if employee_id:
                first_name = employee_id.split(" ")[0]  
                last_action = get_last_action(employee_id)
                action = "checkout" if last_action == "checkin" else "checkin"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(EMPLOYEE_CSV, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([employee_id, action, timestamp])

                if action == "checkin":
                    speech_text = f"Hey thanks for checking in! Have a nice day!"
                else:
                    speech_text = f"Thanks for checking out!, See you soon"

                speech_url = speak_message(speech_text)

                return jsonify({"message": f"Thanks {employee_id}, you have {action} at {timestamp}", "speech_url": speech_url})

            return jsonify({"message": "Face not recognized!"})

        except Exception as e:
            print("Error in Employee Check:", e)
            return jsonify({"message": "Internal Server Error"}), 500

    return render_template("employee_check.html")


@app.route("/", methods=["GET", "POST"])
def login():
    error = False  

    if request.method == "POST":
        employee_id = request.form["employee_id"]
        password = request.form["password"]

        if employee_id == "hr@softshala" and password == "softshala":
            session["role"] = "hr"
            return redirect(url_for("dashboard"))
        
        error = True  

    return render_template("login.html", error=error)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "role" not in session or session["role"] != "hr":
        return redirect(url_for("login"))

    if request.method == "POST":
        employee_data = {
            "First Name": request.form["first_name"],
            "Last Name": request.form["last_name"],
            "Gender": request.form["gender"],
            "Contact Number": request.form["contact"],
            "Birthday": request.form["birth_date"],
            "Father Name": request.form["father_name"],
            "Mother Name": request.form["mother_name"],
            "Age": request.form["age"],
            "Email": request.form["email"],
            "Permanent Address": request.form["address"],
            "Blood Group": request.form["blood_group"],
            "Joining Date": request.form["joining_date"],
            "Aadhar Card": request.form["aadhar"],
            "PAN Card": request.form["pan"],
        }

        image_data = request.form.get("captured_image", "")  # Captured Image (Base64)
        uploaded_file = request.files.get("uploaded_image")  # Uploaded File

        if not image_data and not uploaded_file:
            return jsonify({"message": "Error: Please provide an image (capture or upload)."}), 400

        save_employee_data(employee_data, image_data, uploaded_file)

        return jsonify({"message": "Employee registered successfully!"}), 200

    return render_template("dashboard.html")



def save_base64_image(image_data, file_path):
    try:
        image_data = image_data.split(",")[1]  
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        cv2.imwrite(file_path, image)
        print(f"Image saved successfully: {file_path}")

    except Exception as e:
        print(f"Error Saving Image: {e}")


def get_last_action(employee_id):
    try:
        with open(EMPLOYEE_CSV, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in reversed(rows):
                if row[0] == employee_id:
                    return row[1] 
    except FileNotFoundError:
        return None
    return None


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)