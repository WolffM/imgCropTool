from PIL import Image
import sys
import os
import shutil
from datetime import datetime

def create_thumbnail_collage(max_dimension_inch, width_in, height_in):
    # Constants for thumbnail photos
    MAX_DIMENSION_INCH = max_dimension_inch  # Max dimension (width or height) in inches
    
    # Create input and output directories if they don't exist
    input_dir = os.path.join('main', 'Input')
    output_dir = os.path.join('main', 'Output')
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files from input directory
    image_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(os.path.join(input_dir, file))
    
    if not image_files:
        print("No image files found in main/Input directory.")
        return
    
    try:
        # Calculate optimal DPI based on input image dimensions
        # First, examine all images to determine the optimal DPI
        min_pixel_density = float('inf')
        
        for img_path in image_files:
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate the larger dimension (either width or height)
            max_dimension = max(img_width, img_height)
                
            # Calculate this image's effective DPI based on MAX_DIMENSION_INCH
            image_dpi = max_dimension / MAX_DIMENSION_INCH
            
            # Keep track of the lowest density to avoid upscaling any image
            min_pixel_density = min(min_pixel_density, image_dpi)
        
        # Round down to nearest 10 for cleaner numbers
        DPI = int(min_pixel_density // 10) * 10
        
        # Set a minimum DPI floor
        DPI = max(DPI, 300)
        
        print(f"Using optimal DPI of {DPI} for all thumbnails")
        print(f"Maximum dimension: {MAX_DIMENSION_INCH} inches")
        
        # Set max thumbnail size in pixels based on inferred DPI
        MAX_DIMENSION_PIXELS = int(MAX_DIMENSION_INCH * DPI)
        
        # Page size in pixels from input parameters
        PAGE_WIDTH = int(width_in * DPI)
        PAGE_HEIGHT = int(height_in * DPI)
        
        # Create a white background page
        page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')
        
        # Generate timestamp for output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        photo_count = 0
        page_count = 1
        
        # Track current position on page
        x_pos = 0
        y_pos = 0
        row_height = 0  # Track the height of the current row
        
        for img_path in image_files:
            # Load image
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate aspect ratio
            img_aspect = img_width / img_height
            
            # Determine target dimensions (keeping aspect ratio)
            if img_width > img_height:  # Wider image
                # Width is the limiting factor
                target_width = min(img_width, MAX_DIMENSION_PIXELS)
                target_height = int(target_width / img_aspect)
                
                # Check if height is still within limits
                if target_height > MAX_DIMENSION_PIXELS:
                    target_height = MAX_DIMENSION_PIXELS
                    target_width = int(target_height * img_aspect)
            else:  # Taller or square image
                # Height is the limiting factor
                target_height = min(img_height, MAX_DIMENSION_PIXELS)
                target_width = int(target_height * img_aspect)
                
                # Check if width is still within limits
                if target_width > MAX_DIMENSION_PIXELS:
                    target_width = MAX_DIMENSION_PIXELS
                    target_height = int(target_width / img_aspect)
                
            # Resize the image using high quality resampling
            thumbnail_img = img.resize((target_width, target_height), Image.LANCZOS)
            
            # Check if we need to start a new row
            if x_pos + target_width > PAGE_WIDTH:
                x_pos = 0
                y_pos += row_height + 20  # Add some padding between rows
                row_height = 0
            
            # Check if we need a new page
            if y_pos + target_height > PAGE_HEIGHT:
                # Save current page
                page_path = os.path.join(output_dir, f"thumbnails_{timestamp}_page{page_count}.png")
                page.save(page_path, dpi=(DPI, DPI))
                print(f"Saved thumbnail collage page {page_count} as {page_path}")
                
                # Create new page
                page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')
                page_count += 1
                x_pos = 0
                y_pos = 0
                row_height = 0
            
            # Position and paste the thumbnail
            page.paste(thumbnail_img, (x_pos, y_pos))
            
            # Update position for next image
            x_pos += target_width + 20  # Add some padding between images
            row_height = max(row_height, target_height)
            
            photo_count += 1
        
        # Save the final page
        if photo_count > 0:
            page_path = os.path.join(output_dir, f"thumbnails_{timestamp}_page{page_count}.png")
            page.save(page_path, dpi=(DPI, DPI))
            print(f"Saved thumbnail collage page {page_count} as {page_path}")
        
        # Move processed input files to output directory
        for img_path in image_files:
            filename = os.path.basename(img_path)
            dest_path = os.path.join(output_dir, filename)
            shutil.move(img_path, dest_path)
            print(f"Moved {filename} to output directory")
            
        print(f"Processed {photo_count} thumbnails on {page_count} page(s)")
        print(f"Page dimensions: {width_in}\" x {height_in}\" at {DPI} DPI")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python thumbnail_crop.py <max_dimension_inch> <width_in> <height_in>")
        print("       where:")
        print("       - max_dimension_inch is the maximum dimension for thumbnails (e.g. 3.2)")
        print("       - width_in and height_in are the page dimensions in inches")
    else:
        max_dimension_inch = float(sys.argv[1])
        width_in = float(sys.argv[2])
        height_in = float(sys.argv[3])
        create_thumbnail_collage(max_dimension_inch, width_in, height_in)