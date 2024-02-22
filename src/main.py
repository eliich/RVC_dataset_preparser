import tkinter as tk
from tkinter import filedialog
import os
import re
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile
import shutil
import pygame  # Import pygame for audio playback

class SubtitleProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.video_subtitles = []

    def run(self):
        self.clear_temp_directory()
        self.process_folder()
        return self.video_subtitles

    def clear_temp_directory(self):
        temp_dir = os.path.join(tempfile.gettempdir(), "RVC_dataset_preparser")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

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
    
        end_sec = min(end_sec, clip.duration)
    
        subclip = clip.subclip(start_sec, end_sec)
    
        temp_dir = os.path.join(tempfile.gettempdir(), "RVC_dataset_preparser")
        os.makedirs(temp_dir, exist_ok=True)
    
        unique_file_name = f"{os.path.basename(media_path).split('.')[0]}_{start.replace(':', '-').replace(',', '-')}_to_{end.replace(':', '-').replace(',', '-')}.wav"
        temp_audio_path = os.path.join(temp_dir, unique_file_name)
    
        subclip.write_audiofile(temp_audio_path, codec='pcm_s16le')
    
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

global root

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        processor = SubtitleProcessor(folder_path)
        video_subtitles = processor.run()
        if video_subtitles:
            pygame.mixer.init()
            play_audio_segment(video_subtitles[0]['audio_segment_path'])
            setup_gui_for_audio_control(video_subtitles)
        else:
            print("No audio segments were processed.")
    else:
        print("No folder was selected.")

def play_audio_segment(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)  # Loop indefinitely

def stop_audio():
    pygame.mixer.music.stop()

def setup_gui_for_audio_control(video_subtitles):
    for widget in root.winfo_children():
        widget.destroy()  # Clear the window before adding new elements

    current_index = [0]
    saved_segments = []
    action_history = []

    # Define a label for displaying the current position
    position_label = tk.Label(root, text=f"Current Position: {current_index[0]+1}/{len(video_subtitles)}")
    position_label.pack(pady=5)

    def update_current_position_label():
        # Update the label text to reflect the current index and total segments
        position_label.config(text=f"Current Position: {current_index[0]+1}/{len(video_subtitles)}")

    def log_saved_segments():
        print("Saved Segments' Audio Paths:")
        for segment in saved_segments:
            print(segment['audio_segment_path'])

    def skip():
        if current_index[0] + 1 < len(video_subtitles):
            action_history.append(('skip', current_index[0]))
            current_index[0] += 1
            play_audio_segment(video_subtitles[current_index[0]]['audio_segment_path'])
            update_current_position_label()

    def add_and_skip():
        if current_index[0] < len(video_subtitles):
            saved_segments.append(video_subtitles[current_index[0]])
            action_history.append(('add_and_skip', current_index[0]))
            current_index[0] += 1
            log_saved_segments()
            update_current_position_label()
            if current_index[0] < len(video_subtitles):
                play_audio_segment(video_subtitles[current_index[0]]['audio_segment_path'])

    def redo_last_choice():
        if action_history:
            last_action, index = action_history.pop()
            if last_action == 'skip':
                current_index[0] = index
                play_audio_segment(video_subtitles[current_index[0]]['audio_segment_path'])
            elif last_action == 'add_and_skip':
                if saved_segments and video_subtitles[index] in saved_segments:
                    saved_segments.remove(video_subtitles[index])
                    log_saved_segments()
                current_index[0] = index
                play_audio_segment(video_subtitles[current_index[0]]['audio_segment_path'])
            update_current_position_label()

    def pause_resume():
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    tk.Button(root, text="Skip", command=skip).pack(pady=5)
    tk.Button(root, text="Add & Skip", command=add_and_skip).pack(pady=5)
    tk.Button(root, text="Redo Last Choice", command=redo_last_choice).pack(pady=5)
    tk.Button(root, text="Pause/Resume", command=pause_resume).pack(pady=5)

    # Initially update the current position label
    update_current_position_label()


def main():
    global root
    root = tk.Tk()
    root.title("Subtitle Processor")
    tk.Button(root, text="Select Folder", command=select_folder).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
