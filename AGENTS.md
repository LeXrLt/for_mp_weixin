## Development Guidelines for ImageDownloaderApp

This document provides guidelines for agents modifying or extending the `ImageDownloaderApp` (`get_photos.py`).

### Core Technologies
- **GUI:** Tkinter
- **Asynchronous Operations:** `asyncio`
- **HTTP Requests:** `aiohttp`
- **Threading:** The `threading` module is used to run the `asyncio` event loop in a separate thread to keep the Tkinter GUI responsive.

### Key Architectural Points
1.  **GUI Responsiveness:** All long-running tasks, especially network operations (downloads), MUST be performed asynchronously or in separate threads to avoid freezing the GUI. The current implementation uses an `asyncio` event loop running in a dedicated thread, and `asyncio.run_coroutine_threadsafe` is used to schedule coroutines on this loop from the main (Tkinter) thread.
2.  **Error Handling:**
    *   Downloads should be resilient. The current `download_image` function implements a retry mechanism (3 attempts with a 2-second delay). Maintain or improve this.
    *   Clear feedback should be provided to the user for both successful and failed operations via the GUI's progress area and status label.
    *   Catch specific exceptions where possible (e.g., `aiohttp.ClientError`, `asyncio.TimeoutError`) and provide informative error messages.
3.  **File Handling:**
    *   Images are saved to the `downloads` sub-directory. This directory is created if it doesn't exist.
    *   File naming should attempt to generate unique names. The current implementation uses `image_{counter}{extension}`.
    *   File extension detection logic (Content-Disposition, URL, Content-Type) should be maintained or improved for accuracy.
4.  **URL Parsing:** The application should be flexible in accepting URL inputs. Currently, it extracts URLs from plain text (space or line separated) and markdown-formatted links. Ensure any changes to URL parsing maintain or enhance this flexibility and include basic validation.
5.  **Dependencies:**
    *   `aiohttp` is the only external dependency. If adding new dependencies, list them and provide installation instructions (e.g., in `README.md`).
    *   The script uses standard Python libraries like `tkinter`, `asyncio`, `os`, `re`, `urllib.parse`, and `threading`.

### Making Changes
- **Testing:** Before submitting changes, manually test the application with:
    - Valid image URLs (various types: JPG, PNG, GIF).
    - Invalid or broken URLs.
    - URLs leading to non-image content.
    - A large batch of URLs to test concurrency and responsiveness.
    - No input / empty input.
- **GUI Updates from Threads:** When updating Tkinter widgets from code running in the `asyncio` thread (e.g., within an `async` function), ensure these updates are thread-safe. Tkinter is not generally thread-safe. The current `log_message` function is called from async code but updates Tkinter elements; this is made safe because `log_message` itself is called via `asyncio.run_coroutine_threadsafe` which effectively marshals the execution of `download_all_images` (and thus its calls to `log_message`) to be managed by the asyncio loop, and Tkinter updates happen fast enough or are queued. For more complex GUI updates initiated directly from the asyncio thread, consider using `master.after(0, callback)` or a thread-safe queue if direct calls cause issues. *Correction*: `log_message` is called directly from the asyncio thread. `self.master.update_idletasks()` is used which should be safe. For more complex direct GUI manipulations from the async thread, using `app.master.after(0, lambda: update_gui_stuff())` is a robust pattern.
- **Code Clarity:** Maintain clear variable names and add comments for complex logic.

### Future Enhancements (Ideas)
- Allow user to select download directory.
- Progress bar for individual downloads or overall progress.
- Option to customize retry attempts and timeouts.
- Thumbnail previews.
- Pause/Resume downloads.

Remember to update this `AGENTS.md` if significant architectural changes or new conventions are introduced.
