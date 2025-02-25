import cv2
import numpy as np
import os

def get_dominant_colors(image_path):
    """Detects dominant colors in an image and their percentage, including Black & White."""
    image = cv2.imread(image_path)
    if image is None:
        return f"Error: Could not read image {image_path}"

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Extract Hue, Saturation, and Value channels
    hue = hsv[:, :, 0].flatten()
    saturation = hsv[:, :, 1].flatten()
    value = hsv[:, :, 2].flatten()

    # Get total pixel count
    total_pixels = len(saturation)

    # **Detect Black & White Pixels First**
    black_pixels = np.sum(value < 50) / total_pixels * 100  # Dark areas
    white_pixels = np.sum((value > 200) & (saturation < 50)) / total_pixels * 100  # Bright low-saturation areas

    # **Color Detection (Exclude Low-Saturation Pixels)**
    color_mask = saturation > 50  # Ignore low-saturation (gray) pixels

    if np.sum(color_mask) == 0:  
        hist = np.zeros(180)  # No colored pixels, avoid division by zero
    else:
        hue_filtered = hue[color_mask]
        hist, _ = np.histogram(hue_filtered, bins=180, range=[0, 180])  # 180 bins for Hue values
        hist = hist / hist.sum() * 100  # Convert to percentage safely

    # Define Hue-based color ranges
    color_ranges = {
        "Red": [(0, 10), (170, 180)],
        "Orange": [(10, 25)],
        "Yellow": [(25, 35)],
        "Green": [(35, 85)],
        "Cyan": [(85, 100)],
        "Blue": [(100, 130)],
        "Purple": [(130, 170)]
    }

    # Compute color percentages
    color_percentages = {}
    for color, ranges in color_ranges.items():
        percentage = sum(hist[start:end].sum() for start, end in ranges)
        if percentage > 0.5:  # Ignore very small percentages
            color_percentages[color] = round(percentage, 2)

    # Include Black & White percentages
    if black_pixels > 0.5:
        color_percentages["Black"] = round(black_pixels, 2)
    if white_pixels > 0.5:
        color_percentages["White/Gray"] = round(white_pixels, 2)

    # Sort and return results
    sorted_colors = dict(sorted(color_percentages.items(), key=lambda x: x[1], reverse=True))

    return sorted_colors

images_folder = "images"

# Loop through all image files in the folder
for filename in os.listdir(images_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        image_path = os.path.join(images_folder, filename)
        print(f"Processing: {filename}")
        colors = get_dominant_colors(image_path)
        
        if isinstance(colors, str):
            print(colors)
        else:
            print("Detected Colors:")
            for color, percentage in colors.items():
                print(f"{color}: {percentage}%")

            # Condition to determine if the ID card is a Xerox copy
            if len(colors) == 1 or (len(colors) == 2 and "Black" in colors and "White/Gray" in colors):
                print("This is a Xerox Copy!")
            elif colors.get("Black", 0) + colors.get("White/Gray", 0) > 90:
                print("This is a Xerox Copy!")
            else:
                print("This is an Original ID Card!")
        print("-------------------------------------------")
