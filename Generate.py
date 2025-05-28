from Database import get_unused_posts

import os
import time
import random

from tqdm import tqdm

import requests
import base64
import json

from moviepy.editor import *
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

VIDEO_DIR = './Videos'

def generate_videos(settings):
    posts = get_unused_posts()

    with tqdm(desc='Generating Videos', total=len(posts), unit=' Video(s)') as pbar:
        for post in posts:
            p_id = post[0]
            p_author = post[1]
            p_sub = post[2]
            p_title = post[3]
            p_content = post[4]
            p_score = post[9]
            p_comments = post[10]
            p_nsfw = post[11]

            if len(p_title) > 100:
                save_name = f'{p_id} - {p_title[:100]}'
            else:
                save_name = f'{p_id} - {p_title}'

            output_dir = os.path.join(VIDEO_DIR, p_sub, save_name)
            post_content = f'{p_title}\n{p_content}'

            generate_audio(output_dir, post_content)
            generate_video(output_dir, 59, 'Videos/Background/minecraft.mp4')
            # break
            pbar.update(1)
            time.sleep(1)

def generate_audio(output_dir, post_content, voice='af_alloy', speed=1):
    if os.path.exists(output_dir):
        return

    os.makedirs(output_dir, exist_ok=True)

    response = requests.post(
        "http://localhost:8880/dev/captioned_speech", 

        json = {
            "model": "kokoro",
            "input": post_content,
            "voice": voice,
            "speed": speed,
            "response_format": "mp3",
            "stream": False
        },
        stream=False
    )

    with open(f'{output_dir}/audio.mp3', 'wb') as f:
        audio_json = json.loads(response.content)

        chunk_audio = base64.b64decode(audio_json['audio'].encode('utf-8'))

        f.write(chunk_audio)
        with open(f'{output_dir}/caption.json', 'w') as file:
            json.dump(audio_json['timestamps'], file, indent=4)


def generate_video(video_dir, max_length, background_video):
    subtitle_path = os.path.join(video_dir, "caption.json")
    audio_path = os.path.join(video_dir, "audio.mp3")

    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    bg_clip = VideoFileClip(background_video)

    max_start = max(0, bg_clip.duration - audio_duration)
    start_time = random.uniform(0, max_start)

    # Extract a segment of the background video matching the audio length
    bg_segment = bg_clip.subclip(start_time, start_time + audio_duration)

    # Crop to portrait 9:16 (keeping full height)
    new_width = int(bg_segment.h * 9 / 16)
    x1 = (bg_segment.w - new_width) // 2
    x2 = x1 + new_width
    bg_segment = crop(bg_segment, x1=x1, x2=x2, y1=0, y2=bg_segment.h)

    # Load subtitles
    with open(subtitle_path, "r") as file:
        captions = json.load(file)

    subs = [((cap["start_time"], cap["end_time"]), cap["word"]) for cap in captions]
    generator = lambda txt: TextClip(
        txt, font="Arial-Bold", fontsize=100, color="white"
    )
    subtitles = SubtitlesClip(subs, generator)

    # Combine video, audio, and subtitles
    result = CompositeVideoClip(
        [bg_segment, subtitles.set_position(("center", "center"))]
    )
    result = result.set_audio(audio_clip)

    # Save full version
    result.write_videofile(
        f"{video_dir}/final.mp4",
        fps=bg_segment.fps,
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        codec="libx264",
        audio_codec="aac",
    )

    # Split into parts if needed
    os.makedirs(f"{video_dir}/parts", exist_ok=True)

    true_duration = min(result.duration, audio_clip.duration)

    if true_duration <= max_length:
        result.write_videofile(
            f"{video_dir}/parts/1.mp4",
            fps=bg_segment.fps,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            codec="libx264",
            audio_codec="aac",
        )
    else:
        total_parts = int(true_duration // max_length)
        if true_duration % max_length != 0:
            total_parts += 1

        for i in range(total_parts):
            start = i * max_length
            end = min((i + 1) * max_length, true_duration)

            part = result.subclip(start, end)
            part.write_videofile(
                f"{video_dir}/parts/{i+1}.mp4",
                fps=bg_segment.fps,
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                codec="libx264",
                audio_codec="aac",
            )
