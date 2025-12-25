"""
Utilities Module for Dox2 PDF Application
Provides PDF rendering with RGB color support and helper functions
"""

import io
import fitz  # PyMuPDF
from PIL import Image
import os


def render_page_with_fallback(doc, page_num, zoom_factor=1.0):
    """
    Enhanced PDF page rendering with RGB color support
    
    Args:
        doc: PyMuPDF document object
        page_num: Page number to render (0-indexed)
        zoom_factor: Zoom factor for rendering
    
    Returns:
        Tuple of (PIL Image, rendering method name) or (None, error message)
    """
    try:
        page = doc[page_num]
        
        # Method 1: RGB with higher DPI for better quality
        mat = fitz.Matrix(zoom_factor * 2, zoom_factor * 2)
        try:
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
            if pix.samples:
                img_data = pix.tobytes("ppm")
                return Image.open(io.BytesIO(img_data)), "method 1 (RGB high DPI)"
        except Exception as e:
            pass
        
        # Method 2: RGB alternative approach
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        try:
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            if pix.samples:
                img_data = pix.tobytes("ppm")
                return Image.open(io.BytesIO(img_data)), "method 2 (RGB alternative)"
        except Exception as e:
            pass
        
        # Method 3: RGB with RGBA
        try:
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=True)
            if pix.samples:
                img_data = pix.tobytes("ppm")
                return Image.open(io.BytesIO(img_data)), "method 3 (RGB with alpha)"
        except Exception as e:
            pass
        
        # Method 4: Grayscale fallback
        try:
            pix = page.get_pixmap(matrix=mat)
            if pix.samples:
                img_data = pix.tobytes("ppm")
                return Image.open(io.BytesIO(img_data)), "method 4 (grayscale fallback)"
        except Exception as e:
            pass
        
        return None, "error: unable to render page"
    
    except Exception as e:
        return None, f"error: {str(e)}"


def get_page_size(doc, page_num):
    """
    Get the size of a PDF page
    
    Args:
        doc: PyMuPDF document object
        page_num: Page number (0-indexed)
    
    Returns:
        Tuple of (width, height)
    """
    try:
        page = doc[page_num]
        rect = page.rect
        return (int(rect.width), int(rect.height))
    except Exception as e:
        return (800, 1000)  # Default size


def calculate_optimal_zoom(page_width, page_height, display_width, display_height):
    """
    Calculate optimal zoom factor to fit page in display area
    
    Args:
        page_width: Width of PDF page
        page_height: Height of PDF page
        display_width: Width of display area
        display_height: Height of display area
    
    Returns:
        Zoom factor
    """
    if page_width == 0 or page_height == 0:
        return 1.0
    
    zoom_x = (display_width - 20) / page_width  # Leave 20px margin
    zoom_y = (display_height - 20) / page_height
    
    return min(zoom_x, zoom_y, 1.0)  # Don't zoom beyond 100%


def get_page_text(doc, page_num):
    """
    Extract text from a PDF page
    
    Args:
        doc: PyMuPDF document object
        page_num: Page number (0-indexed)
    
    Returns:
        Extracted text as string
    """
    try:
        page = doc[page_num]
        return page.get_text()
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def validate_pdf_file(filepath):
    """
    Validate if file is a valid PDF
    
    Args:
        filepath: Path to file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    if not filepath.lower().endswith('.pdf'):
        return False, "File is not a PDF"
    
    try:
        doc = fitz.open(filepath)
        page_count = doc.page_count
        doc.close()
        return True, None
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"


def get_pdf_info(filepath):
    """
    Get metadata and information about PDF file
    
    Args:
        filepath: Path to PDF file
    
    Returns:
        Dictionary with PDF information
    """
    try:
        doc = fitz.open(filepath)
        metadata = doc.metadata
        
        info = {
            'title': metadata.get('title', 'Unknown'),
            'author': metadata.get('author', 'Unknown'),
            'subject': metadata.get('subject', 'Unknown'),
            'creator': metadata.get('creator', 'Unknown'),
            'pages': doc.page_count,
            'file_size': os.path.getsize(filepath),
        }
        
        doc.close()
        return info
    except Exception as e:
        return {'error': str(e)}


def format_file_size(size_bytes):
    """
    Format file size to human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_all_pdf_files(directory):
    """
    Get all PDF files in a directory
    
    Args:
        directory: Directory path
    
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    try:
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                if filename.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(directory, filename))
    except Exception as e:
        pass
    
    return sorted(pdf_files)


def create_pdf_from_images(image_paths, output_path):
    """
    Create PDF from a list of image paths
    
    Args:
        image_paths: List of image file paths
        output_path: Output PDF file path
    
    Returns:
        Tuple of (success, message)
    """
    try:
        from PIL import Image
        images = []
        
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                return False, f"Error loading image {img_path}: {str(e)}"
        
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            return True, f"PDF created successfully: {output_path}"
        else:
            return False, "No valid images found"
    
    except Exception as e:
        return False, f"Error creating PDF: {str(e)}"
