import csv
import os
import base64
import re
from backend.face_recognition import save_uploaded_image

DATA_FILE = "employees.csv"
FACE_DATA_FOLDER = "face_data"

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)

def save_employee_data(employee_data, captured_image=None, uploaded_file=None):
    try:
        email = employee_data["Email"]
        filename = f"{email}.jpg"  
        image_path = os.path.join(FACE_DATA_FOLDER, filename)

        saved_image_path = None  

        if captured_image:  
            saved_image_path = save_uploaded_image(captured_image, filename)

        elif uploaded_file:  
            saved_image_path = save_uploaded_image(uploaded_file, filename)

        if saved_image_path:
            print(f"Image saved successfully as: {saved_image_path}")
        else:
            print("No image was provided or saved.")

        file_exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, "a", newline="") as file:
            fieldnames = employee_data.keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(employee_data)

        print(f" Employee data saved successfully: {email}")

    except Exception as e:
        print(f" Error saving employee data: {e}")
