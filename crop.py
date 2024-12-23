from PIL import Image
import sys

def crop_image(image_name, shrink_direction, width_in, height_in):
    try:
        # Construct the image path
        image_path = f"{image_name}.png"
        
        # Load the image
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Calculate target aspect ratio
        target_aspect = width_in / height_in
        img_aspect = img_width / img_height

        # Determine target dimensions while preserving aspect ratio
        if img_aspect > target_aspect:  # Image is wider than target
            target_width = int(img_height * target_aspect)
            target_height = img_height
        else:  # Image is taller than or equal to target
            target_width = img_width
            target_height = int(img_width / target_aspect)

        # Determine cropping box based on shrink direction
        left = (img_width - target_width) // 2
        upper = (img_height - target_height) // 2

        if 'l' in shrink_direction:  # Left-aligned
            left = 0
            right = target_width
        elif 'r' in shrink_direction:  # Right-aligned
            left = img_width - target_width
            right = img_width
        else:  # Center horizontally
            right = left + target_width

        if 'u' in shrink_direction:  # Up-aligned
            upper = 0
            lower = target_height
        elif 'd' in shrink_direction:  # Down-aligned
            upper = img_height - target_height
            lower = img_height
        else:  # Center vertically
            lower = upper + target_height

        # Crop and save the image
        cropped_img = img.crop((left, upper, right, lower))
        output_path = f"cropped_{shrink_direction}_{image_name}.png"
        cropped_img.save(output_path)
        print(f"Image cropped and saved as {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python image_cropper.py <image_name> <shrink_direction> <width_in> <height_in>")
    else:
        image_name = sys.argv[1]
        shrink_direction = sys.argv[2]
        width_in = float(sys.argv[3])
        height_in = float(sys.argv[4])
        crop_image(image_name, shrink_direction, width_in, height_in)
