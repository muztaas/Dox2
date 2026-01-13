"""
File Manager Module for Dox2 PDF Application
Provides file browser and management capabilities
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui_components import (
    StyledFrame, StyledLabel, StyledButton, SectionFrame, StatusBar, ScrolledFrame,
    show_info_dialog, show_error_dialog,
    LIGHT_BLUE, DARK_BLUE, WHITE, DARK_GRAY
)
from src.utils import get_all_pdf_files, get_pdf_info, format_file_size


class FileManager(StyledFrame):
    """File Manager for browsing and managing PDF files"""
    
    def __init__(self, parent, on_pdf_selected=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.current_directory = str(Path.home() / "Documents")
        self.on_pdf_selected = on_pdf_selected  # Callback when PDF is selected
        self.custom_folders = []  # User-added folder shortcuts
        self._load_custom_folders()
        self._setup_ui()
        self._load_directory()
    
    def _load_custom_folders(self):
        """Load custom folder shortcuts from config file"""
        config_file = Path.home() / ".dox2_folders.txt"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    lines = f.readlines()
                    self.custom_folders = [line.strip() for line in lines if line.strip() and os.path.isdir(line.strip())]
            except Exception as e:
                print(f"Error loading custom folders: {e}")
    
    def refresh_custom_folders(self):
        """Refresh custom folder buttons when tab is switched"""
        # Load the latest custom folders from file
        self._load_custom_folders()
        
        # Clear existing custom folder buttons
        for folder_path, (btn_frame, _, _) in list(self.folder_buttons.items()):
            btn_frame.destroy()
        
        self.folder_buttons.clear()
        self.folder_delete_buttons.clear()
        self.show_delete_buttons = False
        
        # Reload custom folder buttons from the updated list
        for folder_path in self.custom_folders:
            if os.path.isdir(folder_path):
                folder_name = os.path.basename(folder_path)
                self._add_custom_folder_button(folder_path, folder_name)
        
        # Update manage delete button visibility
        self._update_manage_delete_button_visibility()
        
        # Update canvas scroll region
        self.nav_buttons_frame.update_idletasks()
        self.nav_canvas.config(scrollregion=self.nav_canvas.bbox('all'))
        self._update_scrollbar_visibility()
    
    def _save_custom_folders(self):
        """Save custom folder shortcuts to config file"""
        config_file = Path.home() / ".dox2_folders.txt"
        try:
            with open(config_file, 'w') as f:
                for folder in self.custom_folders:
                    f.write(f"{folder}\n")
        except Exception as e:
            print(f"Error saving custom folders: {e}")
    
    def _setup_ui(self):
        """Setup UI components"""
        # Use ScrolledFrame for proper scrolling
        scrolled = ScrolledFrame(self)
        scrolled.pack(fill=tk.BOTH, expand=True)
        main_frame = scrolled.scrollable_frame
        
        # ---- Navigation Section with Smart Scrolling ----
        nav_section = SectionFrame(main_frame, title="Navigation")
        nav_section.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Create a canvas with horizontal scrollbar for navigation buttons
        nav_canvas_frame = tk.Frame(nav_section.content, bg=WHITE)
        nav_canvas_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Horizontal scrollbar (will be hidden if not needed)
        self.h_scrollbar = tk.Scrollbar(nav_canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar_id = None  # Track if scrollbar is packed
        
        # Canvas for buttons
        self.nav_canvas = tk.Canvas(
            nav_canvas_frame,
            bg=WHITE,
            highlightthickness=0,
            height=45,
            xscrollcommand=self._on_scrollbar_update
        )
        self.nav_canvas.pack(side=tk.TOP, fill=tk.X)
        self.h_scrollbar.config(command=self.nav_canvas.xview)
        
        # Frame inside canvas to hold buttons
        self.nav_buttons_frame = tk.Frame(self.nav_canvas, bg=WHITE)
        self.nav_canvas_window = self.nav_canvas.create_window(0, 0, window=self.nav_buttons_frame, anchor='nw')
        
        # Bind mousewheel to canvas for horizontal scrolling
        self.nav_canvas.bind('<MouseWheel>', self._on_nav_scroll)
        self.nav_canvas.bind('<Button-4>', self._on_nav_scroll)  # Linux scroll up
        self.nav_canvas.bind('<Button-5>', self._on_nav_scroll)  # Linux scroll down
        
        # Add default buttons
        self._create_nav_button("Browse", self._browse_directory, is_default=True)
        self._create_nav_button("Home", self._go_home, is_default=True)
        self._create_nav_button("Desktop", self._go_desktop, is_default=True)
        self._create_nav_button("Downloads", self._go_downloads, is_default=True)
        
        # Store folder buttons for management
        self.folder_buttons = {}  # {folder_path: button_widget}
        self.folder_delete_buttons = {}  # {folder_path: delete_button}
        self.show_delete_buttons = False  # Toggle for delete button visibility
        
        # Create control buttons frame (at extreme right)
        self.control_buttons_frame = tk.Frame(self.nav_buttons_frame, bg=WHITE)
        self.control_buttons_frame.pack(side=tk.RIGHT, padx=(3, 0))
        
        # Add plus button (green +) for adding custom folders
        self._create_add_folder_button()
        
        # Add minus button for managing custom folders (only show if there are custom folders)
        self._create_manage_delete_button()
        
        # Load previously saved custom folders AFTER manage_delete_btn is created
        for folder_path in self.custom_folders:
            if os.path.isdir(folder_path):
                folder_name = os.path.basename(folder_path)
                self._add_custom_folder_button(folder_path, folder_name)
        
        # Update canvas scroll region and check if scrollbar is needed
        self.nav_buttons_frame.update_idletasks()
        self.nav_canvas.config(scrollregion=self.nav_canvas.bbox('all'))
        self._update_scrollbar_visibility()
        
        # Path label
        path_label = StyledLabel(nav_section.content, text="Current Path:")
        path_label.pack(anchor='w', pady=(5, 0))
        
        self.path_display = tk.Label(
            nav_section.content,
            text=self.current_directory,
            bg=WHITE,
            fg=DARK_GRAY,
            font=('Arial', 9),
            wraplength=500,
            justify=tk.LEFT
        )
        self.path_display.pack(anchor='w', fill=tk.X)
        
        # ---- File List Section ----
        file_section = SectionFrame(main_frame, title="PDF Files")
        file_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list
        list_label = StyledLabel(file_section.content, text="Available PDFs:")
        list_label.pack(anchor='w', pady=(0, 5))
        
        self.file_listbox = tk.Listbox(
            file_section.content,
            bg=WHITE,
            fg=DARK_GRAY,
            font=('Arial', 10),
            height=12,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground='#CCCCCC',
            selectmode=tk.SINGLE,
            activestyle='none'
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.file_listbox.bind('<Double-Button-1>', self._on_file_double_click)
        
        # ---- File Operations Section ----
        ops_section = SectionFrame(main_frame, title="File Operations")
        ops_section.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Operation buttons
        button_frame = tk.Frame(ops_section.content, bg=WHITE)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        open_btn = StyledButton(
            button_frame,
            text="Open",
            command=self._open_file,
            pady=10
        )
        open_btn.pack(side=tk.LEFT, padx=5)
        
        info_btn = StyledButton(
            button_frame,
            text="Info",
            command=self._show_file_info,
            pady=10
        )
        info_btn.pack(side=tk.LEFT, padx=5)
        
        copy_path_btn = StyledButton(
            button_frame,
            text="Copy Path",
            command=self._copy_file_path,
            pady=10
        )
        copy_path_btn.pack(side=tk.LEFT, padx=5)
        
        # ---- Status Bar ----
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _load_directory(self):
        """Load and display PDFs in current directory"""
        try:
            pdf_files = get_all_pdf_files(self.current_directory)
            
            self.file_listbox.delete(0, tk.END)
            for pdf_file in pdf_files:
                self.file_listbox.insert(tk.END, os.path.basename(pdf_file))
            
            self.path_display.config(text=self.current_directory)
            self.status_bar.set_status(f"Found {len(pdf_files)} PDF(s)")
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to load directory: {str(e)}")
            self.status_bar.set_status("Error loading directory")
    
    def _browse_directory(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory(
            title="Select Directory",
            initialdir=self.current_directory
        )
        
        if directory:
            self.current_directory = directory
            self._load_directory()
    
    def _go_home(self):
        """Go to home directory"""
        self.current_directory = str(Path.home())
        self._load_directory()
    
    def _go_desktop(self):
        """Go to desktop directory"""
        self.current_directory = str(Path.home() / "Desktop")
        self._load_directory()
    
    def _go_downloads(self):
        """Go to downloads directory"""
        self.current_directory = str(Path.home() / "Downloads")
        self._load_directory()
    
    def _create_nav_button(self, text, command, is_default=False):
        """Create a navigation button"""
        btn = tk.Button(
            self.nav_buttons_frame,
            text=text,
            font=('Segoe UI', 9),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#6BB3FF',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            command=command
        )
        btn.pack(side=tk.LEFT, padx=3)
        return btn
    
    def _create_add_folder_button(self):
        """Create the add folder button (green + on light blue background)"""
        add_btn = tk.Button(
            self.control_buttons_frame,
            text="+",
            font=('Segoe UI', 11, 'bold'),
            bg='#E8F4F8',  # Light blue background
            fg='#2ECC71',  # Green plus sign
            activebackground='#D0E8F0',
            activeforeground='#27AE60',
            relief=tk.FLAT,
            bd=2,
            highlightthickness=2,
            highlightbackground='#5BA3F5',
            padx=8,
            pady=4,
            command=self._add_custom_folder
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 3))
        self.add_folder_btn = add_btn
    
    def _create_manage_delete_button(self):
        """Create the manage delete button (red minus on right side)"""
        # Create button - will show/hide based on custom folders
        self.manage_delete_btn = tk.Button(
            self.control_buttons_frame,
            text="−",
            font=('Segoe UI', 11, 'bold'),
            bg='#E74C3C',  # Red background
            fg=WHITE,
            activebackground='#C0392B',
            relief=tk.FLAT,
            padx=8,
            pady=4,
            command=self._toggle_delete_buttons
        )
        self._update_manage_delete_button_visibility()
    
    def _toggle_delete_buttons(self):
        """Toggle visibility of delete buttons on custom folders"""
        self.show_delete_buttons = not self.show_delete_buttons
        for folder_path, delete_btn in self.folder_delete_buttons.items():
            if self.show_delete_buttons:
                delete_btn.pack(side=tk.RIGHT, padx=(1, 0))
            else:
                delete_btn.pack_forget()
    
    def _update_manage_delete_button_visibility(self):
        """Show/hide the manage delete button based on custom folders"""
        if len(self.custom_folders) > 0:
            if not self.manage_delete_btn.winfo_manager():  # Only pack if not already packed
                self.manage_delete_btn.pack(side=tk.RIGHT, padx=(1, 0))
        else:
            self.manage_delete_btn.pack_forget()
    
    def _update_scrollbar_visibility(self):
        """Show/hide scrollbar and adjust canvas based on content width"""
        self.nav_buttons_frame.update_idletasks()
        canvas_width = self.nav_canvas.winfo_width()
        scrollregion = self.nav_canvas.bbox('all')
        
        if scrollregion:
            content_width = scrollregion[2] - scrollregion[0]
            
            # If content fits in canvas, hide scrollbar
            if content_width <= canvas_width:
                self.h_scrollbar.pack_forget()
                self.h_scrollbar_id = None
            else:
                # Show scrollbar if not already visible
                if self.h_scrollbar_id is None:
                    self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                    self.h_scrollbar_id = True
        
        self.nav_canvas.config(scrollregion=scrollregion)
    
    def _on_scrollbar_update(self, *args):
        """Handle scrollbar updates and manage visibility"""
        self.h_scrollbar.set(*args)
        # Schedule visibility check after a short delay
        self.after(100, self._update_scrollbar_visibility)
    
    def _add_custom_folder(self):
        """Add a custom folder to shortcuts"""
        if len(self.custom_folders) >= 10:
            show_error_dialog("Limit Reached", "Maximum 10 custom folders allowed")
            return
        
        folder = filedialog.askdirectory(
            title="Select Folder to Add",
            initialdir=self.current_directory
        )
        
        if folder:
            if folder not in self.custom_folders:
                self.custom_folders.append(folder)
                folder_name = os.path.basename(folder)
                self._add_custom_folder_button(folder, folder_name)
                self._save_custom_folders()
                self.status_bar.set_status(f"Added: {folder_name}")
            else:
                show_info_dialog("Info", "Folder already added")
    
    def _add_custom_folder_button(self, folder_path, folder_name):
        """Add a button for custom folder with hidden delete option"""
        # Create frame for button and delete button
        btn_frame = tk.Frame(self.nav_buttons_frame, bg=WHITE)
        btn_frame.pack(side=tk.LEFT, padx=2)
        
        # Folder button
        folder_btn = tk.Button(
            btn_frame,
            text=folder_name,
            font=('Segoe UI', 9),
            bg='#5BA3F5',
            fg=WHITE,
            activebackground='#6BB3FF',
            activeforeground=WHITE,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            command=lambda: self._navigate_to_folder(folder_path)
        )
        folder_btn.pack(side=tk.LEFT)
        
        # Delete button (red minus) - initially hidden, shown when manage delete button is clicked
        del_btn = tk.Button(
            btn_frame,
            text="−",
            font=('Segoe UI', 11, 'bold'),
            bg='#E74C3C',  # Red background
            fg=WHITE,
            activebackground='#C0392B',
            relief=tk.FLAT,
            padx=4,
            pady=4,
            command=lambda: self._remove_custom_folder(folder_path, btn_frame)
        )
        # Store button but don't pack it yet
        self.folder_delete_buttons[folder_path] = del_btn
        
        # Store button reference
        self.folder_buttons[folder_path] = (btn_frame, folder_btn, del_btn)
        
        # Update visibility of manage delete button
        self._update_manage_delete_button_visibility()
        
        # Update canvas scroll region and check if scrollbar is needed
        self.nav_buttons_frame.update_idletasks()
        self.nav_canvas.config(scrollregion=self.nav_canvas.bbox('all'))
        self._update_scrollbar_visibility()
    
    def _navigate_to_folder(self, folder_path):
        """Navigate to a custom folder"""
        if os.path.isdir(folder_path):
            self.current_directory = folder_path
            self._load_directory()
        else:
            show_error_dialog("Error", f"Folder not found: {folder_path}")
            # Remove the folder if it doesn't exist
            if folder_path in self.custom_folders:
                self.custom_folders.remove(folder_path)
                if folder_path in self.folder_buttons:
                    self.folder_buttons[folder_path][0].destroy()
                    del self.folder_buttons[folder_path]
                if folder_path in self.folder_delete_buttons:
                    del self.folder_delete_buttons[folder_path]
                self.show_delete_buttons = False
                self._update_manage_delete_button_visibility()
    
    def _remove_custom_folder(self, folder_path, btn_frame):
        """Remove custom folder button"""
        if folder_path in self.custom_folders:
            self.custom_folders.remove(folder_path)
            btn_frame.destroy()
            if folder_path in self.folder_buttons:
                del self.folder_buttons[folder_path]
            if folder_path in self.folder_delete_buttons:
                del self.folder_delete_buttons[folder_path]
            self._save_custom_folders()
            self.status_bar.set_status(f"Removed folder shortcut")
            
            # Reset delete button state and hide if no custom folders
            self.show_delete_buttons = False
            self._update_manage_delete_button_visibility()
        
        # Update canvas scroll region and check if scrollbar is needed
        self.nav_buttons_frame.update_idletasks()
        self.nav_canvas.config(scrollregion=self.nav_canvas.bbox('all'))
        self._update_scrollbar_visibility()
    
    def _on_nav_scroll(self, event):
        """Handle scrolling in navigation canvas"""
        if event.delta > 0 or event.num == 4:  # Scroll up/left
            self.nav_canvas.xview_scroll(-3, 'units')
        else:  # Scroll down/right
            self.nav_canvas.xview_scroll(3, 'units')
    
    def _get_selected_file(self):
        """Get selected file path"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.file_listbox.get(index)
            return os.path.join(self.current_directory, filename)
        return None
    
    def _open_file(self):
        """Open selected PDF file in Dox2"""
        filepath = self._get_selected_file()
        
        if not filepath:
            show_error_dialog("Error", "Please select a PDF file")
            return
        
        try:
            # If callback is set, use it to open the PDF in Dox2
            if self.on_pdf_selected:
                self.on_pdf_selected(filepath)
                self.status_bar.set_status(f"Opened: {os.path.basename(filepath)}")
            else:
                # Fallback to default application if no callback is set
                if sys.platform == 'win32':
                    os.startfile(filepath)
                elif sys.platform == 'darwin':  # macOS
                    import subprocess
                    subprocess.Popen(['open', filepath])
                else:  # Linux
                    import subprocess
                    subprocess.Popen(['xdg-open', filepath])
                
                self.status_bar.set_status(f"Opened: {os.path.basename(filepath)}")
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to open file: {str(e)}")
    
    def _show_file_info(self):
        """Show information about selected PDF"""
        filepath = self._get_selected_file()
        
        if not filepath:
            show_error_dialog("Error", "Please select a PDF file")
            return
        
        try:
            info = get_pdf_info(filepath)
            
            if 'error' in info:
                show_error_dialog("Error", f"Failed to get info: {info['error']}")
                return
            
            file_size = format_file_size(info.get('file_size', 0))
            
            info_text = f"""
File: {os.path.basename(filepath)}
Size: {file_size}
Pages: {info.get('pages', 'Unknown')}
Title: {info.get('title', 'Unknown')}
Author: {info.get('author', 'Unknown')}
Subject: {info.get('subject', 'Unknown')}
Creator: {info.get('creator', 'Unknown')}
            """
            
            show_info_dialog("PDF Information", info_text.strip())
            self.status_bar.set_status(f"Displayed info for: {os.path.basename(filepath)}")
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to get file info: {str(e)}")
    
    def _copy_file_path(self):
        """Copy file path to clipboard"""
        filepath = self._get_selected_file()
        
        if not filepath:
            show_error_dialog("Error", "Please select a PDF file")
            return
        
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(filepath)
            self.parent.update()
            
            self.status_bar.set_status(f"Copied: {filepath}")
            messagebox.showinfo("Success", f"Path copied to clipboard:\n{filepath}")
        
        except Exception as e:
            show_error_dialog("Error", f"Failed to copy path: {str(e)}")
    
    def _on_file_double_click(self, event):
        """Handle double-click on file"""
        self._open_file()
