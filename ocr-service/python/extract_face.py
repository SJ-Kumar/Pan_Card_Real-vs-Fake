import sys
import cv2

def extract_face(image_path, output_path="extracted_face.png"):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(35, 35))

    if len(faces) == 0:
        print("No face detected.")
        return None

    (x, y, w, h) = faces[0]
    face = image[y:y+h, x:x+w]
    cv2.imwrite(output_path, face)
    print(f"Face extracted and saved as {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("No image path or output path provided")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_face(image_path, output_path)
