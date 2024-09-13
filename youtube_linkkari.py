from flask import Flask, request, jsonify, render_template, send_from_directory
from youtube_transcript_api import YouTubeTranscriptApi
import re
from openai import OpenAI
import os

app = Flask(__name__, static_folder='static')

# Lue OpenAI API-avain tiedostosta
def read_api_key(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except IOError:
        print(f"Virhe: Tiedostoa {filename} ei voitu lukea.")
        return None

# Aseta OpenAI API-avain
api_key = read_api_key("openai_api_key.txt")
if not api_key:
    print("API-avainta ei voitu asettaa. Ohjelma lopetetaan.")
    exit()

# Alusta OpenAI client
client = OpenAI(api_key=api_key)

def get_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    else:
        return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Virhe transkriptin hakemisessa: {e}")
        return None

def create_linkedin_post(transcript):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Tee tästä videon transkriptiosta LinkedIn-päivitys. Tee siitä max 300 merkkiä pitkä. Tee se suomeksi. Transkriptio: {transcript}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Virhe LinkedIn-päivityksen luomisessa: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/process', methods=['POST'])
def process_video():
    url = request.json['url']
    video_id = get_video_id(url)
    
    if not video_id:
        return jsonify({"error": "Virheellinen YouTube URL."}), 400
    
    transcript_text = get_transcript(video_id)
    
    if transcript_text:
        linkedin_post = create_linkedin_post(transcript_text)
        if linkedin_post:
            return jsonify({
                "transcript": transcript_text,
                "linkedin_post": linkedin_post
            })
        else:
            return jsonify({"error": "LinkedIn-päivityksen luominen epäonnistui."}), 500
    else:
        return jsonify({"error": "Transkriptin hakeminen epäonnistui."}), 500

if __name__ == "__main__":
    app.run(debug=True)