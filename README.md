# Dox2 - Advanced PDF Management Application

## Overview

**Dox2** is a comprehensive PDF management application built with Python and Tkinter. It provides a modern, user-friendly interface with a pleasing light blue and white theme.

## Features

### 1. **PDF Reader**
- Open and view PDF files with smooth navigation
- **Vertical Scrolling**: Continuous scrolling similar to Adobe Reader
- **RGB Color Rendering**: Full-color PDF display (not grayscale)
- **Zoom Controls**: Zoom in/out with keyboard shortcuts
- **Fit to Width**: Automatically adjust page to window width
- **Page Navigation**: Easy navigation between pages

### 2. **PDF Creator**
- **Create from Text**: Generate PDFs directly from text content
- **Create from Images**: Convert images to PDF format
- Automatic text wrapping and page breaks
- Support for multiple images in sequence

### 3. **PDF Merger**
- **Merge Multiple PDFs**: Combine two or more PDF files
- **Drag-and-Drop Interface**: Easy file ordering
- **Reorder Pages**: Move PDFs up or down in the merge order
- **Batch Processing**: Merge entire batches of documents

### 4. **File Manager**
- **Browse Files**: Navigate through directories
- **PDF Discovery**: Automatically find all PDF files
- **File Information**: View PDF metadata and properties
- **Quick Access**: Shortcuts to Home and Desktop folders
- **Copy Path**: Quick copy file paths to clipboard

## System Requirements

### Minimum
- **Python**: 3.9 or higher
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 512 MB
- **Storage**: 100 MB free space

### Recommended
- **Python**: 3.10 or higher
- **OS**: Windows 10/11
- **RAM**: 2 GB
- **Storage**: 500 MB free space

## Installation

### 1. Clone or Download the Project
```bash
# If using git
git clone https://github.com/muztaas/Dox2.git
cd Dox2
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

## Project Structure

```
Dox2/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── QUICKSTART.md          # Quick start guide
├── src/
│   ├── __init__.py
│   ├── pdf_reader.py      # PDF viewing module
│   ├── pdf_creator.py     # PDF creation module
│   ├── pdf_merger.py      # PDF merging module
│   ├── file_manager.py    # File browsing module
│   ├── ui_components.py   # Reusable UI components
│   └── utils.py           # Utility functions
├── assets/
│   └── (icons and resources)
└── venv/                  # Virtual environment
```

## Dependencies

### Core Libraries
- **PyMuPDF (fitz)** >= 1.23.0 - High-quality PDF rendering with RGB support
- **PyPDF2** >= 3.0.1 - PDF manipulation and merging
- **reportlab** >= 4.0.4 - PDF creation from scratch
- **Pillow** >= 10.0.0 - Image handling and conversion

### Built-in Libraries
- tkinter - GUI framework
- os, sys, io - System operations
- pathlib - File path handling
- threading - Background operations

## Usage Guide

### Opening a PDF
1. Click on the **"PDF Reader"** tab
2. Click **"Open PDF"** button
3. Select a PDF file from your computer
4. Use navigation buttons or scroll wheel to view pages

### Creating a PDF from Text
1. Click on the **"PDF Creator"** tab
2. Enter a title (optional)
3. Type or paste content in the text area
4. Click **"Create PDF from Text"**
5. Choose save location

### Creating a PDF from Images
1. Click on the **"PDF Creator"** tab
2. Click **"Add Images"** button
3. Select one or more image files
4. Click **"Create PDF from Images"**
5. Choose save location

### Merging PDFs
1. Click on the **"PDF Merger"** tab
2. Click **"Add PDFs"** to select files
3. Use "Move Up" and "Move Down" to arrange order
4. Click **"Merge PDFs"**
5. Choose save location for merged document

### Browsing Files
1. Click on the **"File Manager"** tab
2. Use **"Browse"** to navigate to a folder
3. Double-click a PDF to open it
4. Click **"Info"** to see file details
5. Use **"Copy Path"** to copy file location

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open PDF | Ctrl+O (in Reader) |
| Zoom In | Ctrl+Plus |
| Zoom Out | Ctrl+Minus |
| Fit to Width | Ctrl+W |
| Next Page | Page Down or Scroll Down |
| Previous Page | Page Up or Scroll Up |
| Exit Application | Alt+F4 |

## Theme Colors

### Light Blue & White Theme
- **Light Blue Background**: #E8F4F8
- **Dark Blue Accents**: #4A90E2
- **White Components**: #FFFFFF
- **Dark Gray Text**: #333333
- **Light Gray**: #F5F5F5
- **Border Gray**: #CCCCCC

This color scheme is carefully designed for long reading sessions and minimal eye strain.

## Troubleshooting

### Issue: PDF appears in grayscale
- **Cause**: RGB color rendering not working
- **Solution**: Ensure PyMuPDF version >= 1.23.0 is installed
- **Check**: Run `pip install --upgrade pymupdf`

### Issue: Application won't start
- **Cause**: Missing dependencies
- **Solution**: Reinstall all packages
- **Command**: `pip install -r requirements.txt --force-reinstall`

### Issue: PDF Reader shows white page
- **Cause**: Memory issue or corrupted PDF
- **Solution**: Try a different PDF file
- **Alternative**: Close and reopen the application

### Issue: Slow PDF rendering
- **Cause**: System resources or large PDF file
- **Solution**: Close other applications
- **Alternative**: Reduce zoom level

## Performance Tips

1. **Close Unnecessary Applications**: Free up RAM for faster rendering
2. **Use Fit Width**: Reduces unnecessary rendering overhead
3. **Update Python**: Use Python 3.11+ for better performance
4. **SSD Storage**: Store PDFs on SSD for faster access
5. **GPU Rendering**: Consider upgrading graphics for large files

## Known Limitations

- Maximum PDF size: Depends on available RAM
- Unsupported formats: Encrypted PDFs (read-only)
- Limited OCR: No optical character recognition
- No annotation tools: View-only with PDF Creator

## Development

### Adding New Features
1. Create new module in `src/` directory
2. Import in `main.py`
3. Add tab to notebook interface
4. Test thoroughly

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable names
- Include docstrings for functions
- Add comments for complex logic

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License



## Version History

### Version 1.0.0 (2025)
- Initial release
- PDF Reader with vertical scrolling
- RGB color rendering support
- PDF Creator functionality
- PDF Merger with ordering
- File Manager interface
- Light blue and white theme

## Acknowledgments

- PyMuPDF (fitz) for excellent PDF rendering
- Tkinter for reliable GUI framework
- Community feedback and contributions

## Future Enhancements

- PDF annotation tools
- OCR (Optical Character Recognition)
- Custom themes
- PDF encryption
- Batch processing
- Command-line interface
- Dark mode theme
- PDF compression
- Watermarking

---

**Enjoy using Dox2!** 📄✨
