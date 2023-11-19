from __future__ import print_function, division
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

class VideoRecorder:
    """Video class based on openCV"""

    def __init__(self, name="temp_video.avi", fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30):
        self.open = True
        self.device_index = camindex
        self.fps = fps
        self.fourcc = fourcc
        self.frame_size = (sizex, sizey)
        self.video_filename = name
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frame_size)
        self.frame_counts = 1
        self.start_time = time.time()

    def record(self):
        """Video starts being recorded"""
        timer_start = time.time()
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                self.frame_counts += 1
                time.sleep(1/self.fps)
            else:
                break

    def stop(self):
        """Finishes the video recording therefore the thread too"""
        if self.open:
            self.open = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

    def start(self):
        """Launches the video recording function using a thread"""
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

class AudioRecorder:
    """Audio class based on pyAudio and Wave"""

    def __init__(self, filename="temp_audio.wav", rate=44100, fpb=2**12, channels=1, audio_index=0):
        self.open = True
        self.rate = rate
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio_filename = filename
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=audio_index,
            frames_per_buffer=self.frames_per_buffer
        )
        self.audio_frames = []

    def record(self):
        """Audio starts being recorded"""
        self.stream.start_stream()
        t_start = time.time_ns()
        while self.open:
            try:
                data = self.stream.read(self.frames_per_buffer)
                self.audio_frames.append(data)
            except Exception as e:
                print(f'PyAudio read exception at {((time.time_ns() - t_start) / 10**6):.1f}ms')
                print(e)
            time.sleep(0.01)
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        wave_file = wave.open(self.audio_filename, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()

    def stop(self):
        """Finishes the audio recording therefore the thread too"""
        if self.open:
            self.open = False

    def start(self):
        """Launches the audio recording function using a thread"""
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

def start_av_recording(filename="test", audio_index=0, sample_rate=44100):
    global video_thread
    global audio_thread
    video_thread = VideoRecorder()
    audio_thread = AudioRecorder(audio_index=audio_index, rate=sample_rate)
    audio_thread.start()
    video_thread.start()
    return filename

def start_video_recording(filename="test"):
    global video_thread
    video_thread = VideoRecorder()
    video_thread.start()
    return filename

def start_audio_recording(filename="test", audio_index=0, sample_rate=44100):
    global audio_thread
    audio_thread = AudioRecorder(audio_index=audio_index, rate=sample_rate)
    audio_thread.start()
    return filename

def stop_av_recording(filename="test"):
    audio_thread.stop()
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print(f"total frames {frame_counts}")
    print(f"elapsed time {elapsed_time}")
    print(f"recorded fps {recorded_fps}")
    video_thread.stop()

    # Makes sure the threads have finished
    while threading.active_count() > 1:
        time.sleep(1)

    # Merging audio and video signal
    if abs(recorded_fps - 6) >= 0.01:
        # If the fps rate was higher/lower than expected, re-encode it to the expected
        print("Re-encoding")
        cmd = f"ffmpeg -r {recorded_fps} -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        subprocess.call(cmd, shell=True)
        print("Muxing")
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p {filename}.avi"
        subprocess.call(cmd, shell=True)
    else:
        print("Normal recording\nMuxing")
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p {filename}.avi"
        subprocess.call(cmd, shell=True)
        print("..")

def file_manager(filename="test"):
    """Required and wanted processing of final files"""
    local_path = os.getcwd()
    audio_path = os.path.join(local_path, "temp_audio.wav")
    video_path = os.path.join(local_path, "temp_video.avi")
    video_path2 = os.path.join(local_path, "temp_video2.avi")

    for file_path in [audio_path, video_path, video_path2]:
        if os.path.exists(file_path):
            os.remove(file_path)

def list_audio_devices(name_filter=None):
    """List available audio devices"""
    pa = pyaudio.PyAudio()
    device_index = None
    sample_rate = None

    for x in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(x)
        print(info)
        if name_filter is not None and name_filter in info['name']:
            device_index = info['index']
            sample_rate = int(info['defaultSampleRate'])
            break

    return device_index, sample_rate

if __name__ == '__main__':
    start_av_recording()
    time.sleep(10)
    stop_av_recording()
    file_manager()
