import cv2
import numpy as np
from matplotlib import pyplot as plt

def preprocess_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Adaptive Thresholding for better contrast
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Use Morphological Operations to clean noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Display the processed images
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 3, 1), plt.imshow(gray, cmap='gray'), plt.title("Grayscale")
    plt.subplot(1, 3, 2), plt.imshow(thresh, cmap='gray'), plt.title("Thresholded")
    plt.subplot(1, 3, 3), plt.imshow(cleaned, cmap='gray'), plt.title("Denoised")
    plt.show()

    return cleaned

# Preprocess and save the cleaned image
preprocessed_image = preprocess_image("HongKong_ID.png")
cv2.imwrite("preprocessed_id.png", preprocessed_image)




ocr_script.py

import sys
import json
from imgocr import ImgOcr

def extract_text(image_path):
    m = ImgOcr(use_gpu=False, is_efficiency_mode=True)
    result = m.ocr(image_path)
    
    # Convert result to key-value JSON format
    extracted_data = {f"text_{i}": item["text"] for i, item in enumerate(result)}
    
    print(json.dumps(extracted_data))  # Print JSON output

if __name__ == "__main__":
    image_path = sys.argv[1]
    extract_text(image_path)

OcrService.java

package com.example.imgocr.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class OcrService {

    public Map<String, Object> processImage(MultipartFile file) {
        try {
            // Save uploaded file to a temporary location
            File tempFile = File.createTempFile("uploaded_", ".jpg");
            file.transferTo(tempFile);

            // Execute Python script
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "ocr_script.py", tempFile.getAbsolutePath());
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read Python script output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder jsonOutput = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                jsonOutput.append(line);
            }

            // Convert JSON output to Java Map
            ObjectMapper objectMapper = new ObjectMapper();
            Map<String, Object> extractedData = objectMapper.readValue(jsonOutput.toString(), Map.class);

            return extractedData;

        } catch (Exception e) {
            return Map.of("error", "Failed to process image: " + e.getMessage());
        }
    }
}

ImgOcrController.java

package com.example.imgocr.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.imgocr.service.OcrService;
import java.util.Map;

@RestController
@RequestMapping("/api/ocr")
public class ImgOcrController {

    @Autowired
    private OcrService ocrService;

    @PostMapping("/extract")
    public ResponseEntity<Map<String, Object>> extractText(@RequestParam("image") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "No file uploaded"));
        }
        
        Map<String, Object> extractedData = ocrService.processImage(file);
        return ResponseEntity.ok(extractedData);
    }
}



import uuid
import json
from imgocr import ImgOcr

def extract_hk_id_info(ocr_result):
    extracted_data = {
        "documentType": "national_identity_card",
        "issuingCountry": "HKG",
        "documentNumber": None,
        "fullName": None,
        "firstName": None,
        "middleName": None,
        "lastName": None,
        "gender": None,
        "dateOfBirth": None,
        "dateOfExpiry": None,
        "dobSymbol": None,
        "issuingDate": None,
        "personalNumber": None
    }

    # Helper function to clean text
    def clean_text(text):
        return text.strip().replace(" ", "")

    for entry in ocr_result:
        text = entry['text']

        if "PERMANENTIDENTITYCARD" in text or "HONGKONGPERMANENTIDENTITYCARD" in text:
            extracted_data["documentType"] = "national_identity_card"
            extracted_data["issuingCountry"] = "HKG"
        elif text.replace(" ", "").isdigit() and len(text.replace(" ", "")) > 10:
            extracted_data["personalNumber"] = clean_text(text)
        elif "-" in text and len(text.split("-")) == 3:
            if "DBth" in text or "出生日期" in text:
                extracted_data["dateOfBirth"] = text.replace("DBth", "").strip()
            else:
                extracted_data["issuingDate"] = text.strip()
        elif "(" in text and ")" in text:
            extracted_data["documentNumber"] = text.strip()
        elif len(text.split(",")) == 2:
            extracted_data["lastName"], extracted_data["firstName"] = map(str.strip, text.split(","))
            extracted_data["fullName"] = extracted_data["firstName"] + " " + extracted_data["lastName"]
        elif "AZ" in text:
            extracted_data["dobSymbol"] = text.strip()

    # Construct final JSON output
    formatted_output = {
        "documentId": str(uuid.uuid4()),
        "documentClassification": {
            "documentType": extracted_data["documentType"],
            "issuingCountry": extracted_data["issuingCountry"],
            "version": "2018"
        },
        "extractedOcrData": extracted_data
    }

    return json.dumps(formatted_output, indent=4, ensure_ascii=False)

# Initialize OCR Model
m = ImgOcr(use_gpu=False, is_efficiency_mode=True)

# Run OCR
ocr_results = m.ocr("HongKong_ID.png")

# Process OCR results
formatted_json = extract_hk_id_info(ocr_results)

# Print final JSON output
print(formatted_json)

