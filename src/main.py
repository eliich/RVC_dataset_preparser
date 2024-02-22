import tkinter as tk
from tkinter import filedialog
import os
import re
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile
import shutil
import pygame  # Import pygame for audio playback
import os

class SubtitleProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.video_subtitles = []

    def run(self):
        self.clear_temp_directory()
        self.process_folder()
        # self.display_results()  # This line has been commented out
        return self.video_subtitles  # Returning the list of video subtitles

    def clear_temp_directory(self):
        temp_dir = os.path.join(tempfile.gettempdir(), "RVC_dataset_preparser")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)  # Recreate the directory for this run's files

    def process_folder(self):
        for file in os.listdir(self.folder_path):
            if file.endswith(".srt"):
                self.process_srt_file(file)

    def process_srt_file(self, file_name):
        srt_path = os.path.join(self.folder_path, file_name)
        base_name = os.path.splitext(file_name)[0]
        times = self.parse_srt_file(srt_path)

        for media_ext in ['.mp4', '.mkv', '.avi', '.mp3', '.wav']:
            media_path = os.path.join(self.folder_path, base_name + media_ext)
            if os.path.exists(media_path):
                self.process_media_file(media_path, times)
                break

    def process_media_file(self, media_path, times):
        file_ext = os.path.splitext(media_path)[1].lower()
        is_audio = file_ext in ['.mp3', '.wav']
        for start, end in times:
            audio_segment_path = self.segment_audio(start, end, media_path, is_audio=is_audio)
            self.video_subtitles.append({
                "start_time": start,
                "end_time": end,
                "media_path": media_path,
                "audio_segment_path": audio_segment_path
            })

    @staticmethod
    def parse_srt_file(srt_path):
        pattern = re.compile(r'\d+\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
        with open(srt_path, 'r', encoding='utf-8') as file:
            content = file.read()
        times = pattern.findall(content)
        return [(start, end) for start, end in times]

    def segment_audio(self, start, end, media_path, is_audio):
        start_sec = SubtitleProcessor.timecode_to_seconds(start)
        end_sec = SubtitleProcessor.timecode_to_seconds(end)
    
        if is_audio:
            clip = AudioFileClip(media_path)
        else:
            clip = VideoFileClip(media_path).audio
    
        end_sec = min(end_sec, clip.duration)  # Ensure the end_sec does not exceed the clip's duration
    
        subclip = clip.subclip(start_sec, end_sec)  # Extract the subclip based on adjusted start and end times
    
        temp_dir = os.path.join(tempfile.gettempdir(), "RVC_dataset_preparser")
        os.makedirs(temp_dir, exist_ok=True)
    
        unique_file_name = f"{os.path.basename(media_path).split('.')[0]}_{start.replace(':', '-').replace(',', '-')}_to_{end.replace(':', '-').replace(',', '-')}.wav"
        temp_audio_path = os.path.join(temp_dir, unique_file_name)
    
        subclip.write_audiofile(temp_audio_path, codec='pcm_s16le')  # Write the subclip to a .wav file
    
        return temp_audio_path

    @staticmethod
    def timecode_to_seconds(timecode):
        hours, minutes, seconds_milliseconds = timecode.split(':')
        seconds, milliseconds = seconds_milliseconds.split(',')
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        milliseconds = int(milliseconds)
        return 3600 * hours + 60 * minutes + seconds + milliseconds / 1000.0

    # The display_results method is still here, but not called in run()
    def display_results(self):
        for subtitle in self.video_subtitles:
            print(subtitle)

# Additional functions for playing audio and GUI controls
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        processor = SubtitleProcessor(folder_path)
        video_subtitles = processor.run()
        if video_subtitles:
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()
            play_audio_segment(video_subtitles[0]['audio_segment_path'])
            
            # Setup GUI for skip and add/skip buttons
            setup_gui_for_audio_control(video_subtitles)
        else:
            print("No audio segments were processed.")
    else:
        print("No folder was selected.")

def play_audio_segment(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)  # Play the audio in loop

def stop_audio():
    pygame.mixer.music.stop()

def setup_gui_for_audio_control(video_subtitles):
    def skip():
        nonlocal current_index
        if current_index + 1 < len(video_subtitles):
            current_index += 1
            play_audio_segment(video_subtitles[current_index]['audio_segment_path'])
        else:
            print("No more audio segments.")
            stop_audio()

    def add_and_skip():
        # Add the current segment to a new list for further processing
        saved_segments.append(video_subtitles[current_index])
        print("Current saved segments list:", saved_segments)  # Log the entire saved_segments list
        skip()  # Then skip to the next segment

    def pause_resume():
        nonlocal is_paused
        if is_paused:
            pygame.mixer.music.unpause()
            is_paused = False
            pause_resume_button.config(text="Pause")
        else:
            pygame.mixer.music.pause()
            is_paused = True
            pause_resume_button.config(text="Resume")

    # Initial setup
    current_index = 0
    saved_segments = []
    is_paused = False  # Keep track of the pause state

    # Create skip and add/skip buttons
    skip_button = tk.Button(root, text="Skip", command=skip)
    skip_button.pack(pady=5)

    add_skip_button = tk.Button(root, text="Add & Skip", command=add_and_skip)
    add_skip_button.pack(pady=5)

    # Create pause/resume button
    pause_resume_button = tk.Button(root, text="Pause", command=pause_resume)
    pause_resume_button.pack(pady=5)

def main():
    global root  # Declare root as global to access it in setup_gui_for_audio_control
    root = tk.Tk()
    root.title("Subtitle Processor")
    
    tk.Button(root, text="Select Folder", command=select_folder).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()