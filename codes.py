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
