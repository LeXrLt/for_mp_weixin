import tkinter as tk
from tkinter import scrolledtext, messagebox
import re
import aiohttp
import asyncio
import os
from urllib.parse import urlparse

class ImageDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Image Downloader")
        # Ensure there's an event loop for the main thread if not already present
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.url_input_label = tk.Label(master, text="Enter Image URLs (one per line or separated by spaces/markdown):")
        self.url_input_label.pack()

        self.url_text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=15)
        self.url_text_area.pack(padx=10, pady=5)

        self.download_button = tk.Button(master, text="Download Images", command=self.start_download_thread)
        self.download_button.pack(pady=5)

        self.status_label = tk.Label(master, text="Status: Idle")
        self.status_label.pack(pady=5)

        self.progress_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=10, state=tk.DISABLED)
        self.progress_area.pack(padx=10, pady=5)

        self.id_counter = 1
        self.download_folder = "downloads"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def log_message(self, message):
        self.progress_area.config(state=tk.NORMAL)
        self.progress_area.insert(tk.END, message + "\n")
        self.progress_area.see(tk.END)
        self.progress_area.config(state=tk.DISABLED)
        self.master.update_idletasks() # Ensure GUI updates

    def start_download_thread(self):
        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Downloading...")
        urls = self.get_urls_from_input()

        if not urls:
            messagebox.showwarning("No URLs", "Please enter some image URLs.")
            self.status_label.config(text="Status: Idle")
            self.download_button.config(state=tk.NORMAL)
            return

        self.log_message(f"Starting download for {len(urls)} URLs...")
        # Run asyncio event loop in a separate thread to avoid blocking Tkinter GUI
        # Ensure the loop is running. Tkinter's mainloop can be integrated with asyncio.
        # For simplicity and broader compatibility, we'll use a thread for the asyncio loop
        # if it's not already running or if this causes issues with Tkinter's own event loop.
        # However, run_coroutine_threadsafe is designed for this scenario.

        # Start a new thread for the asyncio tasks if not already handled by how the app is run
        # This ensures the GUI remains responsive.
        # The self.loop should be running in a separate thread for run_coroutine_threadsafe to work correctly.
        # This is typically handled by how the main application loop is started.
        # If the loop isn't running, we might need to start it.
        # For now, we assume `asyncio.get_event_loop()` provides a running loop or one that `run_coroutine_threadsafe` can use.

        asyncio.run_coroutine_threadsafe(self.download_all_images(urls), self.loop)


    async def download_image(self, session, url):
        attempts = 0
        max_retries = 3
        while attempts < max_retries:
            try:
                async with session.get(url, timeout=10) as response: # 10 second timeout for the request
                    response.raise_for_status()  # Raises an exception for 4XX/5XX status codes
                    content = await response.read()

                    # Determine file extension
                    # Try to get it from Content-Disposition header first
                    content_disposition = response.headers.get('Content-Disposition')
                    ext = ''
                    if content_disposition:
                        disp_filename = re.findall('filename="?([^"]+)"?', content_disposition)
                        if disp_filename:
                            ext = os.path.splitext(disp_filename[0])[1]

                    if not ext: # Fallback to URL extension
                        parsed_url = urlparse(url)
                        ext = os.path.splitext(parsed_url.path)[1]

                    if not ext: # Fallback to content type
                        content_type = response.headers.get('Content-Type')
                        if content_type:
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                ext = '.jpg'
                            elif 'png' in content_type:
                                ext = '.png'
                            elif 'gif' in content_type:
                                ext = '.gif'
                            elif 'webp' in content_type:
                                ext = '.webp'

                    # Default extension if none found
                    if not ext or len(ext) > 5 : # basic check for valid extension
                        ext = '.jpg'


                    # Generate a unique filename
                    # We can use a portion of the URL to make it more identifiable if needed
                    # For now, simple counter.
                    filename = f"image_{self.id_counter}{ext}"
                    filepath = os.path.join(self.download_folder, filename)

                    # Ensure filename is unique if we are very unlucky with id_counter + ext
                    while os.path.exists(filepath):
                        self.id_counter += 1
                        filename = f"image_{self.id_counter}{ext}"
                        filepath = os.path.join(self.download_folder, filename)

                    with open(filepath, 'wb') as f:
                        f.write(content)

                    self.id_counter += 1
                    self.log_message(f"Successfully downloaded: {filename} from {url}")
                    return True
            except aiohttp.ClientError as e: # Includes ClientResponseError, ClientConnectionError etc.
                attempts += 1
                self.log_message(f"Attempt {attempts}/{max_retries} failed for {url}: {e}")
                if attempts < max_retries:
                    await asyncio.sleep(2)  # Wait 2 seconds before retrying
                else:
                    self.log_message(f"Failed to download {url} after {max_retries} attempts.")
                    return False
            except asyncio.TimeoutError: # Specific timeout error
                attempts += 1
                self.log_message(f"Attempt {attempts}/{max_retries} timed out for {url}")
                if attempts < max_retries:
                    await asyncio.sleep(2)
                else:
                    self.log_message(f"Failed to download {url} due to timeout after {max_retries} attempts.")
                    return False
            except Exception as e: # Catch any other unexpected errors
                attempts += 1
                self.log_message(f"Attempt {attempts}/{max_retries} - An unexpected error occurred for {url}: {e}")
                if attempts < max_retries:
                     await asyncio.sleep(2)
                else:
                    self.log_message(f"Failed to download {url} due to unexpected error: {e}")
                    return False
        return False # Should not be reached if logic is correct

    async def download_all_images(self, urls):
        # Ensure aiohttp session is created within the async function
        # or passed correctly if created outside and managed by the event loop.
        # For simplicity, create it here.
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_image(session, url) for url in urls]
            results = await asyncio.gather(*tasks)

        successful_downloads = sum(1 for r in results if r)
        failed_downloads = len(urls) - successful_downloads

        self.log_message(f"\nDownload complete. {successful_downloads} successful, {failed_downloads} failed.")
        self.status_label.config(text=f"Status: Complete. {successful_downloads} OK, {failed_downloads} Failed.")
        self.download_button.config(state=tk.NORMAL)


    def get_urls_from_input(self):
        input_text = self.url_text_area.get("1.0", tk.END)
        # Regex to find URLs, can be simple or more complex depending on expected input
        # For now, let's assume one URL per line, or space-separated
        # A more robust regex could be: r'https?://[^\s]+'
        # For markdown style links like in the original script: r'!\[.*?\]\((.*?)\)'
        # Let's try to find any valid looking http/https URL first
        raw_urls = re.findall(r'https?://[^\s"\']+', input_text)

        # Also try to find markdown image URLs
        markdown_urls = re.findall(r'!\[.*?\]\((https?://[^\s"\']+)\)', input_text)

        combined_urls = list(set(raw_urls + markdown_urls)) # Use set to remove duplicates

        valid_urls = []
        for url in combined_urls:
            try:
                result = urlparse(url)
                if all([result.scheme, result.netloc]): # Basic check for a valid URL structure
                    valid_urls.append(url)
                else:
                    self.log_message(f"Skipping invalid URL: {url}")
            except ValueError:
                self.log_message(f"Skipping invalid URL (parse error): {url}")
        return valid_urls


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageDownloaderApp(root)

    # To integrate asyncio with Tkinter, we need to run the asyncio event loop
    # and periodically update Tkinter. One way is to run Tkinter's update
    # from the asyncio loop, or run asyncio in a separate thread and use thread-safe calls.
    # The current approach uses `run_coroutine_threadsafe`, which requires the asyncio loop
    # (app.loop in this case) to be running. A common pattern is to run the asyncio loop
    # in a separate thread.

    import threading

    def start_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # Start the asyncio event loop in a daemon thread
    # This thread will manage all the async tasks (like downloads)
    loop_thread = threading.Thread(target=start_asyncio_loop, args=(app.loop,), daemon=True)
    loop_thread.start()

    # Start Tkinter main loop
    # This will block the main thread until the GUI window is closed
    root.mainloop()

    # After mainloop exits (window closed), we should stop the asyncio loop
    # if it's still running and we want a clean shutdown.
    # For daemon threads, this might not be strictly necessary as they exit when the main program exits.
    # However, for cleaner resource management:
    if app.loop.is_running():
        app.loop.call_soon_threadsafe(app.loop.stop)
    # loop_thread.join() # Optionally wait for the loop thread to finish
