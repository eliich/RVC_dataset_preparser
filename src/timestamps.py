import os
import tkinter as tk
from tkinter import filedialog

class Subtitle:
    def __init__(self, index, start_time, end_time, text, media_path):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.media_path = media_path

def parse_srt_file(file_path, media_path):
    subtitles = []
    media_dir = os.path.dirname(file_path)
    media_file_path = os.path.join(media_dir, media_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        index = None
        start_time = None
        end_time = None
        text = ''
        for line in lines:
            line = line.strip()
            if not line:
                if index is not None and start_time is not None and end_time is not None:
                    subtitles.append(Subtitle(index, start_time, end_time, text, media_file_path))
                    index = None
                    start_time = None
                    end_time = None
                    text = ''
            elif line.isdigit():
                index = int(line)
            elif ' --> ' in line:
                start, end = line.split(' --> ')
                start_time = start.strip()
                end_time = end.strip()
            else:
                text += line + ' '
    return subtitles

def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        video_subtitles = {}
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".srt"):
                file_path = os.path.join(folder_path, file_name)
                media_path = os.path.splitext(file_name)[0] + ".wav"  # Assuming WAV files
                subtitles = parse_srt_file(file_path, media_path)
                video_name = os.path.splitext(file_name)[0]
                video_subtitles[video_name] = subtitles
        print("Dictionary containing video filenames and subtitles:")
        print(video_subtitles)
        process_subtitles(video_subtitles)

def process_subtitles(subtitles_dict):
    if '1_Toby Keith - As Good As I Once Was [ldQrapQ4d0Y]_(Vocals)' in subtitles_dict:
        first_subtitle = subtitles_dict['1_Toby Keith - As Good As I Once Was [ldQrapQ4d0Y]_(Vocals)'][0]
        print("First subtitle:")
        print(f"Start Time: {first_subtitle.start_time}")
        print(f"End Time: {first_subtitle.end_time}")
        print(f"Text: {first_subtitle.text}")
        print(f"Media Path: {os.path.normpath(first_subtitle.media_path)}")
    else:
        print("No subtitles found for '1_Toby Keith - As Good As I Once Was [ldQrapQ4d0Y]_(Vocals)'")

root = tk.Tk()
root.title("Open Folder")

button = tk.Button(root, text="Open Folder", command=open_folder)
button.pack(pady=20)

root.mainloop()
