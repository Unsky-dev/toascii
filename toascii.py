import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from collections import Counter

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

# Calculate the dominant color in the image
def get_dominant_color(image):
    image = image.convert('RGBA')
    pixels = np.array(image)
    pixels = pixels.reshape(-1, 4)
    pixels = pixels[pixels[:, 3] > 0]  # Remove fully transparent pixels
    counts = Counter([tuple(pixel[:3]) for pixel in pixels])
    dominant_color = counts.most_common(1)[0][0]
    return dominant_color

# Save ASCII art to a text file
def save_ascii_art(ascii_art, output_path):
    with open(output_path, 'w') as file:
        for row in ascii_art:
            file.write(row + "\n")

# Convert ASCII art to PNG image with color
def ascii_to_png_with_color(ascii_art, color_map, output_image_path, font_path='Courier', font_size=10, background_opacity=255, background_brightness="auto"):
    char_width, char_height = 8, 16
    width = max(len(line) for line in ascii_art) * char_width
    height = len(ascii_art) * char_height

    # Determine background color
    if background_brightness == "auto":
        dominant_color = get_dominant_color(Image.fromarray(np.array(color_map, dtype=np.uint8)))
        brightness = int(0.299 * dominant_color[0] + 0.587 * dominant_color[1] + 0.114 * dominant_color[2])
        background_color = (0, 0, 0, background_opacity) if brightness > 127 else (255, 255, 255, background_opacity)
    elif background_brightness == "dark":
        background_color = (0, 0, 0, background_opacity)
    else:
        background_color = (255, 255, 255, background_opacity)

    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # Create a new image with transparent background
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)  # Load custom font
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font
    
    # Draw each character with its corresponding color
    for y, (line, colors) in enumerate(zip(ascii_art, color_map)):
        for x, (char, color) in enumerate(zip(line, colors)):
            if char != " ":
                # Draw background color behind the character
                if background_opacity > 0:
                    # Calculate background rectangle position
                    bbox = (x * char_width, y * char_height, (x + 1) * char_width, (y + 1) * char_height)
                    draw.rectangle(bbox, fill=background_color)
                
                # Draw the character with its color
                draw.text((x * char_width, y * char_height), char, font=font, fill=color)
    
    img.save(output_image_path, 'PNG')  # Save image as PNG

# Main function
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python toascii.py CHEMININPUT [quality] [opacity] [background: dark|light|auto]")
        sys.exit(1)
    
    input_image_path = sys.argv[1]
    base_dir = os.path.dirname(input_image_path)
    base_name = os.path.splitext(os.path.basename(input_image_path))[0].replace(" ", "_")

    # Set default parameters
    quality = 100
    background_opacity = 255
    background_brightness = "auto"
    
    if len(sys.argv) >= 3:
        try:
            quality = int(sys.argv[2])  # Override default quality with user input
        except ValueError:
            print(f"Invalid quality value: {sys.argv[2]}")
            sys.exit(1)
    
    if len(sys.argv) >= 4:
        try:
            background_opacity = int(sys.argv[3])  # Override default opacity with user input
        except ValueError:
            print(f"Invalid opacity value: {sys.argv[3]}")
            sys.exit(1)
    
    if len(sys.argv) >= 5:
        background_brightness = sys.argv[4].lower()  # Override default background brightness with user input
    
    input_image = Image.open(input_image_path)
    
    ascii_art, color_map = image_to_ascii_with_color(input_image, width=quality)
    ascii_output_path = os.path.join(base_dir, f"{base_name}_ascii.txt")
    save_ascii_art(ascii_art, ascii_output_path)
    
    final_image_path = os.path.join(base_dir, f"{base_name}_ascii_colored.png")
    ascii_to_png_with_color(ascii_art, color_map, final_image_path, font_size=12, background_opacity=background_opacity, background_brightness=background_brightness)
    
    print(f"ASCII art saved to: {ascii_output_path}")
    print(f"Final colored image saved to: {final_image_path}")
