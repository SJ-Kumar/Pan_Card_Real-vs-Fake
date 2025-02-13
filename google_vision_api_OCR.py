from google.cloud import vision
import io

def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f"Error from Vision API: {response.error.message}")

    if texts:
        extracted_text = texts[0].description
        print("Extracted Text:\n", extracted_text)
        return extracted_text
    else:
        print("No text detected.")
        return None

image_path = "C:\\Users\\jayan\\Downloads\\Face_Recog\\96.jpg"
extracted_text = extract_text_from_image(image_path)
