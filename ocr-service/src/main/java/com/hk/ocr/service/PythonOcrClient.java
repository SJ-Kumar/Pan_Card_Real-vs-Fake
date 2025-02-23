package com.hk.ocr.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.Map;

@Service
public class PythonOcrClient {

    @Value("${ocr.flask.url}")
    private String flaskOcrUrl;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public PythonOcrClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map<String, Object> runOcrScript(File imageFile) {
        try {
            // Create file resource
            FileSystemResource fileResource = new FileSystemResource(imageFile);

            // Create headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            // Create request entity with file
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", fileResource);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            // Send POST request
            ResponseEntity<String> response = restTemplate.exchange(
                flaskOcrUrl + "/process",
                HttpMethod.POST,
                requestEntity,
                String.class
            );

            return objectMapper.readValue(response.getBody(), Map.class);

        } catch (Exception e) {
            return Map.of("error", "Failed to connect to OCR service: " + e.getMessage());
        }
    }
}
