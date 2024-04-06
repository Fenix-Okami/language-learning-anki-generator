import csv
from pathlib import Path
from openai import OpenAI
from env import OPENAI_KEY

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=OPENAI_KEY)

# Define the base directory for audio files relative to this script
audio_dir = Path(__file__).parent / 'data/anki_decks'
audio_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

def generate_audio(text, index):
    speech_file_path = audio_dir / f"speech_{index}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Make sure to choose a voice that supports Japanese if available
        input=text
    )
    response.stream_to_file(str(speech_file_path))
    return speech_file_path

# Function to create an Anki card
def create_anki_card(japanese_text, english_text, index):
    audio_file_path = generate_audio(japanese_text, index=index)
    return [japanese_text, english_text, f'[sound:{audio_file_path.name}]']

# Input CSV file path
input_csv_path = Path(__file__).parent / 'test.csv'

# Output Anki file path within the same 'data/anki_decks' directory
anki_file_path = audio_dir / 'anki_japanese_flashcards.tsv'

# Read the CSV file and create Anki cards
with input_csv_path.open('r', encoding='utf-8') as infile, anki_file_path.open('w', newline='', encoding='utf-8') as outfile:
    csv_reader = csv.reader(infile)
    writer = csv.writer(outfile, delimiter='\t')
    
    for index, row in enumerate(csv_reader, start=1):
        english_text, japanese_text = row
        card = create_anki_card(japanese_text, english_text, index)
        writer.writerow(card)

print(f"Anki flashcards created successfully in {anki_file_path}.")