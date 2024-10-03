import json
import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

# Load coupon data from kupon.json
def load_coupon_data(file='kupon.json'):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file} is not a valid JSON.")
        return []

# Generate a random filename for the coupon image
def generate_filename(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length)) + '.png'

# Generate barcode for the coupon code without saving to a file
def generate_barcode(coupon_code):
    ean = barcode.get('code128', coupon_code, writer=ImageWriter())
    barcode_io = BytesIO()
    ean.write(barcode_io)
    barcode_io.seek(0)
    return Image.open(barcode_io)  # return barcode image directly

# Generate and save coupon image with barcode
def generate_coupon_image(coupon_data, output_dir='coupon', width=600, height=500):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a new blank image (white background)
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Define the text font and size (using a larger default PIL font)
    font = ImageFont.load_default()

    # Adjust text positioning
    padding = 10
    current_height = padding

    # Add coupon details to the image
    d.text((10, current_height), f"Coupon Code: {coupon_data['code']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Offer Description: {coupon_data['description']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Validity Period: {coupon_data['validity']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Terms and Conditions: {coupon_data['terms']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Company Name: {coupon_data['company_name']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Discount Value: {coupon_data['discount_value']}", fill=(0, 0, 0), font=font)
    current_height += 30
    d.text((10, current_height), f"Contact Information: {coupon_data['contact_info']}", fill=(0, 0, 0), font=font)
    current_height += 40  # Add extra space before barcode

    # Generate barcode for the coupon code without saving it to a file
    barcode_img = generate_barcode(coupon_data['code'])

    # Resize barcode if necessary
    barcode_img = barcode_img.resize((400, 100))  # Resize barcode for better fitting

    # Paste the barcode image on the coupon image
    img.paste(barcode_img, (10, current_height))

    # Generate a unique filename and save the image
    filename = generate_filename()
    img.save(os.path.join(output_dir, filename))
    print(f"Coupon image saved as {os.path.join(output_dir, filename)}")

    return filename

# Main function to create coupon images from JSON data
if __name__ == "__main__":
    # Load coupon data from kupon.json
    coupons_data = load_coupon_data()

    if coupons_data:  # Proceed if there are coupons to process
        for coupon in coupons_data:
            generate_coupon_image(coupon)
    else:
        print("No coupon data available to generate images.")
