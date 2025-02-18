import cv2
import numpy as np
import re
import json
from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance
from imgocr import ImgOcr

# Initialize Flask app
app = Flask(__name__)

# Initialize OCR Model
m = ImgOcr(use_gpu=False, is_efficiency_mode=True)

def enhance_image(image):
    """Enhance image contrast and sharpness to improve OCR accuracy."""
    image = np.array(image)
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

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """API endpoint to receive an image, process OCR, and return JSON response."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    image = Image.open(image)

    # Enhance image
    enhanced_image = enhance_image(image)

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

    return jsonify(final_output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)