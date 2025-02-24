import os
import base64
import cv2
import numpy as np
from deepface import DeepFace

FACE_DATA_FOLDER = "face_data"

def save_uploaded_image(image_data, filename=None):
    try:
        if not image_data:
            print("Error: No image data provided.")
            return None

        if isinstance(image_data, str) and image_data.startswith("data:image"):
            image_bytes = base64.b64decode(image_data.split(",")[1])
            if not filename:
                filename = "temp_image.jpg"
            image_path = os.path.join(FACE_DATA_FOLDER, filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"Captured image saved successfully: {image_path}")
            return image_path

        elif hasattr(image_data, "filename"):  
            if not filename:
                filename = image_data.filename
            image_path = os.path.join(FACE_DATA_FOLDER, filename)
            image_data.save(image_path)

            print(f" Uploaded image saved successfully: {image_path}")
            return image_path  

        else:
            print(" Error: Invalid image format provided.")
            return None

    except Exception as e:
        print(f" Error saving uploaded image: {e}")
        return None


def recognize_employee(image_data):

    temp_image_path = save_uploaded_image(image_data)

    if not temp_image_path:
        print("Error: No temporary image created for recognition.")
        return None

    recognized_employee = None  
    deepface_models = ["Facenet", "ArcFace"]

    for filename in os.listdir(FACE_DATA_FOLDER):
        stored_image_path = os.path.join(FACE_DATA_FOLDER, filename)

        if filename == "temp_image.jpg":
            continue  

        try:
            match_results = {model: False for model in deepface_models}  # Store verification results

            for model in deepface_models:
                result = DeepFace.verify(
                    img1_path=temp_image_path,
                    img2_path=stored_image_path,
                    model_name=model,
                    enforce_detection=True  
                )

                match_results[model] = result["verified"]  

                print(f"[{model}] Comparing with {stored_image_path}: Match = {result['verified']}")  

            # **Require both models to return True before recognizing**
            if all(match_results.values()):
                recognized_employee = os.path.splitext(filename)[0]  
                break  

        except Exception as e:
            print(f"Error recognizing face with {stored_image_path}: {e}")

    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)

    if recognized_employee:
        print(f"Employee Recognized: {recognized_employee}")
        return recognized_employee

    print("No matching face found.") 
    return None

