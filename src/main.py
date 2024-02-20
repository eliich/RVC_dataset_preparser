import tkinter as tk
from tkinter import filedialog
import os
import pysrt
from moviepy.editor import AudioFileClip
import tempfile
import shutil

def create_temp_subdir(subdir_name="RVC_dataset_preparser"):
    # Creates a subdirectory within the system's temp directory
    temp_dir = os.path.join(tempfile.gettempdir(), subdir_name)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def cleanup_temp_subdir(subdir_path):
    # Deletes the specified temporary subdirectory and its contents
    if os.path.exists(subdir_path):
        shutil.rmtree(subdir_path)
        print(f"Cleaned up temporary directory: {subdir_path}")
    else:
        print("Temporary directory does not exist. No cleanup needed.")

def segment_media_files(folder_path, temp_dir):
    for file in os.listdir(folder_path):
        if file.endswith(('.mp4', '.mp3', '.wav')):
            media_file_path = os.path.join(folder_path, file)
            srt_file_path = os.path.splitext(media_file_path)[0] + '.srt'

            if os.path.exists(srt_file_path):
                subs = pysrt.open(srt_file_path)
                with AudioFileClip(media_file_path) as audio_clip:
                    duration = audio_clip.duration  # Get the duration of the media file

                    for index, sub in enumerate(subs, start=1):
                        start_time = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000
                        end_time = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000

                        # Ensure the end_time does not exceed the media file's duration
                        end_time = min(end_time, duration)

                        # Skip segments that start after the media file ends
                        if start_time >= duration:
                            continue

                        segment = audio_clip.subclip(start_time, end_time)
                        output_file_path = os.path.join(temp_dir, f"{os.path.splitext(file)[0]}_segment_{index}.mp3")
                        segment.write_audiofile(output_file_path, codec='mp3')
                        print(f"Segment {index} saved: {output_file_path}")

def select_folder():
    # Opens a dialog for folder selection and processes the selected folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
        temp_dir = create_temp_subdir()  # Create or get the temp subdir path
        segment_media_files(folder_path, temp_dir)
        print(f"All segments saved to: {temp_dir}")
        # You can call cleanup_temp_subdir(temp_dir) here or at another appropriate time
    else:
        print("No folder was selected.")

# Create the main window
root = tk.Tk()
root.title("Folder Selection and Media Segmentation")

# Create a button for selecting folders and segmenting media
select_folder_button = tk.Button(root, text="Select Folder and Segment Media", command=select_folder)
select_folder_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()

# Example of calling the cleanup function on app close or after successful dataset parsing:
# cleanup_temp_subdir(create_temp_subdir())
