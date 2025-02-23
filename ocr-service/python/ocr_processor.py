from flask import Flask, request, jsonify
import cv2
import numpy as np
import re
import tempfile
import json
from PIL import Image, ImageEnhance
from imgocr import ImgOcr
import os

# Initialize Flask App
app = Flask(__name__)

# Initialize OCR Model
m = ImgOcr(use_gpu=False, is_efficiency_mode=True)

def enhance_image(image_path):
    """Enhance image contrast and sharpness to improve OCR accuracy."""
    image = cv2.imread(image_path)
    pil_image = Image.fromarray(image)
    
    enhancer = ImageEnhance.Contrast(pil_image)
    image = enhancer.enhance(2)
    
    image = np.array(image)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    image = cv2.filter2D(image, -1, kernel)
    
    return Image.fromarray(image)

def extract_personal_number(ocr_result):
    """Extract personal number in 'XXXX XXXX XXXX' format."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    ocr_text_cleaned = re.sub(r"\.\d", "", ocr_text)
    match = re.search(r"(\d{4})[\s]?(\d{4})[\s]?(\d{4})", ocr_text_cleaned)
    return f"{match.group(1)} {match.group(2)} {match.group(3)}" if match else None

def clean_ocr_response(ocr_result):
    """Extract and clean Chinese full name."""
    unwanted_labels = ["Date of Birth", "DateofBirth", "Date of Issue", "DateofIssue", "出生日期", "签发日期", "Date", "Issue", "SAMPLE"]
    cleaned_text = [i['text'] for i in ocr_result if not any(label in i['text'] for label in unwanted_labels)]
    chinese_text = [text for text in cleaned_text if re.search('[\u4e00-\u9fff]', text)]
    return min(chinese_text, key=len, default=None)

def extract_document_number(ocr_result):
    """Extract document number (e.g., 'A123456')"""
    pattern = r"[A-Za-z][0-9]{6}"
    last_text = ocr_result[-1]['text'].strip()
    return last_text if re.match(pattern, last_text) else None

def extract_date_of_birth(ocr_result):
    """Extract date of birth in 'dd-mm-yyyy' format."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    match = re.search(r"(\d{2}-\d{2}-\d{4})", ocr_text)
    return match.group(1) if match else None

def extract_gender(ocr_result, date_of_birth):
    """Extract gender based on the text following the date of birth."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    position = ocr_text.find(date_of_birth)
    if position != -1:
        following_text = ocr_text[position + len(date_of_birth):].strip()
        if re.search(r"男|M", following_text):
            return "Male"
        elif re.search(r"女|F", following_text):
            return "Female"
    return None

def extract_dob_symbol(ocr_result):
    """Extract dobSymbol like '***XX'."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    match = re.search(r"\*\*\*([A-Za-z]{2})", ocr_text)
    return match.group(0) if match else None

def extract_issuing_date(ocr_result):
    """Extract issuing date in (MM-YY) format."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    match = re.search(r"\d{2}-\d{2}", ocr_text)
    return match.group(0)[1:-1] if match else None

def extract_english_name(ocr_result):
    """Extract English full name."""
    ocr_text = " ".join([i['text'] for i in ocr_result])
    ocr_text = ocr_text.replace("AMPLE SAMPLE", "").replace("SAMPLE", "").strip()
    match = re.search(r"([A-Za-z]+),([A-Za-z]+(?:\s[A-Za-z]+)*)", ocr_text)
    if match:
        surname, given_name = match.group(1).strip(), match.group(2).strip()
        return {
            "englishFullName": f"{surname},{given_name}",
            "englishGivenName": f"{surname},{given_name}",
            "firstName": given_name,
            "englishSurname": surname
        }
    return {"englishFullName": None, "englishGivenName": None, "firstName": None, "englishSurname": None}

def extract_chinese_surname(chinese_full_name):
    """Extract the first character of Chinese full name as surname."""
    return chinese_full_name[0] if chinese_full_name else None

def extract_face(image_path):
    """Extract face from image and save it."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

    if len(faces) == 0:
        return None  # No face found

    # Use first detected face
    (x, y, w, h) = faces[0]
    face = image[y:y+h, x:x+w]

    # Create output directory if not exists
    output_folder = "extracted_faces"
    os.makedirs(output_folder, exist_ok=True)

    # Get the highest existing face number
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("extracted_face_") and f.endswith(".png")]
    existing_numbers = [int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()]
    
    next_index = max(existing_numbers) + 1 if existing_numbers else 1
    output_path = os.path.join(output_folder, f"extracted_face_{next_index}.png")

    # Save the extracted face
    cv2.imwrite(output_path, face)

    return output_path  # Return the new file path

def process_image(image_path):
    """Process image and extract OCR data."""
    try:
        # Enhance image before OCR
        enhanced_image = enhance_image(image_path)

        # Perform OCR
        ocr_result = m.ocr(enhanced_image)

        # Extract fields
        document_number = extract_document_number(ocr_result)
        chinese_full_name = clean_ocr_response(ocr_result)
        personal_number = extract_personal_number(ocr_result)
        dob = extract_date_of_birth(ocr_result)
        gender = extract_gender(ocr_result, dob)
        dob_symbol = extract_dob_symbol(ocr_result)
        issuing_date = extract_issuing_date(ocr_result)
        english_name = extract_english_name(ocr_result)
        chinese_surname = extract_chinese_surname(chinese_full_name)
        
        # Extract face
        face_path = extract_face(image_path)

        # Build JSON response
        final_output = {
            "documentType": "national_identity_card",
            "issuingCountry": "HKG",
            "extractedOcrData": {
                "documentNumber": document_number,
                "chineseFullName": chinese_full_name,
                "chineseGivenName": chinese_full_name,
                "englishFullName": english_name.get("englishFullName"),
                "englishGivenName": english_name.get("englishGivenName"),
                "firstName": english_name.get("firstName"),
                "englishSurname": english_name.get("englishSurname"),
                "chineseSurname": chinese_surname,
                "gender": gender,
                "dateOfBirth": dob,
                "dateOfExpiry": None,
                "dobSymbol": dob_symbol,
                "issuingDate": issuing_date,
                "personalNumber": personal_number
            }
        }

        # Return as JSON string
        return json.dumps(final_output)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route('/process', methods=['POST'])
def ocr_process():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    # Use a system-independent temp directory
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        file.save(temp_path)  # Save uploaded file
        
        # Call your OCR processing function
        ocr_result = process_image(temp_path)

        os.remove(temp_path)  # Clean up the temporary file after processing

        # Ensure proper JSON response
        return jsonify(json.loads(ocr_result))

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
