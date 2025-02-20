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




import sys
import json
import cv2
import numpy as np
from imgocr import ImgOcr

# Initialize OCR Model once (Reuse instead of reloading on every request)
ocr_model = ImgOcr(use_gpu=True, is_efficiency_mode=True)

def process_image(image_bytes):
    try:
        np_image = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Apply simple enhancement instead of costly operations
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ocr_result = ocr_model.ocr(gray)

        return json.dumps({"ocr_data": ocr_result})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    image_bytes = sys.stdin.buffer.read()  # Read image bytes from Java
    print(process_image(image_bytes))


public Mono<Map<String, Object>> runOcrScript(byte[] imageBytes) {
    return Mono.fromCallable(() -> {
        try {
            ProcessBuilder pb = new ProcessBuilder("python3", "ocr_processor.py");
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Write image bytes directly to Python (Avoid disk I/O)
            OutputStream os = process.getOutputStream();
            os.write(imageBytes);
            os.flush();
            os.close();

            // Read response from Python
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            process.waitFor();

            return new ObjectMapper().readValue(output.toString(), Map.class);
        } catch (Exception e) {
            return Map.of("error", "OCR process failed: " + e.getMessage());
        }
    }).subscribeOn(Schedulers.boundedElastic()); // Run OCR in a separate thread
}