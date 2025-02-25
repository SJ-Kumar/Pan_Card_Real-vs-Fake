import cv2
import numpy as np

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

def are_at_least_three_colors_close(template_colors, uploaded_colors, threshold=6):
    """Checks if at least three color percentages are within the threshold difference."""
    common_colors = set(template_colors.keys()).intersection(set(uploaded_colors.keys()))
    close_count = 0
    
    for color in common_colors:
        if abs(template_colors[color] - uploaded_colors[color]) <= threshold:
            close_count += 1
            if close_count >= 3:
                return True  # At least three colors are close
    
    return False

def is_old_id_card(uploaded_image_path, template_image_path, feature_threshold=0.7, color_threshold=90, color_closeness_threshold=6):
    """Checks if the uploaded ID card matches the old format based on feature matching and color analysis."""
    # Load images in grayscale for feature matching
    template = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
    uploaded = cv2.imread(uploaded_image_path, cv2.IMREAD_GRAYSCALE)
    
    if template is None or uploaded is None:
        return "Error: Unable to load images."
    
    # ORB feature detection
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(template, None)
    kp2, des2 = orb.detectAndCompute(uploaded, None)
    
    # Feature matching using Brute-Force Matcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)  # Sort matches by distance
    
    # Calculate similarity score
    feature_similarity = len(matches) / max(len(kp1), len(kp2))
    
    # Get dominant colors from template and uploaded images
    template_colors = get_dominant_colors(template_image_path)
    uploaded_colors = get_dominant_colors(uploaded_image_path)
    
    if isinstance(template_colors, str) or isinstance(uploaded_colors, str):
        return "Error in color extraction."
    
    # Print color percentages before making the final decision
    print("\nTemplate Image Dominant Colors:", {k: f"{v}%" for k, v in template_colors.items()})
    print("Uploaded Image Dominant Colors:", {k: f"{v}%" for k, v in uploaded_colors.items()})
    
    # Compare color similarity
    common_colors = set(template_colors.keys()).intersection(set(uploaded_colors.keys()))
    color_match_score = sum(min(template_colors.get(color, 0), uploaded_colors.get(color, 0)) for color in common_colors)

    # Check if at least three colors have similar percentages
    if are_at_least_three_colors_close(template_colors, uploaded_colors, color_closeness_threshold):
        return "This isn't allowed. Upload the latest ID card."
    
    # Reject only if BOTH feature similarity and color similarity are high
    if feature_similarity >= feature_threshold and color_match_score >= color_threshold:
        return "This isn't allowed. Upload the latest ID card."
    
    return "Success"

# Example Usage
template_path = "old_hkid.jpg"  # Template of old ID card
uploaded_path = "old.jpg"  # Uploaded ID card

result = is_old_id_card(uploaded_path, template_path)
print("\nFinal Decision:", result)
