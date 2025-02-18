package com.hk.ocr.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.util.Map;

@Service
public class PythonOcrClient {
    @Value("${ocr.python.executable}")
    private String pythonExecutable;

    @Value("${ocr.python.script}")
    private String pythonScriptPath;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public Map<String, Object> runOcrScript(File imageFile) {
        try {
            ProcessBuilder pb = new ProcessBuilder(pythonExecutable, pythonScriptPath, imageFile.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            process.waitFor();

            // Call the function to extract the face image
            String extractedFacePath = extractFace(imageFile);

            // Convert the OCR result from the Python script to a Java Map
            Map<String, Object> ocrResult = objectMapper.readValue(output.toString(), Map.class);

            // Add the face extraction path to the OCR result if needed (you mentioned no need to return this path in response)
            return ocrResult;

        } catch (Exception e) {
            return Map.of("error", "Failed to execute OCR script: " + e.getMessage());
        }
    }

    // Method to call the Python face extraction script
 // Method to call the Python face extraction script
    private String extractFace(File imageFile) {
        try {
            String outputFolderPath = "extracted_faces";
            File outputFolder = new File(outputFolderPath);
            if (!outputFolder.exists()) {
                outputFolder.mkdir(); // Create folder if it doesn't exist
            }

            // Get the list of files already present in the folder
            File[] existingFiles = outputFolder.listFiles((dir, name) -> name.startsWith("extracted_face") && name.endsWith(".png"));

            // Generate the next incremental file name (e.g., extracted_face_1.png)
            String outputPath;
            if (existingFiles != null && existingFiles.length > 0) {
                int nextIndex = existingFiles.length + 1; // Increment the index based on existing files
                outputPath = outputFolderPath + "/extracted_face_" + nextIndex + ".png";
            } else {
                outputPath = outputFolderPath + "/extracted_face_1.png"; // First file
            }

            // Call Python script for face extraction
            ProcessBuilder pb = new ProcessBuilder(pythonExecutable, "python/extract_face.py", imageFile.getAbsolutePath(), outputPath);
            pb.redirectErrorStream(true);
            Process process = pb.start();

            process.waitFor();
            return outputPath; // Return the path where the face image is saved
        } catch (Exception e) {
            e.printStackTrace(); // Log the exception for debugging
            return null;
        }
    }

}
