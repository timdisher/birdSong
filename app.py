import os
import random
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
import pygame


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
        response = requests.get(audio_url)
        if response.status_code == 200:
            with open('birdsong.mp3', 'wb') as file:
                file.write(response.content)
            
            pygame.mixer.init()
            pygame.mixer.music.load('birdsong.mp3')
            pygame.mixer.music.play()
            
            input("Press Enter when you're ready to continue...")
            
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            os.remove('birdsong.mp3')
        else:
            print("Failed to download the birdsong audio.")
    else:
        print("No suitable birdsong audio found.")


def play_game(latitude, longitude):
    while True:
        nearby_birds = get_nearby_birds(latitude, longitude)
        if len(nearby_birds) < 4:
            print("Not enough nearby birds found.")
            return

        selected_birds = random.sample(nearby_birds, 4)
        correct_bird = None
        while correct_bird is None:
            correct_bird = random.choice(selected_birds)
            print("Searching for audio recordings...")
            audio_url = get_xeno_canto_audio(correct_bird)
            if audio_url is None:
                print("No suitable audio recordings found for the selected bird. Selecting a new set of birds.")
                selected_birds = random.sample(nearby_birds, 4)
                correct_bird = None

        bird_names = [get_bird_info(bird) for bird in selected_birds]

        print("Listen to the birdsong and guess the bird from the options below:")
        for i, bird in enumerate(bird_names, 1):
            print(f"{i}. {bird}")

        print("Downloading birdsong...")
        play_birdsong(correct_bird)

        guess = int(input("Enter the number of your guess: "))
        if bird_names[guess - 1] == get_bird_info(correct_bird):
            print("Congratulations! You guessed correctly.")
        else:
            print(f"Sorry, the correct answer was {get_bird_info(correct_bird)}.")

        play_again = input("Do you want to play again? (y/n): ")
        if play_again.lower() != 'y':
            break

    print("Thanks for playing!")
 #Hardcoded latitude and longitude for your region
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