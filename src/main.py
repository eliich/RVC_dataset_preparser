import tkinter as tk
from tkinter import filedialog
import os
import re

def parse_srt_file(srt_path):
    """
    Parse an SRT file to extract start and end times for each subtitle.
    """
    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regular expression to find all time codes in the SRT file.
    pattern = re.compile(r'\d+\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    times = pattern.findall(content)
    
    return [(start, end) for start, end in times]

def select_folder():
    """
    Open a dialog to select a folder, then find all SRT files and their corresponding
    media files within that folder to prepare video subtitles list.
    """
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
        video_subtitles = []
        
        for file in os.listdir(folder_path):
            if file.endswith(".srt"):
                base_name = os.path.splitext(file)[0]
                srt_path = os.path.join(folder_path, file)
                times = parse_srt_file(srt_path)
                
                # Check for corresponding media file with the same base name but different extensions.
                for ext in ['.mp4', '.mkv', '.avi']:  # Add other video formats as needed
                    media_path = os.path.join(folder_path, base_name + ext)
                    if os.path.exists(media_path):
                        # Normalize the path to ensure consistent backslashes on Windows.
                        media_path = os.path.normpath(media_path)
                        for start, end in times:
                            video_subtitles.append({
                                "start_time": start,
                                "end_time": end,
                                "media_path": media_path,  # Now using backslashes consistently
                                "audio_segment_path": "none"  # Placeholder for now
                            })
                        break  # Stop searching once the corresponding media file is found
        
        # Debug print to check the output. You might want to handle this data differently in a real application.
        for subtitle in video_subtitles:
            print(subtitle)
    else:
        print("No folder was selected.")

root = tk.Tk()
root.title("Folder Selection")

button = tk.Button(root, text="Select Folder", command=select_folder)
button.pack(pady=20)

root.mainloop()
