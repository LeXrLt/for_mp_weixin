# Async Image Downloader GUI

This Python application provides a user-friendly graphical interface (GUI) for batch downloading images from a list of URLs. It uses `asyncio` and `aiohttp` for fast, asynchronous downloads, ensuring the GUI remains responsive even when downloading many images. Each image download is attempted up to 3 times in case of transient network issues.

## Features

-   **Graphical User Interface:** Easy-to-use interface built with Tkinter.
-   **Batch Downloads:** Input multiple image URLs at once.
-   **Asynchronous Operations:** Downloads images concurrently for speed, without freezing the application.
-   **Retry Mechanism:** Each download will be retried up to 3 times upon failure.
-   **URL Parsing:** Accepts URLs listed one per line, separated by spaces, or embedded in markdown image syntax (`![alt](url)`).
-   **Status Updates:** Real-time feedback on download progress and errors in a dedicated status area.
-   **File Organization:** Images are saved into a `downloads` subdirectory, which is created automatically if it doesn't exist.
-   **Smart Extension Detection:** Tries to determine the correct file extension from HTTP headers (Content-Disposition, Content-Type) or the URL. Defaults to `.jpg` if undetectable.

## Prerequisites

-   Python 3.7+ (due to `asyncio` and `aiohttp` features)
-   `aiohttp` library

## Installation

1.  **Clone the repository or download the script:**
    If you have git:
    ```bash
    # git clone <repository_url> # If this were in a repo
    # cd <repository_directory>
    ```
    Otherwise, just download `get_photos.py`.

2.  **Install dependencies:**
    The application requires the `aiohttp` library. You can install it using pip:
    ```bash
    pip install aiohttp
    ```

## How to Run

Execute the Python script from your terminal:

```bash
python get_photos.py
```

A window will open with the following components:
-   **URL Input Area:** A large text box where you can paste your image URLs. Enter one URL per line, or multiple URLs separated by spaces. Markdown image links like `![description](http://example.com/image.png)` are also supported.
-   **Download Images Button:** Click this button to start the download process for all valid URLs found in the input area.
-   **Status Label:** Shows the current overall status (e.g., "Idle", "Downloading...", "Complete").
-   **Progress Area:** A scrollable text box that logs detailed messages about each download attempt, success, or failure.

## How it Works

1.  Paste your image URLs into the text area.
2.  Click the "Download Images" button.
3.  The application parses the input to find valid URLs.
4.  For each URL, it attempts to download the image asynchronously.
    -   If a download fails, it retries up to two more times (total 3 attempts).
    -   Progress for each image (downloading, success, failure, retries) is shown in the progress area.
5.  Downloaded images are saved in a folder named `downloads` in the same directory as the script. File names are generated (e.g., `image_1.jpg`, `image_2.png`, etc.) with an attempt to use the correct file extension.
6.  Once all downloads are attempted, a summary message is displayed.

## Development

(See `AGENTS.md` for more detailed development guidelines if you plan to modify the script.)

-   The GUI is built using Python's built-in `tkinter` library.
-   Asynchronous network requests are handled by `aiohttp` and `asyncio`.
-   To prevent the GUI from freezing during downloads, the `asyncio` event loop runs in a separate thread. Communication between the Tkinter thread and the asyncio thread is managed carefully (e.g., using `asyncio.run_coroutine_threadsafe`).

## Troubleshooting

-   **No module named 'aiohttp'**: Ensure you have installed the `aiohttp` library using `pip install aiohttp`.
-   **GUI freezes (should not happen)**: If the GUI freezes, it might indicate an issue with how asynchronous tasks are being managed. This script is designed to prevent this.
-   **Images not downloading / Errors in progress area**:
    -   Check if the URLs are correct and accessible in a browser.
    -   Some websites may block automated downloads (e.g., via User-Agent checks or other anti-bot measures). This script uses a default `aiohttp` user agent.
    -   Firewall or network issues might prevent connection.
    -   The progress area will provide details on errors (e.g., 404 Not Found, Timeout).

This script provides a basic framework. Feel free to extend it with more advanced features!
