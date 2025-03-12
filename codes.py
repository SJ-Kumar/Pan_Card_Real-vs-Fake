import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from deepface import DeepFace
import tensorflow as tf
tf.config.experimental_run_functions_eagerly(True)

app = Flask(__name__)

# Ordered list of backends (Fastest & Most Accurate First)
BACKENDS = ["retinaface", "mtcnn", "opencv", "ssd", "dlib"]

# Ordered list of face recognition models (Most Accurate First)
MODELS = ["ArcFace", "Facenet", "VGG-Face"]

# Function to read an uploaded image file
def read_image(image_file):
    try:
        # Convert uploaded file to an OpenCV image
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        raise Exception(f"Error reading image: {str(e)}")

# Function to detect face in an image using multiple backends
def detect_face(image):
    for backend in BACKENDS:
        try:
            print(f"🔍 Trying backend: {backend}")
            face_objs = DeepFace.extract_faces(img_path=image, detector_backend=backend, anti_spoofing=True)
            if face_objs:
                face = face_objs[0]['face']
                facial_area = face_objs[0]['facial_area']
                print(f"✅ Face detected using {backend}")
                return face, facial_area  # Return face and bounding box
        except Exception as e:
            print(f"❌ Backend {backend} failed: {e}")

    print(f"❌ Failed to detect face in the image using all backends.")
    return None, None

# Function to compare two faces using an ensemble of models
def compare_faces_ensemble(img1_path, img2_path, base_threshold=0.55):
    votes = []
    distances = []
    confidences = []

    for model in MODELS:
        try:
            print(f"🔍 Comparing using model: {model}")
            result = DeepFace.verify(img1_path, img2_path, model_name=model, distance_metric="cosine")
            distance = result["distance"]
            distances.append(distance)

            # Convert distance to confidence score
            confidence = (1 - distance) * 100
            confidences.append(confidence)

            votes.append(distance < base_threshold)  # Match if distance is below threshold
        except Exception as e:
            print(f"❌ Model {model} failed: {e}")

    if len(votes) == 0:
        return False, None, None  # No valid results

    avg_distance = np.mean(distances) if distances else None
    avg_confidence = np.mean(confidences) if confidences else None

    # **Adaptive Threshold Adjustment**
    if avg_distance is not None and avg_distance > 0.6:
        print("⚠️ High distance detected, adjusting threshold...")
        base_threshold += 0.14  # Increase threshold for older photos

    is_match = avg_distance < base_threshold
    return is_match, avg_distance, avg_confidence

@app.route('/verify', methods=['POST'])
def verify():
    try:
        if 'img1' not in request.files or 'img2' not in request.files:
            return jsonify({"error": "Please upload both img1 and img2"}), 400

        img1 = request.files['img1']
        img2 = request.files['img2']

        # Save images temporarily
        img1_path = "temp_img1.jpg"
        img2_path = "temp_img2.jpg"
        img1.save(img1_path)
        img2.save(img2_path)

        # **🔍 Anti-Spoofing Check for First Image**
        try:
            face_objs = DeepFace.extract_faces(img_path=img1_path, anti_spoofing=True)
            if face_objs and face_objs[0].get("is_real") is False:
                os.remove(img1_path)
                os.remove(img2_path)
                return jsonify({"error": "Spoof Attack Detected on the selfie video extracted image."}), 400
            print("✅ First image is real, proceeding...")
        except Exception as e:
            os.remove(img1_path)
            os.remove(img2_path)
            return jsonify({"error": f"Anti-spoofing check failed: {str(e)}"}), 400

        # **🔍 Face Detection for Both Images**
        face1, facial_area1 = detect_face(img1_path)
        face2, facial_area2 = detect_face(img2_path)

        if face1 is None or face2 is None:
            os.remove(img1_path)
            os.remove(img2_path)
            return jsonify({"error": "❌ Face detection failed for one or both images."}), 400

        # **🔍 Face Comparison**
        match, avg_dist, avg_conf = compare_faces_ensemble(img1_path, img2_path)

        # Cleanup temp files
        os.remove(img1_path)
        os.remove(img2_path)

        # **✅ Response JSON**
        return jsonify({
            "match": bool(match),  # Convert numpy.bool_ to standard bool
            "average_distance": float(avg_dist) if avg_dist is not None else None,
            "confidence": float(avg_conf) if avg_conf is not None else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
