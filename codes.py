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




import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.server.ServerRequest;
import org.springframework.web.reactive.function.server.ServerResponse;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;
import com.hk.ocr.service.OcrService;
import org.springframework.http.codec.multipart.FilePart;

import java.util.Map;

@RestController
@RequestMapping("/api/ocr")
public class OcrController {

    private final OcrService ocrService;

    public OcrController(OcrService ocrService) {
        this.ocrService = ocrService;
    }

    @PostMapping(value = "/process", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Mono<ResponseEntity<Map<String, Object>>> processOcr(@RequestPart("file") Mono<FilePart> filePartMono) {
        return filePartMono
                .flatMap(filePart -> ocrService.processImage(filePart))
                .map(ResponseEntity::ok)
                .onErrorResume(e -> Mono.just(ResponseEntity.badRequest().body(Map.of("error", "Failed to process image"))));
    }
}


import org.springframework.stereotype.Service;
import org.springframework.http.codec.multipart.FilePart;
import reactor.core.publisher.Mono;

import java.io.File;
import java.io.IOException;
import java.util.Map;

@Service
public class OcrService {

    private final PythonOcrClient pythonOcrClient;

    public OcrService(PythonOcrClient pythonOcrClient) {
        this.pythonOcrClient = pythonOcrClient;
    }

    public Mono<Map<String, Object>> processImage(FilePart filePart) {
        try {
            File tempFile = File.createTempFile("upload_", ".jpg");

            return filePart.transferTo(tempFile)
                    .then(Mono.fromCallable(() -> pythonOcrClient.runOcrScript(tempFile)))
                    .doFinally(signalType -> tempFile.delete()); // Delete temp file after processing
        } catch (IOException e) {
            return Mono.error(new RuntimeException("Failed to save file", e));
        }
    }
}
