from Database import get_unused_posts

import os
import time

from tqdm import tqdm
from openai import OpenAI

VIDEO_DIR = './Videos'
client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")

def generate_videos(settings):
    posts = get_unused_posts()

    with tqdm(desc='Generating Videos', total=len(posts), unit=' Video(s)') as pbar:
        for post in posts:
            generate_video(post, None)
            pbar.update(1)
            time.sleep(1)

def generate_video(post, part_length, voice='af_alloy', speed=1):
    p_id = post[0]
    p_author = post[1]
    p_sub = post[2]
    p_title = post[3]
    p_content = post[4]
    p_score = post[9]
    p_comments = post[10]
    p_nsfw = post[11]

    save_name = f'{p_id} - {p_title}'
    output_dir = os.path.join(VIDEO_DIR, p_sub, save_name)

    os.makedirs(output_dir, exist_ok=True)

    with client.audio.speech.with_streaming_response.create(model='kokoro', voice='af_alloy', input=f'{p_title}\n{p_content}', speed=speed) as response:
        response.stream_to_file(f'{output_dir}/audio.mp3')