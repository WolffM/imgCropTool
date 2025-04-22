from PIL import Image
import sys
import os
import shutil
from datetime import datetime

def create_passport_collage(shrink_direction, width_in, height_in):
    # Constants for passport photos
    PASSPORT_SIZE_INCH = 2.0  # 2 inches x 2 inches
    
    # Create input and output directories if they don't exist
    input_dir = os.path.join('passport', 'Input')
    output_dir = os.path.join('passport', 'Output')
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files from input directory
    image_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(os.path.join(input_dir, file))
    
    if not image_files:
        print("No image files found in passport/Input directory.")
        return
    
    try:
        # Calculate optimal DPI based on input image dimensions
        # First, examine all images to determine the optimal DPI
        min_pixel_density = float('inf')
        
        for img_path in image_files:
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate the minimum dimension of the square crop
            # (since passport photos are square, we'll use the smaller dimension)
            if img_width > img_height:
                crop_size = img_height
            else:
                crop_size = img_width
                
            # Calculate this image's effective DPI based on 2-inch passport size
            image_dpi = crop_size / PASSPORT_SIZE_INCH
            
            # Keep track of the lowest density to avoid upscaling any image
            min_pixel_density = min(min_pixel_density, image_dpi)
        
        # Round down to nearest 10 for cleaner numbers
        DPI = int(min_pixel_density // 10) * 10
        
        # Set a minimum DPI floor (e.g. 300)
        DPI = min(DPI, 600)
        
        print(f"Using optimal DPI of {DPI} for all passport photos")
        
        # Set passport size in pixels based on inferred DPI
        PASSPORT_SIZE_PIXELS = int(PASSPORT_SIZE_INCH * DPI)
        
        # Page size in pixels from input parameters
        PAGE_WIDTH = int(width_in * DPI)
        PAGE_HEIGHT = int(height_in * DPI)
        
        # Create a white background page
        page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')
        
        # Calculate number of photos per row and column
        photos_per_row = PAGE_WIDTH // PASSPORT_SIZE_PIXELS
        photos_per_col = PAGE_HEIGHT // PASSPORT_SIZE_PIXELS
        
        # Spacing for centering
        h_margin = (PAGE_WIDTH - (photos_per_row * PASSPORT_SIZE_PIXELS)) // 2
        v_margin = (PAGE_HEIGHT - (photos_per_col * PASSPORT_SIZE_PIXELS)) // 2
        
        # Generate timestamp for output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        photo_count = 0
        page_count = 1
        
        for img_path in image_files:
            # Load and process each image
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate target aspect ratio (square for passport)
            target_aspect = 1.0  # width/height = 1 for square
            img_aspect = img_width / img_height
            
            # Determine crop dimensions
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
            
            # Crop and resize to passport size
            cropped_img = img.crop((left, upper, right, lower))
            passport_img = cropped_img.resize((PASSPORT_SIZE_PIXELS, PASSPORT_SIZE_PIXELS), Image.LANCZOS)
            
            # Calculate position on the page
            row = photo_count % photos_per_row
            col = (photo_count // photos_per_row) % photos_per_col
            
            # Check if we need a new page
            if photo_count > 0 and photo_count % (photos_per_row * photos_per_col) == 0:
                # Save current page
                page_path = os.path.join(output_dir, f"passport_collage_{timestamp}_page{page_count}.png")
                page.save(page_path, dpi=(DPI, DPI))
                print(f"Saved passport collage page {page_count} as {page_path}")
                
                # Create new page
                page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')
                page_count += 1
                row = 0
                col = 0
            
            # Position and paste the passport photo
            x_pos = h_margin + (row * PASSPORT_SIZE_PIXELS)
            y_pos = v_margin + (col * PASSPORT_SIZE_PIXELS)
            page.paste(passport_img, (x_pos, y_pos))
            
            photo_count += 1
        
        # Save the final page
        if photo_count > 0:
            page_path = os.path.join(output_dir, f"passport_collage_{timestamp}_page{page_count}.png")
            page.save(page_path, dpi=(DPI, DPI))
            print(f"Saved passport collage page {page_count} as {page_path}")
        
        # Move processed input files to output directory
        for img_path in image_files:
            filename = os.path.basename(img_path)
            dest_path = os.path.join(output_dir, filename)
            shutil.move(img_path, dest_path)
            print(f"Moved {filename} to output directory")
            
        print(f"Processed {photo_count} passport photos on {page_count} page(s)")
        print(f"Page dimensions: {width_in}\" x {height_in}\" at {DPI} DPI")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python passportcrop.py <shrink_direction> <width_in> <height_in>")
        print("       where width_in and height_in are the page dimensions in inches")
    else:
        shrink_direction = sys.argv[1]
        width_in = float(sys.argv[2])
        height_in = float(sys.argv[3])
        create_passport_collage(shrink_direction, width_in, height_in)