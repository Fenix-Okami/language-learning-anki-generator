from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import genanki
from env import DATABASE_URL
import random
import re
import hashlib
import os
from typing import List, Dict, Any

def apply_text_styling(text: str) -> str:
    """
    Apply HTML styling to WaniKani markup tags in text.
    
    Args:
        text: Text containing WaniKani markup tags
        
    Returns:
        HTML-styled text
    """
    radical_color = '#4193F1'
    kanji_color = '#EB417D'
    vocabulary_color = '#9F5FBF'

    kanji_pattern = r"<kanji>(.*?)</kanji>"
    styled_text = re.sub(kanji_pattern, f'<span style="color: {kanji_color};font-weight: bold;">\\1</span>', text)

    radical_pattern = r"<radical>(.*?)</radical>"
    styled_text = re.sub(radical_pattern, f'<span style="color: {radical_color};font-weight: bold;">\\1</span>', styled_text)

    vocabulary_pattern = r"<vocabulary>(.*?)</vocabulary>"
    styled_text = re.sub(vocabulary_pattern, f'<span style="color: {vocabulary_color};font-weight: bold;">\\1</span>', styled_text)

    reading_pattern = r"<reading>(.*?)</reading>"
    styled_text = re.sub(reading_pattern, '<b>\\1</b>', styled_text)

    return styled_text


def clean_list_items(items: List[str]) -> List[str]:
    """
    Clean list items by removing extra whitespace and surrounding quotes.
    
    Args:
        items: List of string items to clean
        
    Returns:
        List of cleaned strings
    """
    cleaned_items = []
    for item in items:
        clean_item = item.strip()
        # Remove surrounding single quotes if present
        if clean_item.startswith("'") and clean_item.endswith("'"):
            clean_item = clean_item[1:-1]
        cleaned_items.append(clean_item)
    return cleaned_items


def bolden_primary_reading(readings: List[str], primary_reading: str) -> List[str]:
    """
    Apply bold formatting to the primary reading in a list of readings.
    
    Args:
        readings: List of reading strings
        primary_reading: The reading to bold
        
    Returns:
        List with primary reading bolded
    """
    cleaned_readings = clean_list_items(readings)
    formatted_readings = [
        f"<b>{reading}</b>" if reading == primary_reading else reading 
        for reading in cleaned_readings
    ]
    return formatted_readings


def generate_random_id() -> int:
    """Generate a random ID for Anki decks."""
    return random.randint(1, 2147483647)  # 2^31 - 1


def generate_guid(text: str) -> str:
    """Generate a GUID from text using SHA256."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:10]


def create_database_engine(database_url: str) -> Engine:
    """
    Creates and validates a SQLAlchemy database engine.
    
    Args:
        database_url: PostgreSQL database connection URL
        
    Returns:
        SQLAlchemy Engine instance
        
    Raises:
        ValueError: If database URL is invalid
        SQLAlchemyError: If database connection fails
    """
    try:
        if not database_url:
            raise ValueError("Database URL is required")
        
        engine = create_engine(database_url)
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(select(1))
        
        return engine
        
    except SQLAlchemyError as e:
        print(f"✗ Database connection failed: {e}")
        raise


def fetch_data_from_view(view_name: str, engine: Engine) -> List[Dict[str, Any]]:
    """
    Fetch data from a database view.
    
    Args:
        view_name: Name of the database view to query
        engine: SQLAlchemy engine instance
        
    Returns:
        List of dictionaries containing view data
        
    Raises:
        SQLAlchemyError: If database query fails
    """
    try:
        metadata = MetaData()
        table = Table(view_name, metadata, autoload_with=engine)
        query = select(table)
        
        with engine.connect() as connection:
            result = connection.execute(query)
            data = [row._asdict() for row in result.fetchall()]
            
        print(f"  ✓ Fetched {len(data)} records from view '{view_name}'")
        return data
        
    except SQLAlchemyError as e:
        print(f"✗ Error fetching data from view '{view_name}': {e}")
        raise

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

def save_deck(deck: genanki.Deck, filename: str) -> None:
    """
    Save an Anki deck to a .apkg file.
    
    Args:
        deck: Genanki Deck instance to save
        filename: Output filename (should end with .apkg)
        
    Raises:
        IOError: If there's an error writing the file
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        genanki.Package(deck).write_to_file(filename)
        
        # Get file size
        file_size_kb = os.path.getsize(filename) / 1024
        print(f"  ✓ Saved deck to {filename} ({file_size_kb:.1f} KB)")
        
    except IOError as e:
        print(f"✗ Error saving deck to {filename}: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error saving deck: {e}")
        raise

def generate_all_decks(engine: Engine, output_dir: str = 'ankidecks') -> Dict[str, str]:
    """
    Generate all WaniKani Anki decks from database views.
    
    Args:
        engine: SQLAlchemy engine instance
        output_dir: Directory to save deck files
        
    Returns:
        Dictionary mapping deck type to output filepath
        
    Raises:
        SQLAlchemyError: If database queries fail
        IOError: If file writing fails
    """
    try:
        deck_files = {}
        
        # Generate Radical Deck
        print("\nGenerating Radical deck...")
        radical_model = create_radical_model()
        radical_data = fetch_data_from_view('wanikani_radicals', engine)
        radical_deck = create_radical_deck(radical_data, radical_model)
        radical_file = os.path.join(output_dir, 'WaniKani_Radical_Deck.apkg')
        save_deck(radical_deck, radical_file)
        deck_files['radical'] = radical_file
        
        # Generate Kanji Deck
        print("\nGenerating Kanji deck...")
        kanji_model = create_kanji_model()
        kanji_data = fetch_data_from_view('wanikani_kanji', engine)
        kanji_deck = create_kanji_deck(kanji_data, kanji_model)
        kanji_file = os.path.join(output_dir, 'WaniKani_Kanji_Deck.apkg')
        save_deck(kanji_deck, kanji_file)
        deck_files['kanji'] = kanji_file
        
        # Generate Vocabulary Deck
        print("\nGenerating Vocabulary deck...")
        vocab_model = create_vocab_model()
        vocab_data = fetch_data_from_view('wanikani_vocab', engine)
        vocab_deck = create_vocab_deck(vocab_data, vocab_model)
        vocab_file = os.path.join(output_dir, 'WaniKani_Vocabulary_Deck.apkg')
        save_deck(vocab_deck, vocab_file)
        deck_files['vocabulary'] = vocab_file
        
        # Generate Complete Bundle
        print("\nGenerating complete bundle...")
        package = genanki.Package()
        package.decks = [radical_deck, kanji_deck, vocab_deck]
        complete_file = os.path.join(output_dir, 'WaniKani_Complete_Deck.apkg')
        
        os.makedirs(output_dir, exist_ok=True)
        package.write_to_file(complete_file)
        
        file_size_kb = os.path.getsize(complete_file) / 1024
        print(f"  ✓ Saved complete bundle to {complete_file} ({file_size_kb:.1f} KB)")
        deck_files['complete'] = complete_file
        
        return deck_files
        
    except SQLAlchemyError as e:
        print(f"✗ Database error: {e}")
        raise
    except IOError as e:
        print(f"✗ File I/O error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error generating decks: {e}")
        raise


# Main execution
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("WaniKani Anki Deck Generator")
        print("=" * 60)
        
        # Create database engine
        engine = create_database_engine(DATABASE_URL)
        print("✓ Database connection established")
        
        # Generate all decks
        deck_files = generate_all_decks(engine)
        
        print("\n" + "=" * 60)
        print("✓ All decks generated successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        for deck_type, filepath in deck_files.items():
            print(f"  • {deck_type.capitalize()}: {filepath}")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Deck generation failed: {e}")
        print("=" * 60)
        exit(1)
