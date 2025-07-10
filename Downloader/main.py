import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import json # For saving/loading settings
from downloader_core import DownloadManager # Import the DownloadManager
from PIL import Image, ImageTk # Import Pillow for icons

class DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Universal Downloader")
        master.geometry("900x700") # Slightly larger default size
        master.minsize(700, 550) # Set a minimum size for better layout
        master.resizable(True, True)
        master.configure(bg="#e8f0f7") # Lightest background by default

        self.download_manager = DownloadManager(
            progress_callback=self.update_progress,
            completion_callback=self.on_download_complete,
            error_callback=self.on_download_error
        )

        self.output_directory = os.path.join(os.path.expanduser("~"), "Downloads", "UniversalDownloads")
        os.makedirs(self.output_directory, exist_ok=True) # Ensure default download directory exists

        # --- Settings Variables ---
        self.settings_file = "downloader_settings.json"
        self.current_theme = tk.StringVar(value="light") # Default theme
        self.download_quality_var = tk.StringVar(value="best") # Default quality
        self.themes = {
            "light": {
                "bg_app": "#e8f0f7",      # Very light blue-gray for main window
                "bg_frame": "#dbe9f5",     # Slightly darker for frames
                "bg_accent": "#c3d9eb",       # Even darker for some accents
                "text_primary": "#2c3e50",     # Dark blue-gray for main text
                "text_light": "#ffffff",    # White for text on dark backgrounds
                "button_primary": "#3498db",  # Standard blue for buttons/accents
                "button_hover": "#2980b9", # Darker blue for hover
                "success": "#2ecc71", # Green for success/progress
                "error": "#e74c3c",     # Red for errors
                "border": "#a7b8c9",  # Soft border color
                "input_bg": "#ffffff",      # White for input fields
                "log_bg": "#fdfefe",        # Off-white for log background
            },
            "dark": {
                "bg_app": "#2c3e50",      # Dark blue-gray for main window
                "bg_frame": "#34495e",     # Slightly lighter for frames
                "bg_accent": "#4a627a",       # Even lighter for some accents
                "text_primary": "#ecf0f1",     # Light gray for main text
                "text_light": "#ffffff",    # White for text on dark backgrounds
                "button_primary": "#3498db",  # Standard blue for buttons/accents
                "button_hover": "#2980b9", # Darker blue for hover
                "success": "#2ecc71", # Green for success/progress
                "error": "#e74c3c",     # Red for errors
                "border": "#1a242c",  # Dark border color
                "input_bg": "#3f546a",      # Darker input fields
                "log_bg": "#3f546a",        # Darker log background
            }
        }
        self.load_settings() # Load settings before creating widgets

        # Load icons (ensure icon_generate.py has been run)
        self.icons = {}
        self._load_icons()
        if self.icons.get("app_icon"):
            master.iconphoto(True, self.icons["app_icon"])

        self.create_menu() # Create menu bar
        self.create_widgets()
        self.apply_styles() # Apply styles after widgets are created and settings loaded

        # Add a variable to track the last logged percentage to avoid duplicate log entries
        self._last_logged_percent = -1 
        self.download_manager.set_download_quality(self.download_quality_var.get()) # Set initial quality in manager


    def load_settings(self):
        """Loads application settings from a JSON file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    self.current_theme.set(settings.get("theme", "light"))
                    self.download_quality_var.set(settings.get("download_quality", "best"))
                    saved_dir = settings.get("output_directory")
                    if saved_dir and os.path.isdir(saved_dir):
                        self.output_directory = saved_dir
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Fallback to defaults

    def save_settings(self):
        """Saves current application settings to a JSON file."""
        settings = {
            "theme": self.current_theme.get(),
            "download_quality": self.download_quality_var.get(),
            "output_directory": self.output_directory
        }
        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _load_icons(self):
        """Loads icon images from the 'icons' directory."""
        icon_names = [
            "app_icon", "paste_icon", "browse_icon", "download_icon",
            "video_icon", "audio_icon", "image_icon", "settings_icon",
            "help_icon", "info_icon", "success_icon", "error_icon",
            "light_theme_icon", "dark_theme_icon" # New theme icons
        ]
        icons_dir = "icons"
        
        if not os.path.exists(icons_dir):
            messagebox.showerror("Icon Error", f"The 'icons' directory was not found at '{icons_dir}'. Please run 'icon_generate.py' first to create the icons.")
            return

        for name in icon_names:
            path = os.path.join(icons_dir, f"{name}.png")
            try:
                img = Image.open(path)
                # Resize icons for buttons (e.g., 24x24 or 32x32)
                if name == "app_icon":
                    img = img.resize((64, 64), Image.Resampling.LANCZOS) # Larger for app icon
                else:
                    img = img.resize((24, 24), Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading icon {name}: {e}")
                self.icons[name] = None # Or a default blank image if you have one
                # messagebox.showwarning("Icon Missing", f"Could not load icon: {name}.png. Please ensure 'icon_generate.py' ran successfully.")

    def create_menu(self):
        """Creates the application's menu bar."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Set Output Directory...", command=self.browse_output_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme Submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_radiobutton(label="Light", variable=self.current_theme, value="light",
                                   command=lambda: self.set_theme("light"),
                                   image=self.icons.get("light_theme_icon"), compound=tk.LEFT)
        theme_menu.add_radiobutton(label="Dark", variable=self.current_theme, value="dark",
                                   command=lambda: self.set_theme("dark"),
                                   image=self.icons.get("dark_theme_icon"), compound=tk.LEFT)

        # Download Quality Submenu
        quality_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Download Quality", menu=quality_menu)
        quality_menu.add_radiobutton(label="Best", variable=self.download_quality_var, value="best",
                                     command=self.set_download_quality_option)
        quality_menu.add_radiobutton(label="Medium", variable=self.download_quality_var, value="medium",
                                     command=self.set_download_quality_option)
        quality_menu.add_radiobutton(label="Low", variable=self.download_quality_var, value="low",
                                     command=self.set_download_quality_option)


        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog,
                              image=self.icons.get("info_icon"), compound=tk.LEFT)

    def show_about_dialog(self):
        """Displays an about dialog."""
        messagebox.showinfo(
            "About Universal Downloader",
            "Universal Downloader App v1.0\n\n"
            "Developed by Dannz\n"
            "This application allows you to download videos, audio, and images from various online sources."
        )

    def set_theme(self, theme_name):
        """Changes the application's theme."""
        self.current_theme.set(theme_name)
        self.apply_styles()
        self.save_settings()
        self.log_message(f"Theme set to: {theme_name.capitalize()}", "info")

    def set_download_quality_option(self):
        """Sets the download quality in the download manager and saves settings."""
        quality = self.download_quality_var.get()
        self.download_manager.set_download_quality(quality)
        self.save_settings()
        self.log_message(f"Download quality set to: {quality.capitalize()}", "info")


    def apply_styles(self):
        """Applies modern and appealing styles to Tkinter widgets."""
        theme_colors = self.themes[self.current_theme.get()]
        style = ttk.Style()
        style.theme_use("clam") # A modern theme that allows customization

        # Apply main window background
        self.master.configure(bg=theme_colors["bg_app"])

        # General Frame and LabelFrame styles
        style.configure("TFrame", background=theme_colors["bg_frame"])
        style.configure("TLabelFrame", background=theme_colors["bg_frame"], foreground=theme_colors["text_primary"],
                        font=("Segoe UI", 11, "bold"), bordercolor=theme_colors["border"], relief="flat")
        style.map("TLabelFrame", bordercolor=[("active", theme_colors["button_primary"])])

        # Label styles
        style.configure("TLabel", background=theme_colors["bg_frame"], foreground=theme_colors["text_primary"], font=("Segoe UI", 10))

        # Button styles with more rounded corners and subtle shadow
        style.configure("TButton",
                        font=("Segoe UI", 10, "bold"),
                        background=theme_colors["button_primary"],
                        foreground=theme_colors["text_light"],
                        relief="flat",
                        padding=[12, 6], # Slightly more padding
                        focuscolor="none",
                        bordercolor=theme_colors["button_primary"],
                        focusthickness=0,
                        # borderradius=8, # Tkinter ttk doesn't directly support borderradius for TButton
                       )
        style.map("TButton",
                  background=[("active", theme_colors["button_hover"]), ("disabled", theme_colors["bg_accent"])],
                  foreground=[("active", theme_colors["text_light"]), ("disabled", theme_colors["text_primary"])],
                  relief=[("active", "raised"), ("!active", "flat")] # Subtle raised effect on hover
                 )
        
        # Entry and Combobox styles with more rounded corners
        style.configure("TEntry",
                        fieldbackground=theme_colors["input_bg"],
                        foreground=theme_colors["text_primary"],
                        bordercolor=theme_colors["border"],
                        relief="solid",
                        borderwidth=1,
                        padding=[8, 8], # More internal padding
                        font=("Segoe UI", 10),
                        # borderradius=8, # Tkinter ttk doesn't directly support borderradius for TEntry
                       )
        style.map("TEntry",
                  bordercolor=[("focus", theme_colors["button_primary"])]
                 )

        style.configure("TCombobox",
                        fieldbackground=theme_colors["input_bg"],
                        foreground=theme_colors["text_primary"],
                        selectbackground=theme_colors["button_primary"],
                        selectforeground=theme_colors["text_light"],
                        bordercolor=theme_colors["border"],
                        relief="solid",
                        borderwidth=1,
                        padding=[8, 8], # More internal padding
                        font=("Segoe UI", 10),
                        # borderradius=8, # Tkinter ttk doesn't directly support borderradius for TCombobox
                       )
        style.map("TCombobox",
                  fieldbackground=[("readonly", theme_colors["input_bg"])],
                  arrowcolor=[("!disabled", theme_colors["button_primary"])],
                  bordercolor=[("focus", theme_colors["button_primary"])]
                 )

        # Radiobutton styles
        style.configure("TRadiobutton",
                        background=theme_colors["bg_frame"],
                        foreground=theme_colors["text_primary"],
                        font=("Segoe UI", 10),
                        indicatorcolor=theme_colors["button_primary"],
                        selectcolor=theme_colors["button_primary"],
                        focusthickness=0,
                        padding=[5, 5] # Add some padding around text
                       )
        style.map("TRadiobutton",
                  background=[("active", theme_colors["bg_accent"])],
                  foreground=[("active", theme_colors["text_primary"])]
                 )

        # Progressbar styles with more visual depth
        style.configure("TProgressbar",
                        background=theme_colors["success"],
                        troughcolor=theme_colors["bg_accent"],
                        bordercolor=theme_colors["border"],
                        thickness=20, # Thicker progress bar
                        relief="flat",
                        # borderradius=10, # Tkinter ttk doesn't directly support borderradius for TProgressbar
                       )
        style.layout("TProgressbar",
                     [('progressbar.trough', {'children':
                       [('progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],
                       'sticky': 'nswe'})]) # Ensures pbar fills trough

        # Text widget styling (for log output)
        self.log_text.config(bg=theme_colors["log_bg"], fg=theme_colors["text_primary"])
        self.log_text.tag_configure("info", foreground=theme_colors["text_primary"])
        self.log_text.tag_configure("success", foreground=theme_colors["success"])
        self.log_text.tag_configure("error", foreground=theme_colors["error"])
        self.log_text.tag_configure("progress", foreground=theme_colors["button_primary"])


    def create_widgets(self):
        """Creates and lays out the GUI widgets."""
        # Main Frame
        main_frame = ttk.Frame(self.master, padding="25 25 25 25") # Increased padding for more breathing room
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="Content URL", padding="20 20") # Increased padding
        url_frame.pack(fill=tk.X, pady=15) # Increased pady

        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10) # Increased padx/pady
        self.url_entry.bind("<Return>", lambda event: self.start_download()) # Bind Enter key

        # Use icon for paste button
        paste_button = ttk.Button(url_frame, text="Paste", image=self.icons.get("paste_icon"), compound=tk.LEFT, command=self.paste_url)
        paste_button.pack(side=tk.RIGHT, padx=10, pady=10) # Increased padx/pady

        # Download Type Section
        type_frame = ttk.LabelFrame(main_frame, text="Download Type", padding="20 20") # Increased padding
        type_frame.pack(fill=tk.X, pady=15) # Increased pady

        self.download_type = tk.StringVar(value="video") # Default to video
        ttk.Radiobutton(type_frame, text="Video", image=self.icons.get("video_icon"), compound=tk.LEFT, variable=self.download_type, value="video")\
            .pack(side=tk.LEFT, padx=20, pady=10) # Increased padx/pady
        ttk.Radiobutton(type_frame, text="Audio", image=self.icons.get("audio_icon"), compound=tk.LEFT, variable=self.download_type, value="audio")\
            .pack(side=tk.LEFT, padx=20, pady=10) # Increased padx/pady
        ttk.Radiobutton(type_frame, text="Image", image=self.icons.get("image_icon"), compound=tk.LEFT, variable=self.download_type, value="image")\
            .pack(side=tk.LEFT, padx=20, pady=10) # Increased padx/pady

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="20 20") # Increased padding
        output_frame.pack(fill=tk.X, pady=15) # Increased pady

        self.output_dir_entry = ttk.Entry(output_frame, width=60, state="readonly")
        self.output_dir_entry.insert(0, self.output_directory)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10) # Increased padx/pady

        # Use icon for browse button
        browse_button = ttk.Button(output_frame, text="Browse", image=self.icons.get("browse_icon"), compound=tk.LEFT, command=self.browse_output_directory)
        browse_button.pack(side=tk.RIGHT, padx=10, pady=10) # Increased padx/pady

        # Download Button
        self.download_button = ttk.Button(main_frame, text="Start Download", image=self.icons.get("download_icon"), compound=tk.LEFT, command=self.start_download)
        self.download_button.pack(pady=25, ipadx=40, ipady=15) # Increased padding for a more prominent button

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Download Progress", padding="20 20") # Increased padding
        progress_frame.pack(fill=tk.X, pady=15) # Increased pady

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, expand=True, pady=10) # Increased pady

        self.progress_label = ttk.Label(progress_frame, text="Waiting for download...")
        self.progress_label.pack(pady=8) # Increased pady

        # Log Output Section
        log_frame = ttk.LabelFrame(main_frame, text="Download Log", padding="20 20") # Increased padding
        log_frame.pack(fill=tk.BOTH, expand=True, pady=15) # Increased pady

        self.log_text = tk.Text(log_frame, wrap="word", height=10, state="disabled",
                                bg="white", fg="#2c3e50", font=("Consolas", 9),
                                relief="flat", bd=0, padx=8, pady=8) # Added padx/pady to text widget
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

    def paste_url(self):
        """Pastes content from clipboard into the URL entry."""
        try:
            clipboard_content = self.master.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_content)
            self.log_message("URL pasted from clipboard.", "info")
        except tk.TclError:
            self.log_message("Clipboard is empty or inaccessible.", "error")

    def browse_output_directory(self):
        """Opens a dialog to select the download output directory."""
        new_directory = filedialog.askdirectory(initialdir=self.output_directory)
        if new_directory:
            self.output_directory = new_directory
            self.output_dir_entry.config(state="normal")
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, self.output_directory)
            self.output_dir_entry.config(state="readonly")
            self.log_message(f"Output directory set to: {self.output_directory}", "info")
            self.save_settings() # Save updated output directory

    def start_download(self):
        """Initiates the download process in a separate thread."""
        url = self.url_entry.get().strip()
        download_type = self.download_type.get()

        if not url:
            self.log_message("Please enter a URL to download.", "error")
            return
        
        if self.download_manager.is_downloading:
            self.log_message("A download is already in progress. Please wait.", "error")
            return

        self.log_message(f"Starting download for: {url}", "info")
        self.log_message(f"Type: {download_type.capitalize()}", "info")
        self.log_message(f"Saving to: {self.output_directory}", "info")

        self.progress_bar.config(value=0, mode="indeterminate") # Set to indeterminate mode
        self.progress_label.config(text="Starting download...")
        self.download_button.config(state="disabled") # Disable button during download

        # Start download in a thread
        self.download_manager.download_content(url, download_type, self.output_directory)

    def update_progress(self, d):
        """Updates the GUI with download progress."""
        # This method is called from a background thread, so use master.after to update GUI
        self.master.after(10, self._update_progress_gui, d)

    def _update_progress_gui(self, d):
        """Helper to safely update GUI elements from the main thread."""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)

            # Safely get formatted strings, providing defaults if not present
            percent_str = d.get('_percent_str', 'N/A')
            total_bytes_str = d.get('_total_bytes_str', 'N/A')
            speed_str = d.get('_speed_str', 'N/A')
            eta_str = d.get('_eta_str', 'N/A')
            downloaded_bytes_str = d.get('_downloaded_bytes_str', 'N/A') # Ensure this key is handled

            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
                self.progress_bar.config(mode="determinate", value=percent)
                self.progress_label.config(text=f"Downloading: {percent_str} of {total_bytes_str} at {speed_str} ETA {eta_str}")
            else:
                self.progress_bar.config(mode="indeterminate") # Fallback to indeterminate if total size unknown
                self.progress_label.config(text=f"Downloading: {downloaded_bytes_str} at {speed_str} ETA {eta_str}")
            
            # Log progress updates less frequently to avoid overwhelming the log
            # Use a more robust check for percent_str to avoid errors if it's 'N/A'
            try:
                # Extract numeric part, handle potential non-numeric values
                numeric_percent = float(percent_str.replace('%', '').split('.')[0])
                current_percent = int(numeric_percent)
                if current_percent % 10 == 0 and current_percent != self._last_logged_percent:
                     self.log_message(f"Progress: {percent_str}", "progress")
                     self._last_logged_percent = current_percent
            except ValueError:
                # Handle cases where percent_str is not a valid number (e.g., 'N/A' or during initial setup)
                pass


        elif d['status'] == 'finished':
            self.progress_bar.config(value=100, mode="determinate")
            self.progress_label.config(text="Download complete, processing...")
            self.log_message("Download finished. Post-processing...", "info")
        elif d['status'] == 'error':
            self.progress_bar.config(value=0, mode="determinate")
            self.progress_label.config(text="Download failed.")
            self.log_message("Download failed.", "error")


    def on_download_complete(self, message):
        """Handles download completion."""
        self.master.after(10, self._on_download_complete_gui, message)

    def _on_download_complete_gui(self, message):
        """Helper to safely handle completion in the main thread."""
        self.progress_bar.config(value=100, mode="determinate")
        self.progress_label.config(text="Download completed!")
        self.download_button.config(state="normal") # Re-enable button
        self.log_message(f"Download complete: {message}", "success")
        self.url_entry.delete(0, tk.END) # Clear URL input
        self._last_logged_percent = -1 # Reset for next download

    def on_download_error(self, message):
        """Handles download errors."""
        self.master.after(10, self._on_download_error_gui, message)

    def _on_download_error_gui(self, message):
        """Helper to safely handle errors in the main thread."""
        self.progress_bar.config(value=0, mode="determinate")
        self.progress_label.config(text="Download failed!")
        self.download_button.config(state="normal") # Re-enable button
        self.log_message(f"Error: {message}", "error")
        messagebox.showerror("Download Error", message)
        self._last_logged_percent = -1 # Reset for next download

    def log_message(self, message, tag="info"):
        """Appends a message to the log Text widget."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END) # Auto-scroll to the end
        self.log_text.config(state="disabled")

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

