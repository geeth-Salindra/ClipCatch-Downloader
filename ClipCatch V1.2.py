import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os


DOWNLOAD_FOLDER = r"C:\Users\geeth\Downloads\ClipCatch"

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Global variable to hold the download process
download_process = None

def download_video():
    global download_process
    url = url_entry.get()
    quality = quality_combo.get()

    if not url:
        messagebox.showerror("Error", "Please provide the video URL")
        return

    if not quality:
        messagebox.showerror("Error", "Please select a video quality")
        return

    # Define the output path with a filename format
    output_path = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    # Set the format selection based on quality without restricting to YouTube format codes
    quality_options = {
        "240p": "best[height<=240]",
        "360p": "best[height<=360]",
        "480p": "best[height<=480]",
        "720p": "best[height<=720]",
        "1080p": "best[height<=1080]"
    }
    format_option = quality_options.get(quality, "best")

    # Build the yt-dlp command with progress information
    command = [
        "yt-dlp",
        "-f", format_option,
        "-o", output_path,
        "--newline",
        url
    ]

    # Update UI to indicate download in progress
    progress_label.config(text="Downloading...")
    download_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)
    progress_bar.start()

    # Run yt-dlp in a separate process and read its output without showing cmd
    download_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW  # Suppress command prompt window
    )

    # Read output line by line
    for line in download_process.stdout:
        if "ETA" in line:
            parts = line.split()
            if "%" in parts:
                percent_index = parts.index("%") - 1
                percentage = parts[percent_index]
                progress_bar['value'] = float(percentage)
            if "of" in parts:
                size_index = parts.index("of") + 1
                downloaded_size = parts[size_index - 2]
                total_size = parts[size_index]
                progress_label.config(text=f"Downloaded: {downloaded_size} / {total_size}")

        root.update_idletasks()

    # Check download result and update UI
    if download_process.returncode == 0:
        messagebox.showinfo("Success", f"Video downloaded successfully to {DOWNLOAD_FOLDER}!")
        url_entry.delete(0, tk.END)
    else:
        messagebox.showwarning(
            "Download Issue",
            "The download could not proceed. Possible reasons include:\n"
            "- Video quality not available\n"
            "- Download was canceled\n"
            "- Invalid link or unsupported site\n"
            "- Video already downloaded"
        )

    # Reset UI elements
    progress_label.config(text="")
    download_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)
    progress_bar.stop()
    progress_bar['value'] = 0
    download_process = None

def start_download():
    # Start download in a separate thread
    download_thread = threading.Thread(target=download_video)
    download_thread.start()

def cancel_download():
    global download_process
    if download_process and download_process.poll() is None:
        download_process.terminate()
        messagebox.showinfo("Cancelled", "Download has been cancelled.")
        # Reset UI elements
        progress_label.config(text="")
        download_button.config(state=tk.NORMAL)
        cancel_button.config(state=tk.DISABLED)
        progress_bar.stop()
        progress_bar['value'] = 0
        download_process = None

# GUI
root = tk.Tk()
root.title("ClipCatch")
root.geometry("280x150")
root.resizable(False, False)


url_frame = tk.Frame(root)
url_frame.pack(pady=5)
tk.Label(url_frame, text="Video URL:").pack(side=tk.LEFT, padx=5)
url_entry = tk.Entry(url_frame, width=30)
url_entry.pack(side=tk.LEFT)


quality_progress_frame = tk.Frame(root)
quality_progress_frame.pack(pady=5)

# Quality selection combo box
tk.Label(quality_progress_frame, text="Quality:").pack(side=tk.LEFT, padx=5)
quality_combo = ttk.Combobox(quality_progress_frame, values=["240p", "360p", "480p", "720p", "1080p"], width=10)
quality_combo.pack(side=tk.LEFT, padx=5)
quality_combo.set("720p")  # Default selection


progress_bar = ttk.Progressbar(quality_progress_frame, mode='determinate', length=100)
progress_bar.pack(side=tk.LEFT, padx=5)


progress_label = tk.Label(root, text="Downloaded: 0 B / 0 B")
progress_label.pack()


button_frame = tk.Frame(root)
button_frame.pack(pady=10)
download_button = tk.Button(button_frame, text="Download", command=start_download)
download_button.pack(side=tk.LEFT, padx=5)
cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_download, state=tk.DISABLED)
cancel_button.pack(side=tk.LEFT)

root.mainloop()
