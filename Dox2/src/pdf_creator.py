"""
PDF Creator Module for Dox2 PDF Application
Provides functionality to create PDFs from text and images
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui_components import (
    StyledFrame, StyledLabel, StyledButton, StyledEntry, StyledText,
    SectionFrame, Separator, StatusBar, ScrolledFrame, show_info_dialog, show_error_dialog,
    LIGHT_BLUE, DARK_BLUE, WHITE, DARK_GRAY
)


class PDFCreator(StyledFrame):
    """PDF Creator for creating PDFs from text and images"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.selected_images = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Use ScrolledFrame for proper scrolling
        scrolled = ScrolledFrame(self)
        scrolled.pack(fill=tk.BOTH, expand=True)
        main_frame = scrolled.scrollable_frame
        
        # ---- Text to PDF Section ----
        text_section = SectionFrame(main_frame, title="Create PDF from Text")
        text_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title input
        title_label = StyledLabel(text_section.content, text="PDF Title:")
        title_label.pack(anchor='w', pady=(0, 5))
        
        self.title_entry = StyledEntry(text_section.content)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Content input
        content_label = StyledLabel(text_section.content, text="Content:")
        content_label.pack(anchor='w', pady=(0, 5))
        
        self.content_text = StyledText(text_section.content, height=10)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create PDF from text button
        create_text_btn = StyledButton(
            text_section.content,
            text="Create PDF from Text",
            command=self._create_pdf_from_text
        )
        create_text_btn.pack(side=tk.LEFT, padx=5)
        
        # ---- Image to PDF Section ----
        image_section = SectionFrame(main_frame, title="Create PDF from Images")
        image_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Image selection buttons
        button_frame = tk.Frame(image_section.content, bg=WHITE)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_image_btn = StyledButton(
            button_frame,
            text="Add Images",
            command=self._add_images
        )
        add_image_btn.pack(side=tk.LEFT, padx=5)
        
        clear_images_btn = StyledButton(
            button_frame,
            text="Clear Images",
            command=self._clear_images
        )
        clear_images_btn.pack(side=tk.LEFT, padx=5)
        
        # Selected images list
        list_label = StyledLabel(image_section.content, text="Selected Images:")
        list_label.pack(anchor='w', pady=(0, 5))
        
        self.images_listbox = tk.Listbox(
            image_section.content,
            bg=WHITE,
            fg=DARK_GRAY,
            font=('Arial', 9),
            height=6,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground='#CCCCCC'
        )
        self.images_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create PDF from images button
        create_image_btn = StyledButton(
            image_section.content,
            text="Create PDF from Images",
            command=self._create_pdf_from_images
        )
        create_image_btn.pack(side=tk.LEFT, padx=5)
        
        # ---- Status Bar ----
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _add_images(self):
        """Add images for PDF creation"""
        filepaths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        for filepath in filepaths:
            if filepath not in self.selected_images:
                self.selected_images.append(filepath)
                self.images_listbox.insert(tk.END, os.path.basename(filepath))
    
    def _clear_images(self):
        """Clear selected images"""
        self.selected_images.clear()
        self.images_listbox.delete(0, tk.END)
        self.status_bar.set_status("Images cleared")
    
    def _create_pdf_from_text(self):
        """Create PDF from text content"""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not content:
            show_error_dialog("Error", "Please enter some content")
            return
        
        # Save dialog
        filepath = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Add title if provided
            if title:
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, title)
                y_position = height - 100
            else:
                y_position = height - 50
            
            # Add content
            c.setFont("Helvetica", 12)
            margin = 50
            line_height = 14
            max_width = width - 2 * margin
            
            # Simple text wrapping
            lines = content.split('\n')
            for line in lines:
                # Word wrap for long lines
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    if len(test_line) > 80:  # Approximate character limit
                        if current_line:
                            c.drawString(margin, y_position, current_line.strip())
                            y_position -= line_height
                        current_line = word + " "
                    else:
                        current_line = test_line
                
                if current_line:
                    c.drawString(margin, y_position, current_line.strip())
                    y_position -= line_height
                
                # New paragraph
                y_position -= line_height
                
                # Page break if needed
                if y_position < margin:
                    c.showPage()
                    y_position = height - margin
            
            c.save()
            self.status_bar.set_status(f"PDF created: {filepath}")
            show_info_dialog("Success", f"PDF created successfully:\n{filepath}")
            
            # Clear form
            self.title_entry.delete(0, tk.END)
            self.content_text.delete("1.0", tk.END)
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to create PDF: {str(e)}")
            self.status_bar.set_status("Error creating PDF")
    
    def _create_pdf_from_images(self):
        """Create PDF from selected images"""
        if not self.selected_images:
            show_error_dialog("Error", "Please select at least one image")
            return
        
        # Save dialog
        filepath = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Open and convert images
            images = []
            for img_path in self.selected_images:
                try:
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    show_error_dialog("Error", f"Failed to load {os.path.basename(img_path)}: {str(e)}")
                    return
            
            # Create PDF
            if images:
                images[0].save(
                    filepath,
                    save_all=True,
                    append_images=images[1:],
                    duration=100,
                    loop=0
                )
                
                self.status_bar.set_status(f"PDF created: {filepath}")
                show_info_dialog("Success", f"PDF created successfully:\n{filepath}")
                self._clear_images()
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to create PDF: {str(e)}")
            self.status_bar.set_status("Error creating PDF")
