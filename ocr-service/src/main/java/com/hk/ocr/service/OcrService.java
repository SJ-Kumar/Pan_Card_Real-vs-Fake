package com.hk.ocr.service;

import com.hk.ocr.utils.FileStorageUtil;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.util.Map;

@Service
public class OcrService {
    private final PythonOcrClient pythonOcrClient;

    public OcrService(PythonOcrClient pythonOcrClient) {
        this.pythonOcrClient = pythonOcrClient;
    }

    public Map<String, Object> processImage(MultipartFile file) throws IOException {
        // Save the file temporarily
        File tempFile = FileStorageUtil.saveFile(file);

        // Call the OCR script and get the extracted data
        Map<String, Object> extractedData = pythonOcrClient.runOcrScript(tempFile);

        // Delete the temporary file after processing
        tempFile.delete();

        return extractedData;
    }
}
