package com.hk.ocr.utils;

import org.apache.commons.io.FileUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

public class FileStorageUtil {
    public static File saveFile(MultipartFile multipartFile) throws IOException {
        File tempFile = Files.createTempFile("upload_", "_" + multipartFile.getOriginalFilename()).toFile();
        FileUtils.writeByteArrayToFile(tempFile, multipartFile.getBytes());
        return tempFile;
    }
}
