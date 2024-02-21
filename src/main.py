import tkinter as tk
from tkinter import filedialog
import os
import re
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile

class SubtitleProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.video_subtitles = []

    def run(self):
        self.process_folder()
        self.display_results()

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
            clip = AudioFileClip(media_path).subclip(start_sec, end_sec)
        else:
            clip = VideoFileClip(media_path).subclip(start_sec, end_sec).audio
        
        temp_dir = os.path.join(tempfile.gettempdir(), "RVC_dataset_preparser")
        os.makedirs(temp_dir, exist_ok=True)
        
        unique_file_name = f"{os.path.basename(media_path).split('.')[0]}_{start.replace(':', '-').replace(',', '-')}_to_{end.replace(':', '-').replace(',', '-')}.wav"
        temp_audio_path = os.path.join(temp_dir, unique_file_name)
        
        clip.write_audiofile(temp_audio_path, codec='pcm_s16le')
        
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

    def display_results(self):
        for subtitle in self.video_subtitles:
            print(subtitle)

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        processor = SubtitleProcessor(folder_path)
        processor.run()
    else:
        print("No folder was selected.")

def main():
    root = tk.Tk()
    root.title("Subtitle Processor")
    
    tk.Button(root, text="Select Folder", command=select_folder).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
