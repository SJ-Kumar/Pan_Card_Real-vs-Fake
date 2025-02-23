public Mono<Map<String, Object>> processImage(FilePart filePart) {
    return filePart.content()  // Get file content as stream
        .reduce(new ByteArrayOutputStream(), (baos, dataBuffer) -> {
            try {
                baos.write(dataBuffer.asByteBuffer().array());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            return baos;
        })
        .flatMap(baos -> executeOcrProcess(baos.toByteArray()));  // Send stream to Python
}


