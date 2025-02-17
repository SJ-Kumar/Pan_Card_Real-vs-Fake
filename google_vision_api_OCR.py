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