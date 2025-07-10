import os
import threading
import requests
import yt_dlp
from urllib.parse import urlparse

class DownloadManager:
    def __init__(self, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Initializes the DownloadManager.

        Args:
            progress_callback (callable, optional): A function to call with download progress updates.
                                                    Expected signature: progress_callback(dict_info)
                                                    where dict_info contains 'status', 'total_bytes', 'downloaded_bytes', etc.
            completion_callback (callable, optional): A function to call when a download is complete.
                                                      Expected signature: completion_callback(file_path)
            error_callback (callable, optional): A function to call when an error occurs during download.
                                                 Expected signature: error_callback(message)
        """
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        self.is_downloading = False # Flag to indicate if a download is in progress

    def _yt_dlp_hook(self, d):
        """
        Callback hook for yt-dlp to report download progress.
        """
        if self.progress_callback:
            self.progress_callback(d)

    def _download_video_audio(self, url, output_path, download_type):
        """
        Uses yt-dlp to download video or extract audio.
        """
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._yt_dlp_hook],
            'retries': 3,
            'fragment_retries': 3,
            'ignoreerrors': True, # Continue on errors if possible
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Default video format
        }

        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'extract_audio': True,
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if self.completion_callback:
                # yt-dlp doesn't directly return the final file path easily via hooks for all cases.
                # We can try to infer it or rely on the user to check the output directory.
                # For simplicity, we'll just indicate completion here.
                # A more robust solution would involve parsing the final_path from the hook 'd' dict.
                self.completion_callback(f"Download complete for {url} (check {output_path})")
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Error downloading {url}: {e}")
        finally:
            self.is_downloading = False

    def _download_image(self, url, output_path):
        """
        Downloads an image using the requests library.
        """
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors

            # Infer filename from URL or use a generic one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename: # If no filename or no extension
                filename = "downloaded_image.jpg" # Default to JPG

            file_path = os.path.join(output_path, filename)

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if self.progress_callback:
                        # Simulate yt-dlp progress dict for consistency
                        self.progress_callback({
                            'status': 'downloading',
                            'total_bytes': total_size,
                            'downloaded_bytes': downloaded_size,
                            '_percent_str': f"{downloaded_size / total_size * 100:.1f}%" if total_size > 0 else "N/A",
                            '_eta_str': 'N/A', # Requests doesn't provide ETA easily
                        })
            if self.completion_callback:
                self.completion_callback(file_path)
        except requests.exceptions.RequestException as e:
            if self.error_callback:
                self.error_callback(f"Network error downloading image from {url}: {e}")
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Error downloading image from {url}: {e}")
        finally:
            self.is_downloading = False

    def download_content(self, url, download_type, output_dir):
        """
        Starts the download in a separate thread.

        Args:
            url (str): The URL to download.
            download_type (str): 'video', 'audio', or 'image'.
            output_dir (str): The directory to save the downloaded content.
        """
        if self.is_downloading:
            if self.error_callback:
                self.error_callback("A download is already in progress. Please wait.")
            return

        if not os.path.isdir(output_dir):
            if self.error_callback:
                self.error_callback(f"Output directory does not exist: {output_dir}")
            return

        self.is_downloading = True
        thread = threading.Thread(target=self._run_download_task, args=(url, download_type, output_dir))
        thread.daemon = True # Allow the main program to exit even if thread is running
        thread.start()

    def _run_download_task(self, url, download_type, output_dir):
        """Internal method to run the actual download task."""
        if download_type in ['video', 'audio']:
            self._download_video_audio(url, output_dir, download_type)
        elif download_type == 'image':
            self._download_image(url, output_dir)
        else:
            if self.error_callback:
                self.error_callback(f"Invalid download type: {download_type}")
            self.is_downloading = False

# Example usage (for testing purposes, not part of the main app)
if __name__ == '__main__':
    def test_progress(d):
        if d['status'] == 'downloading':
            print(f"Progress: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']} ETA {d['_eta_str']}")
        elif d['status'] == 'finished':
            print("Done downloading, converting...")

    def test_completion(file_path):
        print(f"Download completed! File: {file_path}")

    def test_error(message):
        print(f"Download error: {message}")

    manager = DownloadManager(test_progress, test_completion, test_error)

    # Create a test output directory
    test_output_dir = "downloads_test"
    os.makedirs(test_output_dir, exist_ok=True)

    print("--- Testing YouTube Video Download ---")
    # Replace with an actual YouTube video URL for testing
    # manager.download_content("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video", test_output_dir)
    # time.sleep(10) # Give it some time to start

    print("\n--- Testing Image Download ---")
    # Replace with an actual image URL for testing
    # manager.download_content("https://placehold.co/600x400/FF0000/FFFFFF/png?text=TestImage", "image", test_output_dir)
    # time.sleep(10)

    print("\n--- Testing TikTok Download (requires a valid TikTok URL) ---")
    # TikTok URLs can be tricky and may require cookies or specific versions of yt-dlp.
    # manager.download_content("https://www.tiktok.com/@tiktok_user/video/1234567890", "video", test_output_dir)
    # time.sleep(10)

    # Keep the main thread alive for a bit to see background downloads
    # import time
    # time.sleep(60)
    print("Test script finished. Check 'downloads_test' folder for results.")
