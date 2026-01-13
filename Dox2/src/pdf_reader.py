"""
PDF Reader Module for Dox2 PDF Application
Provides PDF viewing with vertical scrolling, RGB color rendering, and zoom
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
from PIL import Image, ImageTk
import io
import sys
import os
import webbrowser

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import render_page_with_fallback, get_page_size, get_page_text
from src.ui_components import (
    StyledFrame, StyledLabel, StyledButton, StatusBar,
    show_password_dialog, show_error_dialog,
    LIGHT_BLUE, DARK_BLUE, WHITE, DARK_GRAY
)


class PDFReader(StyledFrame):
    """PDF Reader with vertical scrolling and RGB color rendering"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # PDF document
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.current_filepath = ""  # Track current file path
        
        # Rendering cache for continuous pages
        self.page_images = {}  # Cache of rendered page images
        self.page_positions = {}  # Track y-position of each page on canvas
        self.current_photo_images = []  # Keep references to PhotoImage objects
        self.image_on_canvas = None
        
        # Navigation state to prevent loops
        self.last_navigation_page = -1  # Track which page we last navigated to
        self.scroll_direction = None  # Track scroll direction (up/down)
        
        # Password protection handling
        self.pending_filepath = None  # File waiting for password
        self.password_attempt_count = 0
        self.max_password_attempts = 20
        self.password_input_widget = None  # Reference to password input frame
        self.is_closing = False  # Flag to prevent dialogs during shutdown
        
        # Bookmarks and links
        self.links_on_page = {}  # Dictionary of links per page
        
        # Setup UI
        self._setup_ui()
        
        # Bind mouse wheel for vertical scrolling
        self.canvas.bind('<MouseWheel>', self._on_canvas_mousewheel)
        self.canvas.bind('<Button-4>', self._on_canvas_mousewheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self._on_canvas_mousewheel)  # Linux scroll down
        
        # Bind Shift+MouseWheel for horizontal scrolling
        self.canvas.bind('<Shift-MouseWheel>', self._on_canvas_h_scroll)
        self.canvas.bind('<Shift-Button-4>', self._on_canvas_h_scroll)  # Linux shift scroll
        self.canvas.bind('<Shift-Button-5>', self._on_canvas_h_scroll)  # Linux shift scroll
        
        # Bind click for link detection
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _setup_ui(self):
        """Setup UI components with 3 sections: Open PDF (left), Zoom (center), Pagination (right)"""
        # Top toolbar frame
        toolbar = StyledFrame(self)
        toolbar.pack(fill=tk.X, side=tk.TOP, padx=8, pady=8)
        
        # Section 1: File operations (LEFT) - fixed width
        file_section = tk.Frame(toolbar, bg=WHITE)
        file_section.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_btn = StyledButton(
            file_section, 
            text="📂 Open PDF",
            command=self._open_file
        )
        self.open_btn.pack(side=tk.LEFT, padx=3)
        
        # Section 2: Zoom controls (CENTER) - expandable
        zoom_section = tk.Frame(toolbar, bg=WHITE)
        zoom_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10))
        
        self.zoom_label_text = tk.Label(zoom_section, text="Zoom:", bg=WHITE, fg='#333333', font=('Segoe UI', 10))
        self.zoom_label_text.pack(side=tk.LEFT, padx=(0, 5))
        
        self.zoom_out_btn = StyledButton(
            zoom_section,
            text="−",
            command=self._zoom_out
        )
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        # Editable zoom entry - appears as label until clicked
        self.zoom_input = tk.Entry(
            zoom_section,
            width=6,
            font=('Segoe UI', 10),
            bg=WHITE,
            fg=DARK_GRAY,
            relief=tk.FLAT,
            bd=0,
            justify=tk.CENTER
        )
        self.zoom_input.pack(side=tk.LEFT, padx=4)
        self.zoom_input.bind('<Return>', self._on_zoom_input_enter)
        self.zoom_input.bind('<FocusOut>', self._on_zoom_input_leave)
        self.zoom_input.bind('<Button-1>', self._on_zoom_input_click)
        self.zoom_input.config(state='readonly')  # Start as readonly (label-like)
        
        self.zoom_percent = tk.Label(zoom_section, text="%", bg=WHITE, fg='#333333', font=('Segoe UI', 10))
        self.zoom_percent.pack(side=tk.LEFT, padx=(0, 5))
        
        self.zoom_in_btn = StyledButton(
            zoom_section,
            text="+",
            command=self._zoom_in
        )
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        self.fit_width_btn = StyledButton(
            zoom_section,
            text="🔲 Reset",
            command=self._fit_to_width
        )
        self.fit_width_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Section 3: Page navigation (RIGHT) - fixed width
        nav_section = tk.Frame(toolbar, bg=WHITE)
        nav_section.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.prev_btn = StyledButton(
            nav_section,
            text="◀ Prev",
            command=self._prev_page
        )
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        # Page number display with editable current page
        self.page_label = tk.Entry(
            nav_section,
            width=3,
            font=('Segoe UI', 10),
            bg=WHITE,
            fg=DARK_GRAY,
            relief=tk.FLAT,
            bd=0,
            justify=tk.CENTER
        )
        self.page_label.pack(side=tk.LEFT, padx=4)
        self.page_label.bind('<Return>', self._on_page_input_enter)
        self.page_label.bind('<FocusOut>', self._on_page_input_leave)
        self.page_label.bind('<Button-1>', self._on_page_input_click)
        self.page_label.config(state='readonly')  # Start as readonly (label-like)
        
        # Separator and total pages
        self.page_sep = tk.Label(nav_section, text="/", bg=WHITE, fg='#333333', font=('Segoe UI', 10))
        self.page_sep.pack(side=tk.LEFT, padx=2)
        
        self.page_total = tk.Label(nav_section, text="0", bg=WHITE, fg='#333333', font=('Segoe UI', 10))
        self.page_total.pack(side=tk.LEFT, padx=4)
        
        self.next_btn = StyledButton(
            nav_section,
            text="Next ▶",
            command=self._next_page
        )
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        # Create a frame for canvas and scrollbars
        canvas_frame = tk.Frame(self, bg=LIGHT_BLUE)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas for PDF display with scrollbars
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=LIGHT_BLUE,
            highlightthickness=0,
            cursor='hand2',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _open_file(self):
        """Open PDF file dialog"""
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filepath:
            self.load_pdf(filepath)
    
    def _extract_links_for_page(self, page_num):
        """Extract links from a specific page"""
        if not self.doc or page_num >= self.total_pages or page_num < 0:
            return
        
        if page_num not in self.links_on_page:
            self.links_on_page[page_num] = []
        else:
            return  # Already extracted
        
        page = self.doc[page_num]
        
        try:
            # Get all links on the page
            for link in page.get_links():
                if link['type'] == 'uri':  # External link
                    self.links_on_page[page_num].append({
                        'type': 'external',
                        'uri': link['uri'],
                        'rect': link['from']
                    })
                elif link['type'] == 'goto':  # Internal link
                    self.links_on_page[page_num].append({
                        'type': 'internal',
                        'page': link.get('page', 0),
                        'rect': link['from']
                    })
        except:
            pass
    
    def _on_canvas_click(self, event):
        """Handle click on canvas - check for links"""
        if self.current_page not in self.links_on_page or not self.links_on_page[self.current_page]:
            return
        
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Get page position
        if self.current_page not in self.page_positions:
            return
        
        page_y_offset = self.page_positions[self.current_page]
        
        # Check if click is on any link
        for link in self.links_on_page[self.current_page]:
            rect = link['rect']
            # rect is (x0, y0, x1, y1) in PDF coordinates
            # Need to adjust for page offset
            if rect[0] <= canvas_x <= rect[2] and (page_y_offset + rect[1]) <= canvas_y <= (page_y_offset + rect[3]):
                if link['type'] == 'external':
                    try:
                        webbrowser.open(link['uri'])
                    except:
                        pass
                elif link['type'] == 'internal':
                    self.current_page = link['page']
                    self.page_label.config(state='normal')
                    self.page_label.delete(0, tk.END)
                    self.page_label.insert(0, str(self.current_page + 1))
                    self.page_label.config(state='readonly')
                    self.render_current_page()
                    self.canvas.yview_moveto(0)
                return
    
    def _show_password_input_widget(self):
        """Show password dialog for password-protected PDF"""
        # Don't show dialog if application is closing
        if self.is_closing:
            return
        
        # Show the password input dialog
        password, accepted = show_password_dialog(
            self.password_attempt_count + 1,
            self.max_password_attempts
        )
        
        if accepted and password is not None:
            # User entered password and clicked Open
            self._try_open_with_password(password)
        else:
            # User cancelled
            self._cancel_password_input()
    
    def _try_open_with_password(self, password):
        """Try to open the pending PDF with the provided password"""
        if not self.pending_filepath:
            return
        
        try:
            self.doc = fitz.open(self.pending_filepath)
            
            # Authenticate with the password
            authenticated = self.doc.authenticate(password)
            
            if not authenticated:
                raise Exception("Authentication failed - incorrect password")
            
            # Try to access document metadata to validate password worked
            try:
                page_count = self.doc.page_count
            except Exception as e:
                raise Exception(f"Failed to access document: {e}")
            
            # Success! Load the PDF
            self.total_pages = self.doc.page_count
            self.current_page = 0
            self.current_filepath = self.pending_filepath
            self.pending_filepath = None
            self.password_attempt_count = 0
            
            # Reset navigation state
            self.last_navigation_page = -1
            self.scroll_direction = None
            
            # Clear rendering cache
            self.page_images.clear()
            self.page_positions.clear()
            self.current_photo_images.clear()
            
            # Set zoom to 100% by default
            self.zoom_factor = 1.0
            
            # Update zoom input field with default zoom
            self.zoom_input.config(state='normal')
            self.zoom_input.delete(0, tk.END)
            self.zoom_input.insert(0, "100")
            self.zoom_input.config(state='readonly')
            
            # Update page number display
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, "1")
            self.page_label.config(state='readonly')
            
            self.page_total.config(text=str(self.total_pages))
            
            # Update status bar with file info
            zoom_text = f"Zoom: {int(self.zoom_factor * 100)}%"
            self.status_bar.set_file_info(self.current_filepath, zoom_text)
            
            # Render pages starting from page 0
            self.render_current_page()
            
            # Scroll to top after rendering
            self.canvas.yview_moveto(0)
            
            # Hide password widget
            self._hide_password_input_widget()
            
        except Exception as e:
            self.password_attempt_count += 1
            
            if self.password_attempt_count >= self.max_password_attempts:
                # Too many attempts - close the tab or go back
                self._close_tab_on_password_failure()
            else:
                # Show error and refresh the widget
                remaining = self.max_password_attempts - self.password_attempt_count
                error_msg = f"Incorrect password ({remaining} attempts remaining)"
                self._update_password_widget_message(error_msg)
    
    def _update_password_widget_message(self, error_msg):
        """Update the password widget with an error message and show dialog again"""
        # Simply show the password dialog again, which will display the updated attempt counter
        self._show_password_input_widget()
    
    def _hide_password_input_widget(self):
        """Hide the password input widget (cleanup method)"""
        # No longer needed since we use dialogs, but keep for compatibility
        if self.password_input_widget:
            self.password_input_widget.destroy()
            self.password_input_widget = None
    
    def _cancel_password_input(self):
        """Cancel password input and reset"""
        self.pending_filepath = None
        self.password_attempt_count = 0
        self._hide_password_input_widget()
        self.status_bar.set_status("Password entry cancelled")
    
    def _close_tab_on_password_failure(self):
        """Close the current tab or go back after max password attempts"""
        self._hide_password_input_widget()
        show_error_dialog(
            "Password Failed",
            f"Maximum password attempts ({self.max_password_attempts}) exceeded.\nTab will be closed."
        )
        
        # Reset state
        self.pending_filepath = None
        self.password_attempt_count = 0
        
        # Try to close the tab through the parent
        if hasattr(self.parent, '_close_current_tab'):
            self.parent._close_current_tab()
        else:
            # Fallback: just clear the reader
            if self.doc:
                self.doc.close()
                self.doc = None
            self.canvas.delete('all')
            self.status_bar.set_status("Password attempt limit reached")
    
    def load_pdf(self, filepath):
        """Load PDF file with password support"""
        # Don't load if closing
        if self.is_closing:
            return False
        
        try:
            if self.doc:
                self.doc.close()
                self.doc = None
            
            # Try to open the PDF
            try:
                self.doc = fitz.open(filepath)
            except Exception as e:
                # Check if it's a password-protected PDF
                error_str = str(e).lower()
                
                # Check for various password-related error messages
                if "password" in error_str or "encrypted" in error_str or "needs password" in error_str or "is encrypted" in error_str:
                    # Show password input widget
                    self.pending_filepath = filepath
                    self.password_attempt_count = 0
                    self._show_password_input_widget()
                    return True
                else:
                    # Try to open as password-protected anyway, might need password
                    try:
                        self.doc = fitz.open(filepath, password="")
                    except:
                        # Definitely needs a password
                        self.pending_filepath = filepath
                        self.password_attempt_count = 0
                        self._show_password_input_widget()
                        return True
                    raise
            
            # Check if PDF is encrypted (password-protected)
            if self.doc.is_encrypted:
                # Close the unencrypted handle and show password dialog
                self.doc.close()
                self.doc = None
                self.pending_filepath = filepath
                self.password_attempt_count = 0
                self._show_password_input_widget()
                return True
            
            # Successfully opened without password
            self.total_pages = self.doc.page_count
            self.current_page = 0
            self.current_filepath = filepath
            self.pending_filepath = None
            self.password_attempt_count = 0
            
            # Reset navigation state
            self.last_navigation_page = -1
            self.scroll_direction = None
            
            # Clear rendering cache
            self.page_images.clear()
            self.page_positions.clear()
            self.current_photo_images.clear()
            
            # Set zoom to 100% by default
            self.zoom_factor = 1.0
            
            # Update zoom input field with default zoom
            self.zoom_input.config(state='normal')
            self.zoom_input.delete(0, tk.END)
            self.zoom_input.insert(0, "100")
            self.zoom_input.config(state='readonly')
            
            # Update page number display
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, "1")
            self.page_label.config(state='readonly')
            
            self.page_total.config(text=str(self.total_pages))
            
            # Update status bar with file info
            zoom_text = f"Zoom: {int(self.zoom_factor * 100)}%"
            self.status_bar.set_file_info(filepath, zoom_text)
            
            # Render pages starting from page 0
            self.render_current_page()
            
            # Scroll to top after rendering
            self.canvas.yview_moveto(0)
            
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            self.status_bar.set_status("Error loading PDF")
            self.pending_filepath = None
            self.password_attempt_count = 0
            self._hide_password_input_widget()
            return False
    
    def render_current_page(self):
        """Render all pages continuously for seamless scrolling like Adobe DC"""
        if not self.doc or self.total_pages == 0:
            return
        
        # Extract links from all pages
        for page_num in range(self.total_pages):
            self._extract_links_for_page(page_num)
        
        # Clear previous rendering cache
        self.page_images.clear()
        self.page_positions.clear()
        self.current_photo_images.clear()
        self.canvas.delete('all')
        
        # Render ALL pages in the document
        pages_to_render = list(range(self.total_pages))
        
        # Get canvas width for centering
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 2:
            canvas_width = 800
        
        y_position = 10
        total_height = 0
        img_width = 0
        
        # Render all pages
        for page_num in pages_to_render:
            # Render page with fallback methods
            img, method = render_page_with_fallback(self.doc, page_num, self.zoom_factor)
            
            if img is None:
                continue
            
            # Store page image and position
            self.page_images[page_num] = img
            self.page_positions[page_num] = y_position
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            self.current_photo_images.append(photo)  # Keep reference
            
            # Calculate centering
            img_width, img_height = img.size
            x = max(0, (canvas_width - img_width) // 2)
            
            # Display image on canvas
            self.canvas.create_image(x, y_position, image=photo, anchor='nw')
            
            # Add separator between pages (except after last page)
            if page_num < self.total_pages - 1:
                self.canvas.create_line(
                    0, y_position + img_height + 5,
                    canvas_width, y_position + img_height + 5,
                    fill='#CCCCCC', width=1
                )
            
            # Add page number label
            self.canvas.create_text(
                canvas_width / 2, y_position + img_height + 15,
                text=f"Page {page_num + 1}",
                font=('Segoe UI', 9),
                fill='#999999'
            )
            
            # Update y position for next page
            y_position += img_height + 30
            total_height = y_position
            
            # Update current_page based on viewport (optional, for status tracking)
            # This helps update the page indicator
        
        # Update scroll region to show all pages
        scroll_width = max(img_width, canvas_width)
        self.canvas.config(scrollregion=(0, 0, scroll_width, total_height))
        
        # Update page label (only if it changed)
        try:
            current_page_display = int(self.page_label.get())
        except ValueError:
            current_page_display = -1
        
        if current_page_display != self.current_page + 1:
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
            self.page_label.config(state='readonly')
        
        zoom_percent = int(self.zoom_factor * 100)
        
        # Update zoom input field only if it changed
        try:
            current_zoom = int(self.zoom_input.get())
        except ValueError:
            current_zoom = -1
        
        if current_zoom != zoom_percent:
            self.zoom_input.config(state='normal')
            self.zoom_input.delete(0, tk.END)
            self.zoom_input.insert(0, str(zoom_percent))
            self.zoom_input.config(state='readonly')
        
        # Update status bar with zoom info
        zoom_text = f"Zoom: {zoom_percent}%"
        self.status_bar.set_file_info(self.current_filepath, zoom_text)
    
    def _display_image(self, img):
        """Display single image on canvas (kept for compatibility)"""
        # This method is kept for backward compatibility but is no longer the primary
        # rendering path. The main rendering is done in render_current_page()
        pass
    
    def _on_zoom_input_click(self, event=None):
        """Make zoom input editable when clicked"""
        self.zoom_input.config(state='normal')
        self.zoom_input.select_range(0, tk.END)
    
    def _on_zoom_input_enter(self, event=None):
        """Handle zoom input when Enter is pressed"""
        try:
            zoom_value = int(self.zoom_input.get())
            # Clamp value between 50-300
            if zoom_value < 50:
                zoom_value = 50
            elif zoom_value > 300:
                zoom_value = 300
            
            # Convert to zoom factor (50% = 0.5, 100% = 1.0, 300% = 3.0)
            self.zoom_factor = zoom_value / 100.0
            self.render_current_page()
        except ValueError:
            # If not a number, ignore and keep current zoom
            self.zoom_input.delete(0, tk.END)
            self.zoom_input.insert(0, str(int(self.zoom_factor * 100)))
        finally:
            # Make it readonly again (label-like)
            self.zoom_input.config(state='readonly')
    
    def _on_zoom_input_leave(self, event=None):
        """Make zoom input readonly when focus is lost"""
        try:
            zoom_value = int(self.zoom_input.get())
            # Clamp value between 50-300
            if zoom_value < 50:
                zoom_value = 50
            elif zoom_value > 300:
                zoom_value = 300
            
            # Convert to zoom factor
            self.zoom_factor = zoom_value / 100.0
            self.render_current_page()
        except ValueError:
            # If not a number, restore current zoom
            self.zoom_input.delete(0, tk.END)
            self.zoom_input.insert(0, str(int(self.zoom_factor * 100)))
        finally:
            # Make it readonly again (label-like)
            self.zoom_input.config(state='readonly')
    
    def _on_page_input_click(self, event=None):
        """Make page input editable when clicked"""
        self.page_label.config(state='normal')
        self.page_label.select_range(0, tk.END)
    
    def _on_page_input_enter(self, event=None):
        """Handle page input when Enter is pressed"""
        try:
            page_value = int(self.page_label.get())
            # Clamp value between 1 and total_pages
            if page_value < 1:
                page_value = 1
            elif page_value > self.total_pages:
                page_value = self.total_pages
            
            # Convert to 0-based index
            self.current_page = page_value - 1
            
            # Scroll to the position of the current page
            if self.current_page in self.page_positions:
                y_pos = self.page_positions[self.current_page]
                # Convert absolute position to scroll view position
                scroll_region = self.canvas.cget('scrollregion').split()
                if scroll_region and len(scroll_region) >= 4:
                    try:
                        total_height = float(scroll_region[3])
                        canvas_height = self.canvas.winfo_height()
                        if total_height > canvas_height and canvas_height > 0:
                            scroll_fraction = y_pos / total_height
                            self.canvas.yview_moveto(scroll_fraction)
                    except:
                        pass
        except ValueError:
            # If not a number, restore current page
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
        finally:
            # Make it readonly again (label-like)
            self.page_label.config(state='readonly')
    
    def _on_page_input_leave(self, event=None):
        """Make page input readonly when focus is lost"""
        try:
            page_value = int(self.page_label.get())
            # Clamp value between 1 and total_pages
            if page_value < 1:
                page_value = 1
            elif page_value > self.total_pages:
                page_value = self.total_pages
            
            # Convert to 0-based index
            self.current_page = page_value - 1
            
            # Scroll to the position of the current page
            if self.current_page in self.page_positions:
                y_pos = self.page_positions[self.current_page]
                # Convert absolute position to scroll view position
                scroll_region = self.canvas.cget('scrollregion').split()
                if scroll_region and len(scroll_region) >= 4:
                    try:
                        total_height = float(scroll_region[3])
                        canvas_height = self.canvas.winfo_height()
                        if total_height > canvas_height and canvas_height > 0:
                            scroll_fraction = y_pos / total_height
                            self.canvas.yview_moveto(scroll_fraction)
                    except:
                        pass
        except ValueError:
            # If not a number, restore current page
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
        finally:
            # Make it readonly again (label-like)
            self.page_label.config(state='readonly')
    
    def _zoom_in(self):
        """Zoom in"""
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor = min(self.zoom_factor + 0.2, self.max_zoom)
            self.render_current_page()
    
    def _zoom_out(self):
        """Zoom out"""
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor = max(self.zoom_factor - 0.2, self.min_zoom)
            self.render_current_page()
    
    def _fit_to_width(self):
        """Reset zoom to 100%"""
        if not self.doc:
            return
        
        self.zoom_factor = 1.0
        self.render_current_page()
    
    def _next_page(self):
        """Go to next page by scrolling to it"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            # Scroll to the position of the current page
            if self.current_page in self.page_positions:
                y_pos = self.page_positions[self.current_page]
                # Convert absolute position to scroll view position
                scroll_region = self.canvas.cget('scrollregion').split()
                if scroll_region and len(scroll_region) >= 4:
                    try:
                        total_height = float(scroll_region[3])
                        canvas_height = self.canvas.winfo_height()
                        if total_height > canvas_height and canvas_height > 0:
                            scroll_fraction = y_pos / total_height
                            self.canvas.yview_moveto(scroll_fraction)
                    except:
                        pass
            # Update page indicator
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
            self.page_label.config(state='readonly')
    
    def _prev_page(self):
        """Go to previous page by scrolling to it"""
        if self.current_page > 0:
            self.current_page -= 1
            # Scroll to the position of the current page
            if self.current_page in self.page_positions:
                y_pos = self.page_positions[self.current_page]
                # Convert absolute position to scroll view position
                scroll_region = self.canvas.cget('scrollregion').split()
                if scroll_region and len(scroll_region) >= 4:
                    try:
                        total_height = float(scroll_region[3])
                        canvas_height = self.canvas.winfo_height()
                        if total_height > canvas_height and canvas_height > 0:
                            scroll_fraction = y_pos / total_height
                            self.canvas.yview_moveto(scroll_fraction)
                    except:
                        pass
            # Update page indicator
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
            self.page_label.config(state='readonly')
    
    def _on_canvas_mousewheel(self, event):
        """Handle mouse wheel for vertical canvas scrolling through all pages"""
        if not self.doc:
            return
        
        # Scroll amount
        scroll_amount = 3
        
        if event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-scroll_amount, 'units')
        else:  # Scroll down
            self.canvas.yview_scroll(scroll_amount, 'units')
        
        # Update page indicator based on current scroll position
        self._update_page_indicator()
    
    def _on_canvas_h_scroll(self, event):
        """Handle Shift+mouse wheel for horizontal canvas scrolling"""
        if not self.doc:
            return
        
        # Scroll left/right with Shift+mouse wheel
        # Positive delta = scroll left, negative delta = scroll right
        scroll_amount = 3  # Number of units to scroll
        
        if event.delta > 0:  # Scroll left
            self.canvas.xview_scroll(-scroll_amount, 'units')
        else:  # Scroll right
            self.canvas.xview_scroll(scroll_amount, 'units')
    
    def _on_canvas_configure(self, event):
        """Handle canvas configuration changes (resize) and re-render pages"""
        # Re-render pages when window is resized
        if self.doc and self.total_pages > 0:
            self.render_current_page()
    
    def _update_page_indicator(self):
        """Update the page indicator based on current scroll position"""
        if not self.doc or not self.page_positions:
            return
        
        # Get current scroll position
        scroll_position = self.canvas.yview()
        scroll_region = self.canvas.cget('scrollregion').split()
        
        if not scroll_region or len(scroll_region) < 4:
            return
        
        try:
            total_height = float(scroll_region[3])
            canvas_height = self.canvas.winfo_height()
            
            # Calculate the center of the current view in pixels
            view_start = scroll_position[0] * total_height
            view_end = scroll_position[1] * total_height
            view_center = (view_start + view_end) / 2
            
            # Find which page is at the center of the view
            current_page = 0
            for page_num in sorted(self.page_positions.keys()):
                if self.page_positions[page_num] <= view_center:
                    current_page = page_num
                else:
                    break
            
            # Update current_page and page label
            self.current_page = current_page
            self.page_label.config(state='normal')
            self.page_label.delete(0, tk.END)
            self.page_label.insert(0, str(self.current_page + 1))
            self.page_label.config(state='readonly')
        except:
            pass
    
    def get_current_page_text(self):
        """Get text from current page"""
        if not self.doc or self.current_page >= self.total_pages:
            return ""
        
        return get_page_text(self.doc, self.current_page)
    
    def goto_page(self, page_num):
        """Go to specific page"""
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self.render_current_page()
