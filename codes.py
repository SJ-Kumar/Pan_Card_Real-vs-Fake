Frontend
App.js

import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import OcrUpload from './OcrUpload';

const App = () => {
    return (
        <div>
            <OcrUpload />
        </div>
    );
};

export default App;

OcrUpload.js
import React, { useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, Button, Card, Form, Spinner, Alert } from 'react-bootstrap';

const OcrUpload = () => {
    const [image, setImage] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [ocrResult, setOcrResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setImage(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!image) return;

        setIsProcessing(true);
        setError(null);
        setOcrResult(null);

        const formData = new FormData();
        formData.append("file", image);

        try {
            const response = await axios.post('http://localhost:8080/api/ocr/process', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setIsProcessing(false);
            setOcrResult(response.data);
        } catch (error) {
            setIsProcessing(false);
            setError("Error processing the image. Please try again.");
        }
    };

    return (
        <Container className="mt-4">
            <Row className="justify-content-center">
                <Col md={6}>
                    <Card>
                        <Card.Body>
                            <h3 className="text-center">Upload Your Image for OCR</h3>
                            <Form>
                                <Form.Group controlId="fileUpload">
                                    <Form.Label>Choose Image</Form.Label>
                                    <Form.Control type="file" onChange={handleFileChange} />
                                </Form.Group>
                                <Button
                                    variant="primary"
                                    onClick={handleUpload}
                                    disabled={isProcessing}
                                >
                                    {isProcessing ? (
                                        <Spinner animation="border" size="sm" />
                                    ) : (
                                        "Upload and Process"
                                    )}
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {isProcessing && (
                <Alert variant="info" className="mt-4 text-center">
                    Processing your image, please wait...
                </Alert>
            )}

            {error && (
                <Alert variant="danger" className="mt-4 text-center">
                    {error}
                </Alert>
            )}

            {ocrResult && (
                <Card className="mt-4">
                    <Card.Body>
                        <h4>OCR Result:</h4>
                        <pre>{JSON.stringify(ocrResult, null, 2)}</pre>
                    </Card.Body>
                </Card>
            )}
        </Container>
    );
};

export default OcrUpload;





package com.hk.ocr.controller;

import com.hk.ocr.service.OcrService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/api/ocr")
public class OcrController {

    private final OcrService ocrService;

    public OcrController(OcrService ocrService) {
        this.ocrService = ocrService;
    }

    @PostMapping("/process")
    public Mono<ResponseEntity<Map<String, Object>>> processOcr(@RequestPart("file") Mono<MultipartFile> fileMono) {
        return fileMono.flatMap(file -> ocrService.processImage(file)
                .map(ResponseEntity::ok)
                .onErrorResume(e -> Mono.just(ResponseEntity.badRequest()
                        .body(Map.of("error", "Failed to process image"))))
        );
    }
}



package com.hk.ocr.service;

import com.hk.ocr.utils.FileStorageUtil;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.io.File;
import java.util.Map;

@Service
public class OcrService {

    private final PythonOcrClient pythonOcrClient;

    public OcrService(PythonOcrClient pythonOcrClient) {
        this.pythonOcrClient = pythonOcrClient;
    }

    public Mono<Map<String, Object>> processImage(MultipartFile file) {
        return Mono.fromCallable(() -> {
            File tempFile = FileStorageUtil.saveFile(file);
            Map<String, Object> extractedData = pythonOcrClient.runOcrScript(tempFile);
            tempFile.delete();
            return extractedData;
        });
    }
}



package com.hk.ocr.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

@Service
public class PythonOcrClient {

    @Value("${ocr.python.executable}")
    private String pythonExecutable;

    @Value("${ocr.python.script}")
    private String pythonScriptPath;

    public Mono<Map<String, Object>> runOcrScript(File imageFile) {
        return Mono.fromCallable(() -> {
            Map<String, Object> result = new HashMap<>();
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
                result.put("ocr_data", output.toString());

            } catch (Exception e) {
                result.put("error", "Failed to execute OCR script");
            }
            return result;
        });
    }
}



package com.hk.ocr.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

@Configuration
public class CorsConfig {

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("*");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);

        return new CorsWebFilter(source);
    }
}


spring.application.name=ocr-service
server.port=8080

# Set file upload limits
spring.servlet.multipart.max-file-size=5MB
spring.servlet.multipart.max-request-size=5MB

# Path to Python script
ocr.python.script=python/ocr_processor.py
ocr.python.executable=python


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
@PostMapping("/process")
public ResponseEntity<Map<String, Object>> processOcr(@RequestParam("file") MultipartFile file) {
    Logger logger = LoggerFactory.getLogger(OcrController.class);

    if (file.isEmpty()) {
        logger.error("Received an empty file.");
        return ResponseEntity.badRequest().body(Map.of("error", "No file uploaded"));
    }

    logger.info("Received file: " + file.getOriginalFilename() + " (" + file.getSize() + " bytes)");

    try {
        Map<String, Object> extractedData = ocrService.processImage(file);
        return ResponseEntity.ok(extractedData);
    } catch (IOException e) {
        logger.error("Failed to process image", e);
        return ResponseEntity.badRequest().body(Map.of("error", "Failed to process image"));
    }

}


package com.hk.ocr.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.Arrays;

@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        
        config.setAllowCredentials(true); // Allow credentials (cookies, authentication)
        config.setAllowedOrigins(Arrays.asList("*")); // Allow all origins
        config.setAllowedHeaders(Arrays.asList("*")); // Allow all headers
        config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS")); // Allow all methods
        config.setExposedHeaders(Arrays.asList("*")); // Expose all response headers

        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}