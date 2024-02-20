# Import required modules
import tkinter as tk
from tkinter import filedialog, ttk
import os
import pysrt
from moviepy.editor import AudioFileClip, concatenate_audioclips
import tempfile
import shutil
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Global variables
audio_segments = []
current_segment_index = 0
selected_segments = []
action_history = []

def create_temp_subdir(subdir_name="RVC_dataset_preparser"):
    temp_dir = os.path.join(tempfile.gettempdir(), subdir_name)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def cleanup_temp_subdir(subdir_path):
    if os.path.exists(subdir_path):
        shutil.rmtree(subdir_path)
        print(f"Cleaned up temporary directory: {subdir_path}")
    else:
        print("Temporary directory does not exist. No cleanup needed.")

def segment_media_files(folder_path, temp_dir):
    global audio_segments
    audio_segments = []
    files_to_process = [file for file in os.listdir(folder_path) if file.endswith(('.mp4', '.mp3', '.wav'))]
    
    progress_var.set(0)
    estimated_total_segments = sum([len(pysrt.open(os.path.splitext(os.path.join(folder_path, file))[0] + '.srt'))
                                    for file in files_to_process if os.path.exists(os.path.splitext(os.path.join(folder_path, file))[0] + '.srt')])
    progress_step = 100 / estimated_total_segments if estimated_total_segments else 0
    progress_bar['maximum'] = 100
    
    for file in files_to_process:
        media_file_path = os.path.join(folder_path, file)
        srt_file_path = os.path.splitext(media_file_path)[0] + '.srt'

        if os.path.exists(srt_file_path):
            subs = pysrt.open(srt_file_path)
            with AudioFileClip(media_file_path) as audio_clip:
                for index, sub in enumerate(subs, start=1):
                    start_time = sub.start.ordinal / 1000
                    end_time = min(sub.end.ordinal / 1000, audio_clip.duration)
                    
                    segment = audio_clip.subclip(start_time, end_time)
                    output_file_path = os.path.join(temp_dir, f"{os.path.splitext(file)[0]}_segment_{index}.mp3")
                    segment.write_audiofile(output_file_path, codec='mp3')
                    audio_segments.append(output_file_path)
                    print(f"Segment {index} saved: {output_file_path}")
                    
                    progress_var.set(progress_var.get() + progress_step)
                    root.update_idletasks()
    play_next_segment()

def play_next_segment():
    global current_segment_index
    if current_segment_index < len(audio_segments):
        pygame.mixer.music.load(audio_segments[current_segment_index])
        pygame.mixer.music.play(-1)
        if current_segment_index not in action_history:
            action_history.append(current_segment_index)
        update_position_label()
    else:
        print("No more segments to play.")

def toggle_playback():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def save_and_next():
    global current_segment_index
    if current_segment_index < len(audio_segments):
        selected_segments.append(audio_segments[current_segment_index])
        print(f"Saved: {audio_segments[current_segment_index]}")
        current_segment_index += 1
        if current_segment_index >= len(audio_segments):  # Check if it's the last segment
            concatenate_and_save_final_output()  # Call the function here
        else:
            play_next_segment()
    else:
        print("No more segments to save and play.")

def skip_and_next():
    global current_segment_index
    if current_segment_index < len(audio_segments) - 1:
        current_segment_index += 1
        play_next_segment()
    else:
        print("No more segments to skip and play.")

def redo_last_action():
    global current_segment_index
    if action_history:
        if len(action_history) > 1:
            last_action_index = action_history.pop()
            current_segment_index = action_history[-1]
            if audio_segments[current_segment_index] in selected_segments:
                selected_segments.remove(audio_segments[current_segment_index])
                print(f"Removed: {audio_segments[current_segment_index]}")
        play_next_segment()
    else:
        print("No previous action to redo.")

def select_folder():
    global current_segment_index, action_history
    current_segment_index = 0
    action_history = []
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
        temp_dir = create_temp_subdir()
        segment_media_files(folder_path, temp_dir)
        print(f"All segments saved to: {temp_dir}")
    else:
        print("No folder was selected.")

def update_position_label():
    position_text.set(f"Segment: {current_segment_index + 1}/{len(audio_segments)}")

def concatenate_and_save_final_output():
    global selected_segments
    if not selected_segments:
        print("No segments selected for concatenation.")
        return
    
    audio_clips = [AudioFileClip(segment) for segment in selected_segments]
    final_clip = concatenate_audioclips(audio_clips)
    final_output_path = os.path.join(create_temp_subdir(), "finalOutput.mp3")
    final_clip.write_audiofile(final_output_path, codec='mp3')
    print(f"Final output saved to: {final_output_path}")
    
    for clip in audio_clips:
        clip.close()
    final_clip.close()

root = tk.Tk()
root.title("Folder Selection and Media Segmentation")

select_folder_button = tk.Button(root, text="Select Folder and Segment Media", command=select_folder)
select_folder_button.pack(pady=20)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, mode='determinate')
progress_bar.pack(pady=20)

playback_button = tk.Button(root, text="Toggle Playback", command=toggle_playback)
playback_button.pack(pady=20)

save_and_next_button = tk.Button(root, text="Save and Play Next", command=save_and_next)
save_and_next_button.pack(pady=20)

skip_and_next_button = tk.Button(root, text="Skip and Play Next", command=skip_and_next)
skip_and_next_button.pack(pady=20)

redo_button = tk.Button(root, text="Redo Last Action", command=redo_last_action)
redo_button.pack(pady=20)

position_text = tk.StringVar()
position_label = tk.Label(root, textvariable=position_text)
position_label.pack(pady=20)
update_position_label()

root.mainloop()
