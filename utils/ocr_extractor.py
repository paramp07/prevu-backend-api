from paddleocr import PaddleOCR
import cv2
from matplotlib import pyplot as plt

# Initialize OCR once
ocr = PaddleOCR(lang='en')  # Load English OCR model only once for performance

def run_ocr(image_path: str, show_image: bool = False) -> list:
    """
    Runs OCR on the given image and returns detected text and confidence.

    Args:
        image_path (str): Path to the image file (e.g., "temp/photo.jpg").
        show_image (bool): If True, displays the image using matplotlib.

    Returns:
        List[dict]: List of dictionaries with detected text and accuracy.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at: {image_path}")

    if show_image:
        plt.figure()
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    result = ocr.ocr(img, cls=True)
    output = []

    for line in result:
        for word_info in line:
            text = word_info[1][0]
            accuracy = word_info[1][1]
            output.append({"text": text, "accuracy": round(accuracy, 4)})

    return output

# Example usage
if __name__ == "__main__":
    temp_path = "temp/photo2.jpg"
    results = run_ocr(temp_path, show_image=True)
    print("Detected Text and Accuracy:")
    for item in results:
        print(f"Text: {item['text']}, Accuracy: {item['accuracy']}")


# Get image

# Process Image (OCR)

# Grammar Check Text with Open AI (API) and group related text and return json list of objects of the food and other metadata like location and name of restaurant

# Take JSON and convnert to python object 

# Iterate through each menu items and return 6-7 links to those images (possiblitiy in future to grade on relatabliklty)

# Attach those links to the object adn convert to json 

# Send json through python server api 
