from pytesseract import image_to_string
import image

print(image_to_string(image.open('image_1.jpg')))