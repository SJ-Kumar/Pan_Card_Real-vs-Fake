import cv2
import numpy as np
import os

def convert_to_color_printout_variants(image_path, output_folder):
    """Generates 10 different Color Printout-like images mimicking real-world print scenarios."""

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the input image
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found!")
        return

    color_variants = {}

    # 1. **Normal Color Printout**
    color_variants["color_printout_normal.png"] = cv2.convertScaleAbs(img, alpha=1.0, beta=-10)

    # 2. **Faded Colors** (Low saturation)
    hsv_faded = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_faded[:, :, 1] = hsv_faded[:, :, 1] * 0.5  # Reduce saturation
    color_variants["color_printout_faded.png"] = cv2.cvtColor(hsv_faded, cv2.COLOR_HSV2BGR)

    # 3. **Oversaturated Colors** (High ink usage)
    hsv_saturated = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_saturated[:, :, 1] = np.clip(hsv_saturated[:, :, 1] * 1.5, 0, 255)
    color_variants["color_printout_oversaturated.png"] = cv2.cvtColor(hsv_saturated, cv2.COLOR_HSV2BGR)

    # 4. **Low Contrast Print**
    low_contrast = cv2.convertScaleAbs(img, alpha=0.8, beta=10)
    color_variants["color_printout_low_contrast.png"] = low_contrast

    # 5. **High Contrast Print**
    high_contrast = cv2.convertScaleAbs(img, alpha=1.5, beta=20)
    color_variants["color_printout_high_contrast.png"] = high_contrast

    # 6. **Color Smudges** (Adding blur to mimic smudges)
    smudged = cv2.GaussianBlur(img, (7, 7), 2)
    color_variants["color_printout_smudged.png"] = smudged

    # 7. **Low Ink Print** (Desaturated and brighter)
    hsv_low_ink = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_low_ink[:, :, 1] = hsv_low_ink[:, :, 1] * 0.4  # Lower saturation
    hsv_low_ink[:, :, 2] = hsv_low_ink[:, :, 2] * 1.2  # Increase brightness
    color_variants["color_printout_low_ink.png"] = cv2.cvtColor(hsv_low_ink, cv2.COLOR_HSV2BGR)

    # 8. **Color Noise Print** (Noisy print artifacts)
    noisy = img.copy()
    noise = np.random.randint(0, 30, noisy.shape, dtype='uint8')
    color_variants["color_printout_noisy.png"] = cv2.add(noisy, noise)

    # 9. **Skewed/Rotated Print**
    rows, cols, _ = img.shape
    M = cv2.getRotationMatrix2D((cols // 2, rows // 2), 3, 1)  # Rotate by 3 degrees
    color_variants["color_printout_skewed.png"] = cv2.warpAffine(img, M, (cols, rows), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    # 10. **Striped Print** (Horizontal lines mimicking printing errors)
    striped = img.copy()
    for i in range(0, rows, 30):
        cv2.line(striped, (0, i), (cols, i), (0, 0, 0), 1)
    color_variants["color_printout_striped.png"] = striped

    # Save all generated images
    for filename, img_data in color_variants.items():
        cv2.imwrite(os.path.join(output_folder, filename), img_data)
        print(f"Saved {filename}")

# Example usage
convert_to_color_printout_variants("latest.png", "color_printout_images")
