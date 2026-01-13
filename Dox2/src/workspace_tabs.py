"""
Workspace Tabs Module for Dox2 PDF Application
Manages multiple workspace tabs where each tab can contain any module
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_reader import PDFReader
from src.pdf_creator import PDFCreator
from src.pdf_merger import PDFMerger
from src.file_manager import FileManager
from src.ui_components import StyledFrame, WHITE, DARK_BLUE


class WorkspaceTabs(StyledFrame):
    """Workspace tabs manager for multiple workspaces with different modules"""
    
    def __init__(self, parent, module_buttons_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.module_buttons_callback = module_buttons_callback
        
        # Store open workspaces and their content
        self.workspaces = {}  # {tab_id: {'frame': frame, 'module_type': type, 'module': instance}}
        self.workspace_tabs = []  # List of tab IDs in order
        self.current_tab_id = None
        self.tab_counter = 0
        
        # Setup UI
        self._setup_ui()
        
        # Create first default tab with PDF Reader
        self._add_workspace("PDF Reader")
    
    def _setup_ui(self):
        """Setup UI with tab bar and content area"""
        # Tab bar frame
        self.tab_bar = tk.Frame(self, bg=DARK_BLUE, height=50)
        self.tab_bar.pack(fill=tk.X, side=tk.TOP)
        self.tab_bar.pack_propagate(False)
        
        # Tabs container (scrollable if needed)
        self.tabs_container = tk.Frame(self.tab_bar, bg=DARK_BLUE)
        self.tabs_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add new tab button (opens PDF Reader by default)
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
            pady=8,
            command=lambda: self._add_workspace("PDF Reader")
        )
        self.add_tab_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Content area frame
        self.content_frame = tk.Frame(self, bg=WHITE)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def _add_workspace(self, module_type):
        """Add a new workspace tab with specified module"""
        # Create new tab
        tab_id = self.tab_counter
        self.tab_counter += 1
        
        # Create frame for this workspace
        workspace_frame = tk.Frame(self.content_frame, bg=WHITE)
        
        # Create module instance based on type
        module = None
        if module_type == "PDF Reader":
            module = PDFReader(workspace_frame)
        elif module_type == "PDF Creator":
            module = PDFCreator(workspace_frame)
        elif module_type == "PDF Merger":
            module = PDFMerger(workspace_frame)
        elif module_type == "File Manager":
            # Pass callback to open PDF files in Dox2
            module = FileManager(workspace_frame, on_pdf_selected=self._on_pdf_selected_from_file_manager, bg=WHITE)
        
        if module:
            module.pack(fill=tk.BOTH, expand=True)
        
        # Store workspace info
        self.workspaces[tab_id] = {
            'frame': workspace_frame,
            'module_type': module_type,
            'module': module
        }
        self.workspace_tabs.append(tab_id)
        
        # Create tab button
        self._create_workspace_tab_button(tab_id)
        
        # Switch to this tab
        self._switch_to_workspace(tab_id)
    
    def _create_workspace_tab_button(self, tab_id):
        """Create a tab button for the given workspace"""
        workspace_info = self.workspaces[tab_id]
        module_type = workspace_info['module_type']
        
        # Get tab number (position in workspace_tabs list)
        tab_number = self.workspace_tabs.index(tab_id) + 1
        
        # Create tab label: "Tab 1 - Reader" (without emoji)
        module_short_names = {
            "PDF Reader": "Reader",
            "PDF Creator": "Creator",
            "PDF Merger": "Merger",
            "File Manager": "Files"
        }
        module_short = module_short_names.get(module_type, module_type)
        tab_label = f"Tab {tab_number} - {module_short}"
        
        # Create frame for tab button and close button
        tab_btn_frame = tk.Frame(self.tabs_container, bg=DARK_BLUE)
        tab_btn_frame.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Tab button
        tab_btn = tk.Button(
            tab_btn_frame,
            text=tab_label,
            font=('Segoe UI', 9),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#6BB3FF',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self._switch_to_workspace(tab_id)
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
            command=lambda: self._close_workspace(tab_id)
        )
        close_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Store button references
        self.workspaces[tab_id]['tab_btn_frame'] = tab_btn_frame
        self.workspaces[tab_id]['tab_btn'] = tab_btn
        self.workspaces[tab_id]['close_btn'] = close_btn
    
    def _switch_to_workspace(self, tab_id):
        """Switch to the specified workspace"""
        if tab_id not in self.workspaces:
            return
        
        # Hide all frames
        for tid in self.workspace_tabs:
            self.workspaces[tid]['frame'].pack_forget()
        
        # Show selected frame
        self.workspaces[tab_id]['frame'].pack(fill=tk.BOTH, expand=True)
        self.current_tab_id = tab_id
        
        # If switching to a File Manager, refresh its custom folders
        module = self.workspaces[tab_id]['module']
        if hasattr(module, 'refresh_custom_folders'):
            module.refresh_custom_folders()
        
        # Update button styling
        for tid in self.workspace_tabs:
            if tid == tab_id:
                self.workspaces[tid]['tab_btn'].config(bg='#6BB3FF')
                self.workspaces[tid]['tab_btn_frame'].config(bg='#6BB3FF')
            else:
                self.workspaces[tid]['tab_btn'].config(bg='#5BA3F5')
                self.workspaces[tid]['tab_btn_frame'].config(bg=DARK_BLUE)
        
        # Notify parent about module change
        if self.module_buttons_callback:
            self.module_buttons_callback(self.workspaces[tab_id]['module_type'])
    
    def _close_workspace(self, tab_id):
        """Close a specific workspace"""
        if tab_id not in self.workspaces:
            return
        
        # Get the module to clean up
        module = self.workspaces[tab_id]['module']
        
        # Close PDF if it's a reader
        if hasattr(module, 'doc') and module.doc:
            module.doc.close()
        
        # Destroy the frame and buttons
        self.workspaces[tab_id]['frame'].destroy()
        self.workspaces[tab_id]['tab_btn_frame'].destroy()
        
        # Remove from tracking
        self.workspace_tabs.remove(tab_id)
        del self.workspaces[tab_id]
        
        # Renumber all remaining tabs
        self._renumber_tabs()
        
        # If this was the current tab, switch to another
        if self.current_tab_id == tab_id:
            if self.workspace_tabs:
                self._switch_to_workspace(self.workspace_tabs[0])
            else:
                self.current_tab_id = None
    
    def _renumber_tabs(self):
        """Renumber all tabs after closing one"""
        module_short_names = {
            "PDF Reader": "Reader",
            "PDF Creator": "Creator",
            "PDF Merger": "Merger",
            "File Manager": "Files"
        }
        
        for index, tab_id in enumerate(self.workspace_tabs):
            tab_number = index + 1
            module_type = self.workspaces[tab_id]['module_type']
            module_short = module_short_names.get(module_type, module_type)
            new_label = f"Tab {tab_number} - {module_short}"
            self.workspaces[tab_id]['tab_btn'].config(text=new_label)
    
    def _on_pdf_selected_from_file_manager(self, filepath):
        """Called when a PDF is selected from File Manager"""
        # Check if we can create a new tab (max 10 tabs)
        if len(self.workspace_tabs) < 10:
            # Create a new tab with PDF Reader
            self._add_workspace("PDF Reader")
            # Load the PDF in the new tab
            current_reader = self.workspaces[self.current_tab_id]['module']
            if hasattr(current_reader, 'load_pdf'):
                current_reader.load_pdf(filepath)
        else:
            # Switch to PDF Reader in current tab if available
            current_workspace = self.workspaces[self.current_tab_id]
            if current_workspace['module_type'] != "PDF Reader":
                # Switch current tab to PDF Reader
                if self.module_buttons_callback:
                    self.module_buttons_callback("PDF Reader")
                # Replace the module with PDF Reader
                workspace_frame = current_workspace['frame']
                if current_workspace['module']:
                    current_workspace['module'].destroy()
                current_workspace['module_type'] = "PDF Reader"
                module = PDFReader(workspace_frame)
                module.pack(fill=tk.BOTH, expand=True)
                current_workspace['module'] = module
                
                # Update tab label
                tab_number = self.workspace_tabs.index(self.current_tab_id) + 1
                current_workspace['tab_btn'].config(text=f"Tab {tab_number} - Reader")
            
            # Load the PDF
            current_reader = self.workspaces[self.current_tab_id]['module']
            if hasattr(current_reader, 'load_pdf'):
                current_reader.load_pdf(filepath)
