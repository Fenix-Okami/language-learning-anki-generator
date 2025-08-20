from sqlalchemy import create_engine, select, MetaData, Table
import genanki
from env import DATABASE_URL  # Ensure this contains your actual database URL
import random
import re
import hashlib

# Initialize SQLAlchemy engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

def apply_text_styling(text):
    radical_color='#4193F1'
    kanji_color='#EB417D'
    vocabulary_color='#9F5FBF'

    kanji_pattern = r"<kanji>(.*?)</kanji>"
    styled_text = re.sub(kanji_pattern, f'<span style="color: {kanji_color};font-weight: bold;">\\1</span>', text)

    radical_pattern = r"<radical>(.*?)</radical>"
    styled_text = re.sub(radical_pattern, f'<span style="color: {radical_color};font-weight: bold;">\\1</span>', styled_text)

    vocabulary_pattern = r"<vocabulary>(.*?)</vocabulary>"
    styled_text = re.sub(vocabulary_pattern, f'<span style="color: {vocabulary_color};font-weight: bold;">\\1</span>', styled_text)

    reading_pattern = r"<reading>(.*?)</reading>"
    styled_text = re.sub(reading_pattern, '<b>\\1</b>', styled_text)

    return styled_text

def clean_list_items(items):
    cleaned_items = []
    for item in items:
        # Strip leading and trailing whitespace first
        clean_item = item.strip()
        # Check and remove surrounding single quotes specifically
        if clean_item.startswith("'") and clean_item.endswith("'"):
            clean_item = clean_item[1:-1]  # Remove the first and last characters
        cleaned_items.append(clean_item)
    return cleaned_items

def bolden_primary_reading(readings, primary_reading):
    # Clean the readings list from any surrounding quotes or extra spaces
    cleaned_readings = clean_list_items(readings)
    # Apply bold formatting to the primary reading
    formatted_readings = [f"<b>{reading}</b>" if reading == primary_reading else reading for reading in cleaned_readings]
    return formatted_readings

def generate_random_id():
    return random.randint(1, 2147483647)  # 2^31 - 1

def generate_guid(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:10] 

def fetch_data_from_view(view_name):
    """Fetch data from the database using the specified view."""
    table = Table(view_name, metadata, autoload_with=engine)
    query = select(table)
    with engine.connect() as connection:
        result = connection.execute(query)
        return [row._asdict() for row in result.fetchall()]

def create_radical_model():
    return genanki.Model(
        1,
        'WaniKani Radical Model',
        fields=[
            {'name': 'Radical'},
            {'name': 'Meanings'},
            {'name': 'Meaning_Mnemonic'},
            {'name': 'Level'},
            {'name': 'ID'}
        ],
        templates=[
            {
                'name': 'Radical Card',
                'qfmt': '''
                    <div class="radical"><br>{{Radical}}<br><br></div>
                ''',  # Front template
                'afmt': '''
                    {{FrontSide}}<br>
                    <span class="title"><font color="#4193F1"><b>{{Meanings}}</b></font></span><p>
                    <span class="text"><b>Meaning Mnemonic:</b><br>{{Meaning_Mnemonic}}</span><br>
                    <br>
                    <span class="text">Wanikani Level: {{Level}}</span><br>
                ''',  # Back template
            },
        ],
        css='''
            .card {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 16px;
                text-align: center;
                color: #969696;
                background-color: #202020;
            }
            .radical {
                font-family: "Meiryo", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
                font-size: 40px;
                color: #FFFFFF;
                line-height: 60px;
                background-color: #4193F1;
            }
            .title {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 26px;
            }
            .text {
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
        '''
    )

def create_radical_deck(data, model):
    deck = genanki.Deck(
        generate_random_id(),
        "WaniKani Japanese::Radicals"
    )
    for item in data:
        note = genanki.Note(
            model=model,
            fields=[
                item['radical'],
                ', '.join(clean_list_items(item['meanings'])),
                apply_text_styling(item['meaning_mnemonic']),
                str(item['level']),
                str(item['id'])
            ],
            guid=item['id']
        )
        deck.add_note(note)
    return deck

def create_kanji_model():
    my_model = genanki.Model(
        2,
        'WaniKani Kanji Model',
        fields=[
            {'name': 'Kanji'},
            {'name': 'Meanings'},
            {'name': 'Onyomi_Readings'},
            {'name': 'Kunyomi_Readings'},
            {'name': 'Meaning_Mnemonic'},
            {'name': 'Reading_Mnemonic'},
            {'name': 'Level'},
            {'name': 'ID'}
        ],
        templates=[
            {
                'name': 'Kanji Card',
                'qfmt': '''
                    <div class="kanji"><br>{{Kanji}}<br><br></div>
                ''',  # Front template
                'afmt': '''
                    {{FrontSide}}<br>
                    <span class="title"><font color="#EB417D"><b>{{Meanings}}</b></font></span><p>
                    <span class="text"><b>On'yomi: </b></span>
                    <span class="hiragana">{{Onyomi_Readings}}</span><br>
                    <span class="text"><b>Kun'yomi: </b></span>
                    <span class="hiragana">{{Kunyomi_Readings}}</span><p>
                    <span class="text"><b>Meaning Mnemonic:</b></span><br>
                    <span class="text">{{Meaning_Mnemonic}}</span><p>
                    <span class="text"><b>Reading Mnemonic:</b></span><br>
                    <span class="text">{{Reading_Mnemonic}}</span><br>
                    <br>
                    <span class="text">Wanikani Level: {{Level}}</span><br>
                ''',  # Back template
            },
        ],
        css='''
            .card {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 16px;
                text-align: center;
                color: #969696;
                background-color: #202020;
            }
            .kanji {
                font-family: "Meiryo", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
                font-size: 70px;
                color: #FFFFFF;
                line-height: 100px;
                background-color: #EB417D;
            }
            .hiragana {
                font-family: "Meiryo", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
                font-size: 20px;
            }
            .title {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 26px;
            }
            .text {
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
        '''
    )
    return my_model

def create_kanji_deck(data, model):
    deck = genanki.Deck(
        generate_random_id(),
        "WaniKani Japanese::Kanji"
    )
    for item in data:

        formatted_onyomi = bolden_primary_reading(item['onyomi_readings'], item['primary_reading'])
        formatted_kunyomi = bolden_primary_reading(item['kunyomi_readings'], item['primary_reading'])

        note = genanki.Note(
            model=model,
            fields=[
                item['kanji'],
                ', '.join(clean_list_items(item['meanings'])),
                ', '.join(formatted_onyomi),
                ', '.join(formatted_kunyomi),
                apply_text_styling(item['meaning_mnemonic']),
                apply_text_styling(item['reading_mnemonic']),
                str(item['level']),
                str(item['id'])
            ],
            guid=item['id']
        )
        deck.add_note(note)
    return deck

def create_vocab_model():
    return genanki.Model(
        3,
        'WaniKani Vocabulary Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Meanings'},
            {'name': 'Readings'},
            {'name': 'Auxiliary_Meanings'},
            {'name': 'Meaning_Mnemonic'},
            {'name': 'Reading_Mnemonic'},
            {'name': 'Level'},
            {'name': 'ID'}
        ],
        templates=[
            {
                'name': 'Vocabulary Card',
                'qfmt': '''
                    <div class="word"><br>{{Word}}<br><br></div>
                ''',  # Front template
                'afmt': '''
                    {{FrontSide}}<br>
                    <span class="title"><font color="#9F5FBF"><b>{{Meanings}}</b></font></span><p>
                    <span class="title"><b>{{Readings}}</b></span><br>
                    <span class="text"><b>Auxiliary Meanings:</b> {{Auxiliary_Meanings}}</span><p>
                    <span class="text"><b>Meaning Mnemonic:</b><br>{{Meaning_Mnemonic}}</span><p>
                    <span class="text"><b>Reading Mnemonic:</b><br>{{Reading_Mnemonic}}</span><br>
                    <br>
                    <span class="text">Wanikani Level: <b>{{Level}}</b></span><br>
                ''',  # Back template
            },
        ],
        css='''
            .card {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 16px;
                text-align: center;
                color: #969696;
                background-color: #202020;
            }
            .word {
                font-family: "Meiryo", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
                font-size: 40px;
                color: #FFFFFF;
                line-height: 60px;
                background-color: #833EA8;
            }
            .title {
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 26px;
            }
            .text {
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
        '''
    )

def create_vocab_deck(data, model):
    deck = genanki.Deck(
        generate_random_id(),
        "WaniKani Japanese::Vocabulary"
    )
    for item in data:
        note = genanki.Note(
            model=model,
            fields=[
                item['word'],
                ', '.join(clean_list_items(item['meanings'])),
                ', '.join(clean_list_items(item['readings'])),
                ', '.join(clean_list_items(item['auxiliary_meanings'])),
                apply_text_styling(item['meaning_mnemonic']),
                apply_text_styling(item['reading_mnemonic']),
                str(item['level']),
                str(item['id'])
            ],
            guid=item['id']
        )
        deck.add_note(note)
    return deck

def save_deck(deck, filename):
    genanki.Package(deck).write_to_file(filename)

radical_model = create_radical_model()
radical_data = fetch_data_from_view('wanikani_radicals')  # Assuming a view exists similar to kanji and vocabulary
radical_deck = create_radical_deck(radical_data, radical_model)
save_deck(radical_deck, 'ankidecks/WaniKani_Radical_Deck.apkg')
print("Radical deck created and saved successfully.")

kanji_model = create_kanji_model()
kanji_data = fetch_data_from_view('wanikani_kanji')
kanji_deck = create_kanji_deck(kanji_data,kanji_model)
save_deck(kanji_deck, 'ankidecks/WaniKani_Kanji_Deck.apkg')
print("Kanji deck created and saved successfully.")

vocab_model = create_vocab_model()
vocab_data = fetch_data_from_view('wanikani_vocab')  # Assuming you have a similar view for vocabulary
vocab_deck = create_vocab_deck(vocab_data, vocab_model)
save_deck(vocab_deck, 'ankidecks/WaniKani_Vocabulary_Deck.apkg')
print("Vocab deck created and saved successfully.")

package = genanki.Package()
package.decks = [kanji_deck, vocab_deck, radical_deck]

# Save to a single .apkg file
package.write_to_file('ankidecks/WaniKani_Complete_Deck.apkg')

print("All decks have been bundled into one .apkg file successfully.")
