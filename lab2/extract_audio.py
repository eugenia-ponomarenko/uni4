import moviepy.editor

def extract_audio_from_video(video_path, audio_output_path):
    try:
        with moviepy.editor.VideoFileClip(video_path) as video:
            audio = video.audio
            audio.write_audiofile(audio_output_path, codec='mp3')
        print("Audio successfully extracted.")
    except Exception as e:
        print(f"An error occurred: {e}")

extract_audio_from_video("lab2.mp4", "audio.mp3")
