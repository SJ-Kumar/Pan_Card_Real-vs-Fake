package com.hk.ocr.controller;

import com.hk.ocr.service.OcrService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/ocr")
public class OcrController {
    private final OcrService ocrService;

    public OcrController(OcrService ocrService) {
        this.ocrService = ocrService;
    }

    @PostMapping("/process")
    public ResponseEntity<Map<String, Object>> processOcr(@RequestParam("file") MultipartFile file) {
        try {
            Map<String, Object> extractedData = ocrService.processImage(file);
            return ResponseEntity.ok(extractedData);
        } catch (IOException e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Failed to process image"));
        }
    }
}
