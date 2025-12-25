"""
PDF Reader Tabs Module for Dox2 PDF Application
Manages multiple PDF documents in tabs similar to Adobe Acrobat DC
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_reader import PDFReader
from src.ui_components import StyledFrame, WHITE, DARK_BLUE


class PDFReaderTabs(StyledFrame):
    """PDF Reader with tab support for multiple documents"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Store open PDFs and their tabs
        self.open_pdfs = {}  # {tab_id: {'frame': frame, 'reader': PDFReader, 'filepath': filepath}}
        self.pdf_tabs = []  # List of tab IDs in order
        self.current_tab_id = None
        self.tab_counter = 0
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI with tab bar and content area"""
        # Tab bar frame
        self.tab_bar = tk.Frame(self, bg=DARK_BLUE, height=35)
        self.tab_bar.pack(fill=tk.X, side=tk.TOP)
        self.tab_bar.pack_propagate(False)
        
        # Tabs container (scrollable if needed)
        self.tabs_container = tk.Frame(self.tab_bar, bg=DARK_BLUE)
        self.tabs_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add new tab button
        self.add_tab_btn = tk.Button(
            self.tab_bar,
            text="+ New Tab",
            font=('Segoe UI', 9),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#6BB3FF',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._add_new_tab
        )
        self.add_tab_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Content area frame
        self.content_frame = tk.Frame(self, bg=WHITE)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def _add_new_tab(self):
        """Add a new PDF tab and open file dialog"""
        # Create new tab
        tab_id = self.tab_counter
        self.tab_counter += 1
        
        # Create frame for this PDF
        pdf_frame = tk.Frame(self.content_frame, bg=WHITE)
        
        # Create PDF Reader instance
        pdf_reader = PDFReader(pdf_frame)
        pdf_reader.pack(fill=tk.BOTH, expand=True)
        
        # Store tab info
        self.open_pdfs[tab_id] = {
            'frame': pdf_frame,
            'reader': pdf_reader,
            'filepath': None,
            'filename': 'Untitled'
        }
        self.pdf_tabs.append(tab_id)
        
        # Create tab button
        self._create_tab_button(tab_id)
        
        # Open file dialog
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filepath:
            self.open_pdfs[tab_id]['filepath'] = filepath
            self.open_pdfs[tab_id]['filename'] = os.path.basename(filepath)
            pdf_reader.load_pdf(filepath)
            self._switch_to_tab(tab_id)
        else:
            # If no file selected, remove the tab
            self._close_tab(tab_id)
    
    def _create_tab_button(self, tab_id):
        """Create a tab button for the given tab ID"""
        tab_info = self.open_pdfs[tab_id]
        filename = tab_info['filename']
        
        # Truncate filename if too long
        if len(filename) > 20:
            filename = filename[:17] + "..."
        
        # Create frame for tab button and close button
        tab_btn_frame = tk.Frame(self.tabs_container, bg=DARK_BLUE)
        tab_btn_frame.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Tab button
        tab_btn = tk.Button(
            tab_btn_frame,
            text=filename,
            font=('Segoe UI', 9),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#6BB3FF',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=lambda: self._switch_to_tab(tab_id)
        )
        tab_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = tk.Button(
            tab_btn_frame,
            text="✕",
            font=('Segoe UI', 8),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#FF6B6B',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=4,
            pady=4,
            command=lambda: self._close_tab(tab_id)
        )
        close_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Store button references
        self.open_pdfs[tab_id]['tab_btn_frame'] = tab_btn_frame
        self.open_pdfs[tab_id]['tab_btn'] = tab_btn
        self.open_pdfs[tab_id]['close_btn'] = close_btn
    
    def _switch_to_tab(self, tab_id):
        """Switch to the specified tab"""
        if tab_id not in self.open_pdfs:
            return
        
        # Hide all frames
        for tid in self.pdf_tabs:
            self.open_pdfs[tid]['frame'].pack_forget()
        
        # Show selected frame
        self.open_pdfs[tab_id]['frame'].pack(fill=tk.BOTH, expand=True)
        self.current_tab_id = tab_id
        
        # Update button styling
        for tid in self.pdf_tabs:
            if tid == tab_id:
                self.open_pdfs[tid]['tab_btn'].config(bg='#6BB3FF')
                self.open_pdfs[tid]['tab_btn_frame'].config(bg='#6BB3FF')
            else:
                self.open_pdfs[tid]['tab_btn'].config(bg='#5BA3F5')
                self.open_pdfs[tid]['tab_btn_frame'].config(bg=DARK_BLUE)
    
    def _close_tab(self, tab_id):
        """Close a specific tab"""
        if tab_id not in self.open_pdfs:
            return
        
        # Get the reader to close the document
        pdf_reader = self.open_pdfs[tab_id]['reader']
        if pdf_reader.doc:
            pdf_reader.doc.close()
        
        # Destroy the frame and buttons
        self.open_pdfs[tab_id]['frame'].destroy()
        self.open_pdfs[tab_id]['tab_btn_frame'].destroy()
        
        # Remove from tracking
        self.pdf_tabs.remove(tab_id)
        del self.open_pdfs[tab_id]
        
        # If this was the current tab, switch to another
        if self.current_tab_id == tab_id:
            if self.pdf_tabs:
                self._switch_to_tab(self.pdf_tabs[0])
            else:
                self.current_tab_id = None
    
    def open_pdf(self, filepath):
        """Open a PDF file in a new tab"""
        # Create new tab
        tab_id = self.tab_counter
        self.tab_counter += 1
        
        # Create frame for this PDF
        pdf_frame = tk.Frame(self.content_frame, bg=WHITE)
        
        # Create PDF Reader instance
        pdf_reader = PDFReader(pdf_frame)
        pdf_reader.pack(fill=tk.BOTH, expand=True)
        
        # Store tab info
        self.open_pdfs[tab_id] = {
            'frame': pdf_frame,
            'reader': pdf_reader,
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        }
        self.pdf_tabs.append(tab_id)
        
        # Create tab button
        self._create_tab_button(tab_id)
        
        # Load the PDF
        pdf_reader.load_pdf(filepath)
        
        # Switch to this tab
        self._switch_to_tab(tab_id)
