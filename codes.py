import cv2
import pytesseract
import numpy as np
from PIL import Image
from collections import defaultdict

# Load image
image_path = "id_card.jpg"  # Change this to your image path
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding to improve text detection
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Extract text with bounding boxes
custom_config = r'--psm 6'  # Assume uniform block of text
data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

font_sizes = []
char_counts = defaultdict(int)

# Iterate through detected text
for i in range(len(data["text"])):
    if data["text"][i].strip():
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        font_sizes.append(h)  # Height of bounding box as font size estimate
        
        roi = gray[y:y+h, x:x+w]
        edges = cv2.Canny(roi, 50, 150)  # Edge detection for font style analysis
        char_counts[np.mean(edges)] += 1  # Store average edge density

# Estimate the most common font size
if font_sizes:
    avg_font_size = int(np.median(font_sizes))
else:
    avg_font_size = "Unknown"

# Identify the dominant font style based on edge density
if char_counts:
    common_edge_density = max(char_counts, key=char_counts.get)
    if common_edge_density > 100:
        font_style = "Bold or Heavy"
    elif common_edge_density > 50:
        font_style = "Regular"
    else:
        font_style = "Thin or Light"
else:
    font_style = "Unknown"

# Print results
print(f"Estimated Font Size: {avg_font_size} pixels")
print(f"Estimated Font Style: {font_style}")

# Show processed image
cv2.imshow("Processed Image", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
