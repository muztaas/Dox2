"""
Dox2 - Advanced PDF Management Application
Main entry point for the application

Features:
- PDF Reader with vertical scrolling and RGB color rendering
- PDF Creator for creating PDFs from text and images
- PDF Merger for combining multiple PDFs
- File Manager for browsing PDF files
- Light blue and white theme for pleasant viewing
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workspace_tabs import WorkspaceTabs
from src.ui_components import (
    configure_ttk_theme, LIGHT_BLUE, DARK_BLUE, WHITE
)


class Dox2Application:
    """Main application class for Dox2"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Dox2 - PDF Management Application")
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)
        
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'Images', 'D2_logo_48.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Configure ttk theme
        configure_ttk_theme()
        
        # Setup main UI
        self._setup_ui()
        
        # Configure window theme
        self._configure_window()
    
    def _configure_window(self):
        """Configure window colors and appearance"""
        self.root.config(bg=WHITE)
    
    def _setup_ui(self):
        """Setup main UI with workspace tabs"""
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg=WHITE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame with title and module tabs
        header_frame = tk.Frame(main_frame, bg=DARK_BLUE, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Application title in header
        title_label = tk.Label(
            header_frame,
            text="📄 Dox2",
            font=('Segoe UI', 20, 'bold'),
            bg=DARK_BLUE,
            fg=WHITE
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Separator
        separator = tk.Frame(header_frame, bg='#3A7BC8', width=2, height=40)
        separator.pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        # Create module buttons frame in header
        buttons_frame = tk.Frame(header_frame, bg=DARK_BLUE)
        buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Module selection buttons (quick access to switch module in current workspace)
        tab_names = [
            ("📖 PDF Reader", "PDF Reader"),
            ("✏️ PDF Creator", "PDF Creator"),
            ("🔗 PDF Merger", "PDF Merger"),
            ("📁 File Manager", "File Manager")
        ]
        
        self.module_buttons_list = []
        self.current_module = "PDF Reader"
        
        for tab_text, module_name in tab_names:
            btn = tk.Button(
                buttons_frame,
                text=tab_text,
                font=('Segoe UI', 9),
                bg='#5BA3F5',
                fg=WHITE,
                activebackground=WHITE,
                activeforeground='#5BA3F5',
                relief=tk.FLAT,
                padx=12,
                pady=6,
                command=lambda mod=module_name: self._switch_current_workspace_module(mod)
            )
            btn.pack(side=tk.LEFT, padx=4)
            self.module_buttons_list.append((btn, module_name))
        
        # Create workspace tabs below header (with callback already set)
        self.workspace_tabs = WorkspaceTabs(main_frame, module_buttons_callback=self._on_workspace_module_changed, bg=WHITE)
        self.workspace_tabs.pack(fill=tk.BOTH, expand=True)
        
        # Show first module button as selected
        self._update_module_button_styles()
    
    def _switch_current_workspace_module(self, module_name):
        """Switch module in current workspace"""
        if self.workspace_tabs.current_tab_id is None:
            return
        
        current_tab_id = self.workspace_tabs.current_tab_id
        current_workspace = self.workspace_tabs.workspaces[current_tab_id]
        
        # If already this module, do nothing
        if current_workspace['module_type'] == module_name:
            return
        
        # Get the workspace frame
        workspace_frame = current_workspace['frame']
        
        # Destroy old module
        if current_workspace['module']:
            if hasattr(current_workspace['module'], 'doc') and current_workspace['module'].doc:
                current_workspace['module'].doc.close()
            current_workspace['module'].destroy()
        
        # Create new module
        from src.pdf_reader import PDFReader
        from src.pdf_creator import PDFCreator
        from src.pdf_merger import PDFMerger
        from src.file_manager import FileManager
        
        module = None
        if module_name == "PDF Reader":
            module = PDFReader(workspace_frame)
        elif module_name == "PDF Creator":
            module = PDFCreator(workspace_frame)
        elif module_name == "PDF Merger":
            module = PDFMerger(workspace_frame)
        elif module_name == "File Manager":
            # Pass callback to open PDF files in Dox2
            module = FileManager(workspace_frame, on_pdf_selected=self.workspace_tabs._on_pdf_selected_from_file_manager, bg=WHITE)
        
        if module:
            module.pack(fill=tk.BOTH, expand=True)
        
        # Update workspace info
        current_workspace['module_type'] = module_name
        current_workspace['module'] = module
        
        # Update tab button label
        module_short_names = {
            "PDF Reader": "Reader",
            "PDF Creator": "Creator",
            "PDF Merger": "Merger",
            "File Manager": "Files"
        }
        module_short = module_short_names.get(module_name, "")
        
        # Get tab number
        tab_number = self.workspace_tabs.workspace_tabs.index(current_tab_id) + 1
        current_workspace['tab_btn'].config(text=f"Tab {tab_number} - {module_short}")
        
        # Update module button styles
        self.current_module = module_name
        self._update_module_button_styles()
    
    def _on_workspace_module_changed(self, module_name):
        """Called when workspace module changes (e.g., switching tabs)"""
        self.current_module = module_name
        self._update_module_button_styles()
    
    def _update_module_button_styles(self):
        """Update module button styling based on current module"""
        for btn, module_name in self.module_buttons_list:
            if module_name == self.current_module:
                btn.config(bg=WHITE, fg='#5BA3F5')
            else:
                btn.config(bg='#5BA3F5', fg=WHITE)
    
    def _show_about(self):
        """Show about dialog"""
        from tkinter import messagebox
        about_text = """Dox2 - Advanced PDF Management Application

Version: 1.0.0

Features:
• PDF Reader with zoom and scrolling
• RGB color rendering support
• PDF Creator from text and images
• PDF Merger with multiple files
• File Manager for browsing
• Modern material design UI

Libraries:
PyMuPDF (fitz) • reportlab • PyPDF2 • Pillow

Copyright © 2025
        """
        messagebox.showinfo("About Dox2", about_text)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        from tkinter import messagebox
        shortcuts_text = """Keyboard Shortcuts

PDF Reader:
• Scroll with Mouse Wheel - Navigate vertically
• Shift + Scroll - Navigate horizontally
• Zoom In/Out Buttons - Change zoom level
• Fit Width - Reset to 100% zoom
• Arrow Buttons - Go to next/previous page

General:
• Alt+F4 - Close application
• Ctrl+Tab - Switch between tabs

Tips:
• Use Zoom +/- buttons for detailed viewing
• Scroll bars appear when content exceeds window
• Press Fit Width to reset zoom to 100%
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = Dox2Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
