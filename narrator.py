import os
from openai import OpenAI
import base64
import json
import time
import simpleaudio as sa
import streamlit as st
import errno
import cv2
import time
from PIL import Image
import numpy as np
from elevenlabs import generate, play, set_api_key, voices
set_api_key(os.environ["ELEVENLABS_API_KEY"])
#set_api_key("134993a2ff0e8b929f49745f2a71a107")

client = OpenAI()

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    audio = generate(text, voice="TZY96Oh4Q5dZBOvjcuK8", model = "eleven_monolingual_v1") #Dora the Explorer voice

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio) # used without streamlit


def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are Dora the Explorer from the animated TV show. Narrate the picture of the human as if it is a character from Dora the Explorer.
                Make it cute and exciting. Sing a song like Dora. If I do anything remotely interesting, make a big deal about it!  
                """,
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text   


def main():
    script = []
    # path to your image
    image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

    # getting the base64 encoding
    base64_image = encode_image(image_path)

    # analyze posture
    print("👀 Dora is watching you...")
    analysis = analyze_image(base64_image, script=script)

    print("🎙️ Dora says:")
    print(analysis)
                
    play_audio(analysis) # 

    script = script + [{"role": "assistant", "content": analysis}]

    # wait for 5 seconds
    #time.sleep(5)


if __name__ == "__main__":
    main()
