from PIL import Image, ImageDraw, ImageFont
import os
import math

def generate_icons(output_dir="icons"):
    """
    Generates a set of modern, minimalist icons for the Universal Downloader app.
    Icons are saved as PNG files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    icon_size = 64 # Base size for rendering, will be resized in app
    small_icon_size = 32 # Size for smaller icons like in radio buttons
    
    # Try to load a modern font, fallback to default if not found
    try:
        font_path = "arial.ttf" # Common system font
        # Attempt to find a more modern font if available
        if os.name == 'nt': # Windows
            # Check for Segoe UI or Inter (if installed)
            if os.path.exists("C:/Windows/Fonts/segoeui.ttf"):
                font_path = "C:/Windows/Fonts/segoeui.ttf"
            elif os.path.exists("C:/Windows/Fonts/Inter-Regular.ttf"): # Assuming Inter might be installed
                font_path = "C:/Windows/Fonts/Inter-Regular.ttf"
        elif os.name == 'posix': # macOS/Linux
            if os.path.exists("/System/Library/Fonts/SFProText-Regular.otf"): # macOS
                font_path = "/System/Library/Fonts/SFProText-Regular.otf"
            elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"): # Linux
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        font_large = ImageFont.truetype(font_path, int(icon_size * 0.6)) # For main app icon
        font_medium = ImageFont.truetype(font_path, int(small_icon_size * 0.6)) # For general icons
        font_small = ImageFont.truetype(font_path, int(small_icon_size * 0.4)) # For smaller text/symbols
    except IOError:
        print("Warning: Could not load specified font. Using default PIL font.")
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Define a color palette for icons
    icon_colors = {
        "primary": "#3498db", # Blue
        "secondary": "#2ecc71", # Green
        "accent": "#e74c3c", # Red
        "dark": "#2c3e50", # Dark text
        "light": "#ffffff", # White text/elements
        "gray": "#7f8c8d", # Gray
        "success_green": "#2ecc71", # Added this missing key
        "error_red": "#e74c3c", # Added this missing key for consistency if used elsewhere
    }

    # --- App Icon (Larger and more detailed) ---
    img = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0)) # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Main shape: a stylized download arrow/cloud
    # Cloud shape
    draw.ellipse((5, 20, 35, 50), fill=icon_colors["primary"])
    draw.ellipse((20, 10, 50, 40), fill=icon_colors["primary"])
    draw.ellipse((30, 25, 60, 55), fill=icon_colors["primary"])
    draw.ellipse((15, 30, 45, 60), fill=icon_colors["primary"])
    
    # Arrow down
    arrow_points = [(icon_size/2, icon_size * 0.8), (icon_size/2 - 10, icon_size * 0.6), (icon_size/2 + 10, icon_size * 0.6)]
    draw.polygon(arrow_points, fill=icon_colors["light"])
    draw.line((icon_size/2, icon_size * 0.6, icon_size/2, icon_size * 0.4), fill=icon_colors["light"], width=5)

    img.save(os.path.join(output_dir, "app_icon.png"))

    # --- Common Icon Generation Function ---
    def create_icon(name, draw_func, size=small_icon_size):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_func(draw, size, icon_colors)
        img.save(os.path.join(output_dir, f"{name}.png"))

    # --- Specific Icons ---

    # Paste Icon (Clipboard with arrow)
    def draw_paste_icon(draw, size, colors):
        pad = size * 0.15
        clip_width = size * 0.5
        clip_height = size * 0.6
        clip_x = (size - clip_width) / 2
        clip_y = pad
        
        # Clipboard body
        draw.rounded_rectangle((clip_x, clip_y, clip_x + clip_width, clip_y + clip_height), radius=size*0.08, fill=colors["dark"])
        # Top part of clipboard
        draw.rounded_rectangle((clip_x + clip_width * 0.2, clip_y - size * 0.1, clip_x + clip_width * 0.8, clip_y + size * 0.05), radius=size*0.05, fill=colors["dark"])
        
        # Arrow pointing into clipboard
        arrow_start_x = size / 2
        arrow_start_y = size * 0.8
        arrow_end_y = clip_y + clip_height - 5
        
        draw.line((arrow_start_x, arrow_start_y, arrow_start_x, arrow_end_y), fill=colors["primary"], width=3)
        draw.polygon([(arrow_start_x, arrow_end_y), (arrow_start_x - 5, arrow_end_y - 8), (arrow_start_x + 5, arrow_end_y - 8)], fill=colors["primary"])
    create_icon("paste_icon", draw_paste_icon)

    # Browse Icon (Folder with magnifying glass)
    def draw_browse_icon(draw, size, colors):
        pad = size * 0.15
        # Folder
        draw.rounded_rectangle((pad, pad + size*0.1, size - pad, size - pad), radius=size*0.08, fill=colors["dark"])
        draw.rounded_rectangle((pad + size*0.05, pad, pad + size*0.4, pad + size*0.2), radius=size*0.05, fill=colors["dark"])
        
        # Magnifying glass
        mag_x = size * 0.6
        mag_y = size * 0.5
        mag_radius = size * 0.2
        draw.ellipse((mag_x - mag_radius, mag_y - mag_radius, mag_x + mag_radius, mag_y + mag_radius), outline=colors["primary"], width=2)
        draw.line((mag_x + mag_radius * 0.7, mag_y + mag_radius * 0.7, size - pad, size - pad), fill=colors["primary"], width=2)
    create_icon("browse_icon", draw_browse_icon)

    # Download Icon (Down arrow with line)
    def draw_download_icon(draw, size, colors):
        center_x, center_y = size / 2, size / 2
        line_length = size * 0.4
        arrow_head_size = size * 0.15
        
        # Vertical line
        draw.line((center_x, center_y - line_length/2, center_x, center_y + line_length/2 - arrow_head_size/2), fill=colors["light"], width=3)
        # Arrow head
        draw.polygon([
            (center_x, center_y + line_length/2),
            (center_x - arrow_head_size/2, center_y + line_length/2 - arrow_head_size),
            (center_x + arrow_head_size/2, center_y + line_length/2 - arrow_head_size)
        ], fill=colors["light"])
        # Base line
        draw.line((center_x - line_length/2, center_y + line_length/2 + 5, center_x + line_length/2, center_y + line_length/2 + 5), fill=colors["light"], width=3)
    create_icon("download_icon", draw_download_icon)

    # Video Icon (Play button in a rectangle)
    def draw_video_icon(draw, size, colors):
        pad = size * 0.2
        draw.rounded_rectangle((pad, pad, size - pad, size - pad), radius=size*0.08, outline=colors["primary"], width=2)
        # Play triangle
        play_x = size / 2 - size * 0.05
        play_y = size / 2
        draw.polygon([
            (play_x - size*0.1, play_y - size*0.15),
            (play_x - size*0.1, play_y + size*0.15),
            (play_x + size*0.15, play_y)
        ], fill=colors["primary"])
    create_icon("video_icon", draw_video_icon)

    # Audio Icon (Music note)
    def draw_audio_icon(draw, size, colors):
        center_x, center_y = size / 2, size / 2
        note_size = size * 0.3
        
        # Main note stem
        draw.line((center_x - note_size/2, center_y + note_size/2, center_x - note_size/2, center_y - note_size), fill=colors["primary"], width=3)
        # Note head
        draw.ellipse((center_x - note_size, center_y + note_size/2 - note_size/4, center_x - note_size/2 + note_size/2, center_y + note_size/2 + note_size/4), fill=colors["primary"])
        # Flag
        draw.line((center_x - note_size/2, center_y - note_size, center_x + note_size/2, center_y - note_size), fill=colors["primary"], width=3)
        draw.line((center_x + note_size/2, center_y - note_size, center_x + note_size/2, center_y - note_size * 0.5), fill=colors["primary"], width=3)
    create_icon("audio_icon", draw_audio_icon)

    # Image Icon (Mountain and sun)
    def draw_image_icon(draw, size, colors):
        pad = size * 0.2
        # Frame
        draw.rounded_rectangle((pad, pad, size - pad, size - pad), radius=size*0.08, outline=colors["primary"], width=2)
        # Mountain
        draw.polygon([
            (pad + size*0.1, size - pad - size*0.1),
            (size / 2, pad + size*0.1),
            (size - pad - size*0.1, size - pad - size*0.1)
        ], fill=colors["primary"])
        # Sun (circle)
        draw.ellipse((size - pad - size*0.25, pad + size*0.05, size - pad - size*0.05, pad + size*0.25), fill=colors["primary"])
    create_icon("image_icon", draw_image_icon)

    # Settings Icon (Gear)
    def draw_settings_icon(draw, size, colors):
        center_x, center_y = size / 2, size / 2
        outer_radius = size * 0.35
        inner_radius = size * 0.2
        num_teeth = 8
        
        for i in range(num_teeth):
            angle = 2 * math.pi * i / num_teeth
            # Outer points
            x1 = center_x + outer_radius * math.cos(angle)
            y1 = center_y + outer_radius * math.sin(angle)
            
            # Inner points for the tooth
            angle_inner_start = angle - (math.pi / num_teeth / 2)
            angle_inner_end = angle + (math.pi / num_teeth / 2)
            
            x_inner_start = center_x + inner_radius * math.cos(angle_inner_start)
            y_inner_start = center_y + inner_radius * math.sin(angle_inner_start)
            
            x_inner_end = center_x + inner_radius * math.cos(angle_inner_end)
            y_inner_end = center_y + inner_radius * math.sin(angle_inner_end)
            
            draw.polygon([
                (x_inner_start, y_inner_start),
                (x1, y1),
                (x_inner_end, y_inner_end)
            ], fill=colors["dark"])
        
        # Inner circle of the gear
        draw.ellipse((center_x - inner_radius * 0.6, center_y - inner_radius * 0.6,
                      center_x + inner_radius * 0.6, center_y + inner_radius * 0.6), fill=colors["light"])
    create_icon("settings_icon", draw_settings_icon)

    # Help Icon (Question mark)
    def draw_help_icon(draw, size, colors):
        center_x, center_y = size / 2, size / 2
        # Question mark body
        draw.arc((center_x - size*0.15, center_y - size*0.25, center_x + size*0.15, center_y + size*0.05),
                 start=0, end=180, fill=colors["dark"], width=3)
        draw.line((center_x, center_y + size*0.05, center_x, center_y + size*0.15), fill=colors["dark"], width=3)
        # Dot
        draw.ellipse((center_x - 3, center_y + size*0.2 - 3, center_x + 3, center_y + size*0.2 + 3), fill=colors["dark"])
    create_icon("help_icon", draw_help_icon)

    # Info Icon (i in a circle)
    def draw_info_icon(draw, size, colors):
        center_x, center_y = size / 2, size / 2
        radius = size * 0.4
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), outline=colors["primary"], width=2)
        draw.line((center_x, center_y - size*0.15, center_x, center_y + size*0.1), fill=colors["primary"], width=3)
        draw.ellipse((center_x - 3, center_y - size*0.25 - 3, center_x + 3, center_y - size*0.25 + 3), fill=colors["primary"])
    create_icon("info_icon", draw_info_icon)

    # Success Icon (Checkmark)
    def draw_success_icon(draw, size, colors):
        pad = size * 0.2
        draw.line((pad, size/2, size/2 - size*0.05, size - pad), fill=colors["success_green"], width=4)
        draw.line((size/2 - size*0.05, size - pad, size - pad, pad), fill=colors["success_green"], width=4)
    create_icon("success_icon", draw_success_icon)

    # Error Icon (X mark)
    def draw_error_icon(draw, size, colors):
        pad = size * 0.25
        draw.line((pad, pad, size - pad, size - pad), fill=colors["error_red"], width=4)
        draw.line((size - pad, pad, pad, size - pad), fill=colors["error_red"], width=4)
    create_icon("error_icon", draw_error_icon)

    print(f"Generated icons in '{output_dir}' directory.")

if __name__ == "__main__":
    generate_icons()
