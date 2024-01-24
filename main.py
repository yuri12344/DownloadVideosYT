import tkinter as tk
from tkinter import ttk, messagebox
import json
from pytube import YouTube
import threading
import os


def add_to_json(url, name, quality):
    video_info = {"name": name, "url": url, "quality": quality}
    try:
        with open('videos.json', 'r+') as file:
            data = json.load(file)
            data.append(video_info)
            file.seek(0)
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", "Video added to the list successfully!")
        url_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        quality_combobox.set("720p")
    except FileNotFoundError:
        with open('videos.json', 'w') as file:
            json.dump([video_info], file, indent=4)
        messagebox.showinfo("Success", "Video added to the list successfully!")
        url_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        quality_combobox.set("720p")

def update_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining 
    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_var.set(percentage_of_completion)
    app.update_idletasks()

def download_video(video_info):
    try:
        yt = YouTube(video_info['url'], on_progress_callback=update_progress)
        video = yt.streams.filter(res=video_info['quality'], progressive=True, file_extension='mp4').first()
        if not video:
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video_info['name']:
            video_info['name'] = yt.title

        # Verifica e cria o caminho da pasta se necessário
        file_path = f"./videos/{video_info['name']}"
        if '/' in video_info['name']:
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Verifica a extensão do arquivo
        if not file_path.endswith('.mp4'):
            file_path += '.mp4'

        # Faz o download do vídeo
        video.download(filename=file_path)
    
        return f"Video downloaded: {yt.title} in {video.resolution}"
    except Exception as e:
        return f"Error downloading video: {e}"

def start_download():
    def thread_target():
        try:
            with open('videos.json', 'r') as file:
                videos = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "No videos to download.")
            return

        for video_info in videos:
            download_video(video_info)

    download_thread = threading.Thread(target=thread_target)
    download_thread.start()

app = tk.Tk()
app.title("YouTube Video Downloader")

tk.Label(app, text="Video URL:").pack(padx=10, pady=5)
url_entry = tk.Entry(app, width=50)
url_entry.pack(padx=10, pady=5)

tk.Label(app, text="Video Name:").pack(padx=10, pady=5)
tk.Label(app, text="/folder_name/video_name.mp4").pack(padx=10, pady=5)
tk.Label(app, text="If empty it will be YT video title").pack(padx=10, pady=5)
name_entry = tk.Entry(app, width=50)
name_entry.pack(padx=10, pady=5)

tk.Label(app, text="Quality:").pack(padx=10, pady=5)
quality_combobox = ttk.Combobox(app, values=["1080p", "720p", "480p", "360p"], state="readonly")
quality_combobox.pack(padx=10, pady=5)
quality_combobox.set("720p")

add_button = tk.Button(app, text="Add to List", command=lambda: add_to_json(url_entry.get(), name_entry.get(), quality_combobox.get()))
add_button.pack(padx=10, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=200, variable=progress_var, maximum=100)
progress_bar.pack(padx=10, pady=10)

download_button = tk.Button(app, text="Download Videos", command=start_download)
download_button.pack(padx=10, pady=10)

app.mainloop()
