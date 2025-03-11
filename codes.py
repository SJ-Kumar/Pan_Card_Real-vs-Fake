import cv2

# Load the image
image_path = "/mnt/data/file-Fo7NP4rxZGwcV13gFrMaPH"
image = cv2.imread(image_path)

# Create a callback function to get coordinates
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: x={x}, y={y}")

# Show image and capture click positions
cv2.imshow("Click to get coordinates", image)
cv2.setMouseCallback("Click to get coordinates", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
