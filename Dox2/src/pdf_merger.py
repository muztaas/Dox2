"""
PDF Merger Module for Dox2 PDF Application
Provides functionality to merge multiple PDFs with drag-and-drop interface
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from PyPDF2 import PdfMerger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui_components import (
    StyledFrame, StyledLabel, StyledButton, SectionFrame, StatusBar,
    show_info_dialog, show_error_dialog,
    LIGHT_BLUE, DARK_BLUE, WHITE, DARK_GRAY
)


class PDFMerger(StyledFrame):
    """PDF Merger for combining multiple PDFs"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pdf_files = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        main_frame = StyledFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ---- PDF Selection Section ----
        selection_section = SectionFrame(main_frame, title="Select PDFs to Merge")
        selection_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(selection_section.content, bg=WHITE)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_btn = StyledButton(
            button_frame,
            text="Add PDFs",
            command=self._add_pdfs
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = StyledButton(
            button_frame,
            text="Remove Selected",
            command=self._remove_selected
        )
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = StyledButton(
            button_frame,
            text="Clear All",
            command=self._clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        move_up_btn = StyledButton(
            button_frame,
            text="Move Up",
            command=self._move_up
        )
        move_up_btn.pack(side=tk.LEFT, padx=5)
        
        move_down_btn = StyledButton(
            button_frame,
            text="Move Down",
            command=self._move_down
        )
        move_down_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_label = StyledLabel(
            selection_section.content,
            text="Select PDFs and arrange them in the desired order, then click 'Merge PDFs'",
            wraplength=400
        )
        info_label.pack(anchor='w', pady=(0, 10))
        
        # PDF list
        list_label = StyledLabel(selection_section.content, text="PDF Files:")
        list_label.pack(anchor='w', pady=(0, 5))
        
        self.pdf_listbox = tk.Listbox(
            selection_section.content,
            bg=WHITE,
            fg=DARK_GRAY,
            font=('Arial', 10),
            height=10,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground='#CCCCCC',
            selectmode=tk.SINGLE,
            activestyle='none'
        )
        self.pdf_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Merge button
        merge_btn = StyledButton(
            selection_section.content,
            text="Merge PDFs",
            command=self._merge_pdfs
        )
        merge_btn.pack(side=tk.LEFT, padx=5)
        
        # ---- Status Bar ----
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _add_pdfs(self):
        """Add PDF files for merging"""
        filepaths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for filepath in filepaths:
            if filepath not in self.pdf_files:
                self.pdf_files.append(filepath)
                self.pdf_listbox.insert(tk.END, os.path.basename(filepath))
        
        if filepaths:
            self.status_bar.set_status(f"Added {len(filepaths)} PDF(s)")
    
    def _remove_selected(self):
        """Remove selected PDF from list"""
        selection = self.pdf_listbox.curselection()
        if selection:
            index = selection[0]
            self.pdf_files.pop(index)
            self.pdf_listbox.delete(index)
            self.status_bar.set_status("PDF removed")
        else:
            messagebox.showinfo("Info", "Please select a PDF to remove")
    
    def _clear_all(self):
        """Clear all PDFs"""
        self.pdf_files.clear()
        self.pdf_listbox.delete(0, tk.END)
        self.status_bar.set_status("All PDFs cleared")
    
    def _move_up(self):
        """Move selected PDF up in the list"""
        selection = self.pdf_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a PDF to move")
            return
        
        index = selection[0]
        if index > 0:
            # Swap in list
            self.pdf_files[index], self.pdf_files[index - 1] = \
                self.pdf_files[index - 1], self.pdf_files[index]
            
            # Update listbox
            self._refresh_listbox()
            self.pdf_listbox.selection_set(index - 1)
            self.status_bar.set_status("PDF moved up")
    
    def _move_down(self):
        """Move selected PDF down in the list"""
        selection = self.pdf_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a PDF to move")
            return
        
        index = selection[0]
        if index < len(self.pdf_files) - 1:
            # Swap in list
            self.pdf_files[index], self.pdf_files[index + 1] = \
                self.pdf_files[index + 1], self.pdf_files[index]
            
            # Update listbox
            self._refresh_listbox()
            self.pdf_listbox.selection_set(index + 1)
            self.status_bar.set_status("PDF moved down")
    
    def _refresh_listbox(self):
        """Refresh the listbox display"""
        self.pdf_listbox.delete(0, tk.END)
        for filepath in self.pdf_files:
            self.pdf_listbox.insert(tk.END, os.path.basename(filepath))
    
    def _merge_pdfs(self):
        """Merge selected PDFs"""
        if not self.pdf_files:
            show_error_dialog("Error", "Please add at least one PDF file")
            return
        
        if len(self.pdf_files) < 2:
            show_error_dialog("Error", "Please add at least two PDF files to merge")
            return
        
        # Save dialog
        filepath = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            self.status_bar.set_status("Merging PDFs...")
            self.update()
            
            # Create merger
            merger = PdfMerger()
            
            # Add all PDFs in order
            for pdf_file in self.pdf_files:
                try:
                    merger.append(pdf_file)
                except Exception as e:
                    show_error_dialog(
                        "Error",
                        f"Failed to add {os.path.basename(pdf_file)}: {str(e)}"
                    )
                    merger.close()
                    return
            
            # Write merged PDF
            merger.write(filepath)
            merger.close()
            
            self.status_bar.set_status(f"Merged PDF saved: {filepath}")
            show_info_dialog(
                "Success",
                f"PDFs merged successfully:\n{filepath}"
            )
            
            # Clear list after successful merge
            self._clear_all()
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to merge PDFs: {str(e)}")
            self.status_bar.set_status("Error merging PDFs")
