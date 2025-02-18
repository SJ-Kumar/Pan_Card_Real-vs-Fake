<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Hong Kong ID Card</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f9fa;
        }

        .container {
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background: white;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        input {
            margin: 10px 0;
        }

        button {
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }

        button:disabled {
            background-color: gray;
            cursor: not-allowed;
        }

        .error {
            color: red;
            font-size: 14px;
        }

        .hidden {
            display: none;
        }

        #result {
            background: #eee;
            padding: 10px;
            border-radius: 5px;
            text-align: left;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>OCR Hong Kong ID Card</h1>
        <input type="file" id="imageInput" accept="image/*">
        <button id="uploadBtn">Upload & Extract</button>
        <p id="errorMessage" class="error"></p>

        <div id="loading" class="hidden">Processing...</div>

        <div id="resultContainer" class="hidden">
            <h2>Extracted Information</h2>
            <pre id="result"></pre>
        </div>
    </div>

    <script>
        document.getElementById("uploadBtn").addEventListener("click", async function () {
            const fileInput = document.getElementById("imageInput");
            const errorMessage = document.getElementById("errorMessage");
            const loadingText = document.getElementById("loading");
            const resultContainer = document.getElementById("resultContainer");
            const resultText = document.getElementById("result");

            // Clear previous error and result
            errorMessage.textContent = "";
            resultContainer.classList.add("hidden");
            resultText.textContent = "";

            if (!fileInput.files.length) {
                errorMessage.textContent = "Please select an image.";
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append("image", file);

            loadingText.classList.remove("hidden");

            try {
                const response = await fetch("http://127.0.0.1:5000/ocr", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("Failed to process image.");
                }

                const data = await response.json();
                resultText.textContent = JSON.stringify(data.extractedOcrData, null, 2);
                resultContainer.classList.remove("hidden");
            } catch (error) {
                errorMessage.textContent = error.message;
            } finally {
                loadingText.classList.add("hidden");
            }
        });
    </script>

</body>
</html>