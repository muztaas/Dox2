"""
UI Components Module for Dox2 PDF Application
Provides reusable components styled with light blue and white theme
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import os

# Color Theme
LIGHT_BLUE = "#E8F4F8"
DARK_BLUE = "#4A90E2"
WHITE = "#FFFFFF"
DARK_GRAY = "#333333"
LIGHT_GRAY = "#F5F5F5"
BORDER_GRAY = "#CCCCCC"


class StyledButton(tk.Button):
    """Custom button styled with material design and light blue/white theme"""
    
    def __init__(self, parent, text="", command=None, **kwargs):
        style_config = {
            'bg': DARK_BLUE,
            'fg': WHITE,
            'font': ('Segoe UI', 10, 'bold'),
            'padx': 18,
            'pady': 10,
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'activebackground': '#2E7FC1',
            'activeforeground': WHITE,
            'bd': 0,
            'highlightthickness': 0,
            'overrelief': tk.FLAT
        }
        style_config.update(kwargs)
        super().__init__(parent, text=text, command=command, **style_config)
        
        # Bind hover effects for material design feedback
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _on_enter(self, event):
        """Hover effect - lighten color"""
        self.config(bg='#5BA3F5')
    
    def _on_leave(self, event):
        """Return to normal color"""
        self.config(bg=DARK_BLUE)
    
    def _on_press(self, event):
        """Press effect - darken color"""
        self.config(bg='#2E7FC1')
    
    def _on_release(self, event):
        """Release effect - return to hover color"""
        self.config(bg='#5BA3F5')


class StyledLabel(tk.Label):
    """Custom label styled with light blue and white theme"""
    
    def __init__(self, parent, text="", **kwargs):
        style_config = {
            'bg': WHITE,
            'fg': DARK_GRAY,
            'font': ('Segoe UI', 10)
        }
        style_config.update(kwargs)
        super().__init__(parent, text=text, **style_config)


class TitleLabel(tk.Label):
    """Large title label for section headers"""
    
    def __init__(self, parent, text="", **kwargs):
        style_config = {
            'bg': LIGHT_BLUE,
            'fg': DARK_BLUE,
            'font': ('Segoe UI', 14, 'bold'),
            'pady': 10
        }
        style_config.update(kwargs)
        super().__init__(parent, text=text, **style_config)


class StyledFrame(tk.Frame):
    """Custom frame styled with light blue and white theme"""
    
    def __init__(self, parent, **kwargs):
        style_config = {
            'bg': WHITE,
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 1,
            'highlightbackground': BORDER_GRAY,
            'highlightcolor': DARK_BLUE
        }
        style_config.update(kwargs)
        super().__init__(parent, **style_config)


class SectionFrame(tk.Frame):
    """Frame for organizing sections with light blue header"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=WHITE, **kwargs)
        
        # Header
        header = tk.Frame(self, bg=LIGHT_BLUE, height=35)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text=title,
            bg=LIGHT_BLUE,
            fg=DARK_BLUE,
            font=('Arial', 12, 'bold'),
            padx=15
        )
        title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Content area
        self.content = tk.Frame(self, bg=WHITE)
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


class StyledEntry(tk.Entry):
    """Custom entry widget styled with light blue and white theme"""
    
    def __init__(self, parent, **kwargs):
        style_config = {
            'font': ('Segoe UI', 10),
            'bg': WHITE,
            'fg': DARK_GRAY,
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 1,
            'highlightbackground': BORDER_GRAY,
            'highlightcolor': DARK_BLUE
        }
        style_config.update(kwargs)
        super().__init__(parent, **style_config)


class StyledText(tk.Text):
    """Custom text widget styled with light blue and white theme"""
    
    def __init__(self, parent, **kwargs):
        style_config = {
            'font': ('Segoe UI', 10),
            'bg': WHITE,
            'fg': DARK_GRAY,
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 1,
            'highlightbackground': BORDER_GRAY,
            'highlightcolor': DARK_BLUE
        }
        style_config.update(kwargs)
        super().__init__(parent, **style_config)


class StyledListbox(tk.Listbox):
    """Custom listbox styled with light blue and white theme"""
    
    def __init__(self, parent, **kwargs):
        style_config = {
            'font': ('Segoe UI', 10),
            'bg': WHITE,
            'fg': DARK_GRAY,
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 1,
            'highlightbackground': BORDER_GRAY,
            'highlightcolor': DARK_BLUE,
            'selectbackground': DARK_BLUE,
            'selectforeground': WHITE,
            'activestyle': 'none'
        }
        style_config.update(kwargs)
        super().__init__(parent, **style_config)


class MenuBar(tk.Menu):
    """Custom menu bar styled with light blue and white theme"""
    
    def __init__(self, parent, **kwargs):
        style_config = {
            'bg': WHITE,
            'fg': DARK_GRAY,
            'activebackground': LIGHT_BLUE,
            'activeforeground': DARK_BLUE,
            'font': ('Arial', 10)
        }
        style_config.update(kwargs)
        super().__init__(parent, **style_config)


class Separator(tk.Frame):
    """Horizontal separator line"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BORDER_GRAY, height=1, **kwargs)


class StatusBar(tk.Frame):
    """Status bar at the bottom of the application with file info and zoom"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=LIGHT_BLUE, height=25, **kwargs)
        self.pack_propagate(False)
        
        # Left label for file path/name (80%)
        self.file_label = tk.Label(
            self,
            text="Ready",
            bg=LIGHT_BLUE,
            fg=DARK_GRAY,
            font=('Segoe UI', 9),
            padx=10,
            anchor='w'
        )
        self.file_label.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Right label for zoom (20%)
        self.zoom_label = tk.Label(
            self,
            text="",
            bg=LIGHT_BLUE,
            fg=DARK_GRAY,
            font=('Segoe UI', 9),
            padx=10,
            anchor='e'
        )
        self.zoom_label.pack(fill=tk.BOTH, side=tk.RIGHT, padx=(0, 10))
        
        self.full_path = ""  # Store full path for tooltip
    
    def set_file_info(self, filepath, zoom_text=""):
        """Update file info with truncation and tooltip"""
        self.full_path = filepath
        
        # Truncate filepath for display
        display_text = self._truncate_path(filepath)
        
        self.file_label.config(text=display_text)
        self.zoom_label.config(text=zoom_text)
        
        # Add tooltip on hover
        self._add_tooltip(self.file_label, filepath)
    
    def _truncate_path(self, filepath):
        """Truncate filepath to fit in available space"""
        if not filepath:
            return "Ready"
        
        # Get approximate available width (80% of frame)
        # This is a rough estimate; adjust as needed
        max_width = 100  # characters, approximate
        
        if len(filepath) <= max_width:
            return filepath
        
        # If path is too long, try showing just filename
        filename = os.path.basename(filepath)
        directory = os.path.dirname(filepath)
        
        # If filename alone fits with ellipsis
        if len(filename) + 4 < max_width:  # +4 for "... "
            # Show filename with truncated path
            if directory:
                truncated_dir = directory
                available = max_width - len(filename) - 5  # -5 for " ... "
                if len(truncated_dir) > available:
                    truncated_dir = "..." + truncated_dir[-(available-3):]
                return f"{truncated_dir}/{filename}"
            return filename
        
        # If even filename is too long, truncate middle of filename
        if len(filename) > max_width - 4:
            available = max_width - 7  # -7 for "......"
            mid = available // 2
            return f"{filename[:mid]}...{filename[-mid:]}"
        
        return filepath
    
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget on hover"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background=WHITE, foreground=DARK_GRAY, relief=tk.SOLID, borderwidth=1, font=('Segoe UI', 8), padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def set_status(self, message):
        """Update status message (legacy)"""
        self.file_label.config(text=message)
        self.update()
    
    def clear_status(self):
        """Clear status message"""
        self.file_label.config(text="Ready")
        self.zoom_label.config(text="")


class ToolBar(tk.Frame):
    """Toolbar with styled buttons"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=LIGHT_BLUE, height=50, **kwargs)
        self.pack_propagate(False)
    
    def add_button(self, text, command=None):
        """Add a button to the toolbar"""
        btn = StyledButton(self, text=text, command=command, padx=10, pady=5)
        btn.pack(side=tk.LEFT, padx=5, pady=5)
        return btn
    
    def add_separator(self):
        """Add a vertical separator"""
        sep = tk.Frame(self, bg=BORDER_GRAY, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)


class ScrolledFrame(tk.Frame):
    """Frame with scrollbar"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=WHITE)
        
        self.canvas = tk.Canvas(self, bg=WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=WHITE)
        
        # Create window on canvas
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Update canvas scroll region and width when frame changes
        def on_frame_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Make scrollable_frame width match canvas width
            self.canvas.itemconfig(self.window_id, width=self.canvas.winfo_width())
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to update scrollable_frame width
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


def show_info_dialog(title, message):
    """Show information dialog"""
    messagebox.showinfo(title, message)


def show_error_dialog(title, message):
    """Show error dialog"""
    messagebox.showerror(title, message)


def show_warning_dialog(title, message):
    """Show warning dialog"""
    messagebox.showwarning(title, message)


def show_confirmation_dialog(title, message):
    """Show confirmation dialog"""
    return messagebox.askyesno(title, message)


def show_password_dialog(attempt_number, max_attempts):
    """Show password input dialog for password-protected PDFs
    
    Args:
        attempt_number: Current attempt number (1-based)
        max_attempts: Maximum number of attempts allowed
    
    Returns:
        Tuple of (password, accepted) where accepted is True if user entered password, False if Cancel
    """
    from tkinter import simpledialog
    
    # Create a temporary root for the dialog
    temp_root = tk.Tk()
    temp_root.withdraw()
    temp_root.attributes('-topmost', True)
    
    # Set dialog icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Images', 'D2_logo_32.ico')
        if os.path.exists(icon_path):
            temp_root.iconbitmap(icon_path)
    except:
        pass
    
    try:
        # Show password prompt using simpledialog
        message = f"This PDF is password protected.\nEnter password to open (Attempt {attempt_number}/{max_attempts})"
        
        password = simpledialog.askstring(
            "Password Protected PDF",
            message,
            show='*',
            parent=temp_root
        )
        
        temp_root.destroy()
        
        if password is None:
            return None, False
        return password, True
    except Exception as e:
        temp_root.destroy()
        return None, False


# Theme configuration for ttk widgets
def configure_ttk_theme():
    """Configure ttk widgets to match the theme"""
    style = ttk.Style()
    
    # Configure treeview
    style.configure('Treeview', 
                    font=('Arial', 10),
                    background=WHITE,
                    foreground=DARK_GRAY,
                    fieldbackground=WHITE)
    style.configure('Treeview.Heading',
                    font=('Arial', 10, 'bold'),
                    background=LIGHT_BLUE,
                    foreground=DARK_BLUE)
    
    # Configure scrollbar
    style.configure('Vertical.TScrollbar',
                    background=LIGHT_GRAY,
                    troughcolor=WHITE)
    
    # Configure progressbar
    style.configure('Horizontal.TProgressBar',
                    background=DARK_BLUE,
                    troughcolor=WHITE)
