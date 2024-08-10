import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Converts an image to ASCII art with color
def image_to_ascii_with_color(image, width):
    image = image.convert('RGBA')  # Convert image to RGBA mode
    aspect_ratio = image.height / image.width
    height = int(aspect_ratio * width * 0.5)  # Calculate new height based on width
    image = image.resize((width, height))  # Resize image
    pixels = np.array(image)
    
    ascii_chars = "$@B%8&W#*+=-:. "  # ASCII characters used for different gray levels
    ascii_art = []  # To store ASCII art lines
    color_map = []  # To store color information
    
    # Process each pixel in the image
    for row in pixels:
        ascii_row = ""
        color_row = []
        for pixel in row:
            r, g, b, a = pixel
            if a == 0:  # Transparent pixels
                ascii_char = " "
                color = (255, 255, 255, 0)
            else:  # Opaque pixels
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # Convert to grayscale
                ascii_char = ascii_chars[gray // (255 // (len(ascii_chars) - 1))]  # Map to ASCII char
                color = (r, g, b, 255)  # Color of the pixel
            ascii_row += ascii_char
            color_row.append(color)
        ascii_art.append(ascii_row)
        color_map.append(color_row)
    
    return ascii_art, color_map

# Save ASCII art to a text file
def save_ascii_art(ascii_art, output_path):
    with open(output_path, 'w') as file:
        for row in ascii_art:
            file.write(row + "\n")

# Convert ASCII art to PNG image with color
def ascii_to_png_with_color(ascii_art, color_map, output_image_path, font_path='Courier', font_size=10):
    char_width, char_height = 8, 16
    width = max(len(line) for line in ascii_art) * char_width
    height = len(ascii_art) * char_height

    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # Create a new image
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)  # Load custom font
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font
    
    # Draw each character with its corresponding color
    for y, (line, colors) in enumerate(zip(ascii_art, color_map)):
        for x, (char, color) in enumerate(zip(line, colors)):
            if char != " ":
                draw.text((x * char_width, y * char_height), char, font=font, fill=color)
    
    img.save(output_image_path, 'PNG')  # Save image as PNG

# Main function
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python toascii.py CHEMININPUT [quality]")
        sys.exit(1)
    
    input_image_path = sys.argv[1]
    base_dir = os.path.dirname(input_image_path)
    base_name = os.path.splitext(os.path.basename(input_image_path))[0].replace(" ", "_")

    # Set default quality (width)
    quality = 100
    if len(sys.argv) >= 3:
        quality = int(sys.argv[2])  # Override default quality with user input
    
    input_image = Image.open(input_image_path)
    
    ascii_art, color_map = image_to_ascii_with_color(input_image, width=quality)
    ascii_output_path = os.path.join(base_dir, f"{base_name}_ascii.txt")
    save_ascii_art(ascii_art, ascii_output_path)
    
    final_image_path = os.path.join(base_dir, f"{base_name}_ascii_colored.png")
    ascii_to_png_with_color(ascii_art, color_map, final_image_path, font_size=12)
    
    print(f"ASCII art saved to: {ascii_output_path}")
    print(f"Final colored image saved to: {final_image_path}")
