import cv2
import numpy as np
import os

def convert_to_xerox_variants(image_path, output_folder):
    """Generates 10 different Xerox-like images mimicking real-world photocopy scenarios."""
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the input image
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found!")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    xerox_variants = {}

    # 1. **Normal Xerox Effect** (Base version)
    xerox_variants["xerox_normal.png"] = cv2.convertScaleAbs(gray, alpha=1.2, beta=-30)

    # 2. **High Contrast Xerox**
    xerox_variants["xerox_high_contrast.png"] = cv2.convertScaleAbs(gray, alpha=1.5, beta=-40)

    # 3. **Low Ink Effect** (Lighter areas, faded look)
    xerox_variants["xerox_low_ink.png"] = cv2.convertScaleAbs(gray, alpha=0.8, beta=20)

    # 4. **Overexposed Copy** (Too bright)
    xerox_variants["xerox_overexposed.png"] = cv2.convertScaleAbs(gray, alpha=1.0, beta=60)

    # 5. **Underexposed Copy** (Too dark)
    xerox_variants["xerox_underexposed.png"] = cv2.convertScaleAbs(gray, alpha=1.0, beta=-60)

    # 6. **Blurred Copy** (Simulating motion blur or scanning issues)
    xerox_variants["xerox_blurred.png"] = cv2.GaussianBlur(gray, (5, 5), 2)

    # 7. **Noisy Copy** (Simulating poor-quality Xerox machines)
    noisy = gray.copy()
    noise = np.random.randint(0, 50, noisy.shape, dtype='uint8')
    xerox_variants["xerox_noisy.png"] = cv2.add(noisy, noise)

    # 8. **Skewed/Rotated Copy**
    rows, cols = gray.shape
    M = cv2.getRotationMatrix2D((cols//2, rows//2), 5, 1)  # Rotate by 5 degrees
    xerox_variants["xerox_skewed.png"] = cv2.warpAffine(gray, M, (cols, rows), borderMode=cv2.BORDER_CONSTANT, borderValue=255)

    # 9. **Ink Smudge Effect** (Horizontal smudge)
    smudged = cv2.GaussianBlur(gray, (15, 3), 0)
    xerox_variants["xerox_smudged.png"] = smudged

    # 10. **Vertical Streaks** (Mimicking poor rollers)
    streaks = gray.copy()
    for i in range(0, cols, 20):  # Add streaks every 20 pixels
        cv2.line(streaks, (i, 0), (i, rows), (0, 0, 0), 1)
    xerox_variants["xerox_streaks.png"] = streaks

    # Save all images
    for filename, img_data in xerox_variants.items():
        cv2.imwrite(os.path.join(output_folder, filename), img_data)
        print(f"Saved {filename}")


convert_to_xerox_variants("latest.png", "images")
