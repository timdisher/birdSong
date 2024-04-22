import os
import random
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv



load_dotenv()
EBIRD_API_KEY = os.getenv('EBIRD_API_KEY')

app = Flask(__name__)



def get_nearby_birds(latitude, longitude):
    url = f'https://api.ebird.org/v2/data/obs/geo/recent?lat={latitude}&lng={longitude}&dist=10&back=7'
    headers = {'X-eBirdApiToken': EBIRD_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return [bird['comName'] for bird in data]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def get_bird_info(common_name):
    return common_name

def get_xeno_canto_audio(common_name):
    url = 'https://xeno-canto.org/api/2/recordings'
    query = f'{common_name}'  # Search for high-quality recordings of the common name
    response = requests.get(url, params={'query': query})
    
    if response.status_code == 200:
        data = response.json()
        if 'recordings' in data and len(data['recordings']) > 0:
            recording = random.choice(data['recordings'])
            return recording['file']
    
    return None

def get_xeno_canto_audio(common_name):
    base_url = 'https://xeno-canto.org/api/2/recordings'
    query = f'{common_name}+q:A'  # Search for high-quality recordings of the specific species code
    
    url = f'{base_url}?query={query}'
    
    response = requests.get(url)
    
    
    
    if response.status_code == 200:
        data = response.json()
        if 'recordings' in data and len(data['recordings']) > 0:
            recording = random.choice(data['recordings'])
            return recording['file']
    
    return None

def play_birdsong(common_name):
    audio_url = get_xeno_canto_audio(common_name)
    if audio_url:
        return audio_url
    else:
        return None



def play_game():
    nearby_birds = get_nearby_birds(latitude, longitude)
    if len(nearby_birds) < 4:
        return "Not enough nearby birds found."
    selected_birds = random.sample(nearby_birds, 4)
    correct_bird = random.choice(selected_birds)
    audio_url = play_birdsong(correct_bird)
    bird_names = [get_bird_info(bird) for bird in selected_birds]
    return render_template('game.html', audio_url=audio_url, bird_names=bird_names, correct_bird=correct_bird)

latitude = 44.679374
longitude = -63.330239

# Initialize pygame
#pygame.init()

#play_game(latitude, longitude)

# Hardcoded latitude and longitude for your region
latitude = 44.679374
longitude = -63.330239

@app.route('/')
def index():
    return play_game()

def play_game():
    nearby_birds = get_nearby_birds(latitude, longitude)
    if len(nearby_birds) < 4:
        return "Not enough nearby birds found."
    selected_birds = random.sample(nearby_birds, 4)
    correct_bird = random.choice(selected_birds)
    audio_url = get_xeno_canto_audio(correct_bird)
    bird_names = [get_bird_info(bird) for bird in selected_birds]
    return render_template('game.html', audio_url=audio_url, bird_names=bird_names, correct_bird=correct_bird)

@app.route('/play', methods=['POST'])
def play():
    guess = request.form['guess']
    correct_bird = request.form['correct_bird']
    if guess == correct_bird:
        result = "Congratulations! You guessed correctly."
    else:
        result = f"Sorry, the correct answer was {correct_bird}."
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)