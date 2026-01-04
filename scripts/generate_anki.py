#!/usr/bin/env python3
"""
Generate Anki decks from Spanish vocabulary YAML files.

Creates the following decks (both ordered and randomized versions):
1. Words & Verbs deck (common.yaml + verbs.yaml)
2. Complete deck (common.yaml + verbs.yaml + sentences.yaml + extras.yaml)
3. Sentences Only deck (sentences.yaml + extras.yaml)

Each deck includes Spanish→English and English→Spanish cards with
expandable extra info showing example sentences and conjugations.
"""

import yaml
import genanki
import random
import html
import argparse
from pathlib import Path
from collections import defaultdict


# Generate consistent model and deck IDs
WORD_MODEL_ID = 1607392319
VERB_MODEL_ID = 1607392320
SENTENCE_MODEL_ID = 1607392321
WORDS_VERBS_DECK_ID = 2059400110
COMPLETE_DECK_ID = 2059400111


def create_word_model():
    """Create Anki model for common words."""
    return genanki.Model(
        WORD_MODEL_ID,
        'Spanish Word',
        fields=[
            {'name': 'Spanish'},
            {'name': 'English'},
            {'name': 'Form'},
            {'name': 'ExampleSentences'},
        ],
        templates=[
            {
                'name': 'Spanish → English',
                'qfmt': '''
                    <div class="card spanish-front">
                        <div class="word">{{Spanish}}</div>
                        <div class="form">({{Form}})</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card">
                        <div class="word">{{Spanish}}</div>
                        <div class="form">({{Form}})</div>
                        <hr>
                        <div class="answer">{{English}}</div>
                        {{#ExampleSentences}}
                        <details class="extra">
                            <summary>Example Sentences</summary>
                            {{ExampleSentences}}
                        </details>
                        {{/ExampleSentences}}
                    </div>
                ''',
            },
            {
                'name': 'English → Spanish',
                'qfmt': '''
                    <div class="card english-front">
                        <div class="word">{{English}}</div>
                        <div class="form">({{Form}})</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card">
                        <div class="word">{{English}}</div>
                        <div class="form">({{Form}})</div>
                        <hr>
                        <div class="answer">{{Spanish}}</div>
                        {{#ExampleSentences}}
                        <details class="extra">
                            <summary>Example Sentences</summary>
                            {{ExampleSentences}}
                        </details>
                        {{/ExampleSentences}}
                    </div>
                ''',
            },
        ],
        css='''
            .card {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: #333;
                background-color: #fafafa;
                padding: 20px;
            }
            .word {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .form {
                font-size: 14px;
                color: #666;
                font-style: italic;
            }
            .answer {
                font-size: 28px;
                color: #2e7d32;
                margin: 15px 0;
            }
            details.extra {
                text-align: left;
                margin-top: 20px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 8px;
            }
            details.extra summary {
                cursor: pointer;
                font-weight: bold;
                color: #1976d2;
            }
            .sentence {
                margin: 10px 0;
                padding: 8px;
                background: white;
                border-left: 3px solid #1976d2;
            }
            .sentence-spanish {
                font-weight: bold;
            }
            .sentence-english {
                color: #666;
                font-style: italic;
            }
        ''',
    )


def create_verb_model():
    """Create Anki model for verbs with conjugations."""
    return genanki.Model(
        VERB_MODEL_ID,
        'Spanish Verb',
        fields=[
            {'name': 'Spanish'},
            {'name': 'English'},
            {'name': 'Conjugations'},
            {'name': 'ExampleSentences'},
        ],
        templates=[
            {
                'name': 'Spanish → English',
                'qfmt': '''
                    <div class="card spanish-front">
                        <div class="word">{{Spanish}}</div>
                        <div class="form">(verb)</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card">
                        <div class="word">{{Spanish}}</div>
                        <div class="form">(verb)</div>
                        <hr>
                        <div class="answer">{{English}}</div>
                        <details class="extra conjugations">
                            <summary>Conjugations</summary>
                            {{Conjugations}}
                        </details>
                        {{#ExampleSentences}}
                        <details class="extra">
                            <summary>Example Sentences</summary>
                            {{ExampleSentences}}
                        </details>
                        {{/ExampleSentences}}
                    </div>
                ''',
            },
            {
                'name': 'English → Spanish',
                'qfmt': '''
                    <div class="card english-front">
                        <div class="word">{{English}}</div>
                        <div class="form">(verb)</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card">
                        <div class="word">{{English}}</div>
                        <div class="form">(verb)</div>
                        <hr>
                        <div class="answer">{{Spanish}}</div>
                        <details class="extra conjugations">
                            <summary>Conjugations</summary>
                            {{Conjugations}}
                        </details>
                        {{#ExampleSentences}}
                        <details class="extra">
                            <summary>Example Sentences</summary>
                            {{ExampleSentences}}
                        </details>
                        {{/ExampleSentences}}
                    </div>
                ''',
            },
        ],
        css='''
            .card {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: #333;
                background-color: #fafafa;
                padding: 20px;
            }
            .word {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .form {
                font-size: 14px;
                color: #666;
                font-style: italic;
            }
            .answer {
                font-size: 28px;
                color: #2e7d32;
                margin: 15px 0;
            }
            details.extra {
                text-align: left;
                margin-top: 20px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 8px;
            }
            details.extra summary {
                cursor: pointer;
                font-weight: bold;
                color: #1976d2;
            }
            .conj-table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .conj-table th {
                background: #1976d2;
                color: white;
                padding: 8px;
                text-align: left;
            }
            .conj-table td {
                padding: 6px 8px;
                border-bottom: 1px solid #ddd;
            }
            .conj-table tr:nth-child(even) {
                background: #f9f9f9;
            }
            .tense-header {
                background: #e3f2fd;
                font-weight: bold;
                padding: 8px;
                margin-top: 10px;
                border-radius: 4px;
            }
            .sentence {
                margin: 10px 0;
                padding: 8px;
                background: white;
                border-left: 3px solid #1976d2;
            }
            .sentence-spanish {
                font-weight: bold;
            }
            .sentence-english {
                color: #666;
                font-style: italic;
            }
        ''',
    )


def create_sentence_model():
    """Create Anki model for sentences."""
    return genanki.Model(
        SENTENCE_MODEL_ID,
        'Spanish Sentence',
        fields=[
            {'name': 'Spanish'},
            {'name': 'English'},
            {'name': 'VerbInfo'},
            {'name': 'ExtraInfo'},
        ],
        templates=[
            {
                'name': 'Spanish → English',
                'qfmt': '''
                    <div class="card spanish-front sentence-card">
                        <div class="sentence-text">{{Spanish}}</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card sentence-card">
                        <div class="sentence-text spanish">{{Spanish}}</div>
                        <hr>
                        <div class="sentence-text answer">{{English}}</div>
                        {{#VerbInfo}}
                        <details class="extra">
                            <summary>Verb Conjugations</summary>
                            {{VerbInfo}}
                        </details>
                        {{/VerbInfo}}
                        {{#ExtraInfo}}
                        <details class="extra">
                            <summary>Grammar Notes</summary>
                            {{ExtraInfo}}
                        </details>
                        {{/ExtraInfo}}
                    </div>
                ''',
            },
            {
                'name': 'English → Spanish',
                'qfmt': '''
                    <div class="card english-front sentence-card">
                        <div class="sentence-text">{{English}}</div>
                    </div>
                ''',
                'afmt': '''
                    <div class="card sentence-card">
                        <div class="sentence-text english">{{English}}</div>
                        <hr>
                        <div class="sentence-text answer">{{Spanish}}</div>
                        {{#VerbInfo}}
                        <details class="extra">
                            <summary>Verb Conjugations</summary>
                            {{VerbInfo}}
                        </details>
                        {{/VerbInfo}}
                        {{#ExtraInfo}}
                        <details class="extra">
                            <summary>Grammar Notes</summary>
                            {{ExtraInfo}}
                        </details>
                        {{/ExtraInfo}}
                    </div>
                ''',
            },
        ],
        css='''
            .card {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: #333;
                background-color: #fafafa;
                padding: 20px;
            }
            .sentence-card .sentence-text {
                font-size: 24px;
                line-height: 1.5;
                margin: 15px 0;
            }
            .sentence-card .answer {
                color: #2e7d32;
            }
            details.extra {
                text-align: left;
                margin-top: 20px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 8px;
            }
            details.extra summary {
                cursor: pointer;
                font-weight: bold;
                color: #1976d2;
            }
            .verb-header {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                margin-bottom: 10px;
            }
            .conj-table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .conj-table th {
                background: #1976d2;
                color: white;
                padding: 8px;
                text-align: left;
            }
            .conj-table td {
                padding: 6px 8px;
                border-bottom: 1px solid #ddd;
            }
            .conj-table tr:nth-child(even) {
                background: #f9f9f9;
            }
            .tense-header {
                background: #e3f2fd;
                font-weight: bold;
                padding: 8px;
                margin-top: 10px;
                border-radius: 4px;
            }
            .extra-info-item {
                margin: 8px 0;
                padding: 8px;
                background: white;
                border-left: 3px solid #ff9800;
            }
            .extra-spanish {
                font-weight: bold;
            }
            .extra-english {
                color: #666;
                font-style: italic;
            }
        ''',
    )


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def format_english(english_list: list) -> str:
    """Format English translations as a string."""
    if isinstance(english_list, list):
        return ', '.join(english_list)
    return str(english_list)


def format_conjugations_html(conjugations: dict) -> str:
    """Format verb conjugations as HTML table."""
    if not conjugations:
        return ''

    pronouns = ['yo', 'tú', 'él', 'nosotros', 'vosotros', 'ellos']
    tense_names = {
        'present': 'Present',
        'preterite': 'Preterite',
        'imperfect': 'Imperfect',
        'future': 'Future'
    }

    html_parts = []

    for tense, forms in conjugations.items():
        if tense not in tense_names:
            continue
        html_parts.append(f'<div class="tense-header">{tense_names[tense]}</div>')
        html_parts.append('<table class="conj-table">')
        html_parts.append('<tr><th>Pronoun</th><th>Conjugation</th></tr>')
        for pronoun in pronouns:
            if pronoun in forms:
                html_parts.append(f'<tr><td>{pronoun}</td><td>{html.escape(forms[pronoun])}</td></tr>')
        html_parts.append('</table>')

    return ''.join(html_parts)


def format_sentences_html(sentences: list) -> str:
    """Format example sentences as HTML."""
    if not sentences:
        return ''

    html_parts = []
    for sent in sentences[:5]:  # Limit to 5 sentences
        spanish = html.escape(sent.get('spanish', ''))
        english = html.escape(sent.get('english', ''))
        html_parts.append(f'''
            <div class="sentence">
                <div class="sentence-spanish">{spanish}</div>
                <div class="sentence-english">{english}</div>
            </div>
        ''')

    return ''.join(html_parts)


def format_extra_infos_html(extra_infos: list) -> str:
    """Format extra_infos from sentences as HTML."""
    if not extra_infos:
        return ''

    html_parts = []
    for info in extra_infos:
        spanish = html.escape(info.get('spanish', ''))
        english = html.escape(info.get('english', ''))
        html_parts.append(f'''
            <div class="extra-info-item">
                <span class="extra-spanish">{spanish}</span> -
                <span class="extra-english">{english}</span>
            </div>
        ''')

    return ''.join(html_parts)


def build_sentence_index(sentences: list) -> tuple[dict, dict]:
    """Build indexes mapping words and verbs to their sentences."""
    word_sentences = defaultdict(list)
    verb_sentences = defaultdict(list)

    for sent in sentences:
        word_id = sent.get('word', '')
        verb_id = sent.get('verb', '')

        sentence_data = {
            'spanish': sent.get('spanish', ''),
            'english': sent.get('english', ''),
        }

        if word_id:
            word_sentences[word_id].append(sentence_data)
        if verb_id:
            verb_sentences[verb_id].append(sentence_data)

    return word_sentences, verb_sentences


def create_word_notes(common: dict, word_sentences: dict, model: genanki.Model) -> list:
    """Create Anki notes for common words. Returns list of field tuples for creating notes."""
    notes_data = []

    for word_id, data in common.items():
        spanish = str(data.get('spanish', '') or '')
        english = format_english(data.get('english', []))
        form = str(data.get('form', '') or '')

        # Get example sentences for this word
        sentences_html = format_sentences_html(word_sentences.get(word_id, [])) or ''

        notes_data.append({
            'fields': [spanish, english, form, sentences_html],
            'tags': ['word', form] if form else ['word'],
        })

    return notes_data


def create_verb_notes(verbs: dict, verb_sentences: dict, model: genanki.Model) -> list:
    """Create Anki notes for verbs. Returns list of field tuples for creating notes."""
    notes_data = []

    for verb_id, data in verbs.items():
        spanish = str(data.get('spanish', '') or '')
        english = format_english(data.get('english', []))
        conjugations = data.get('conjugations', {}) or {}

        # Format conjugations
        conjugations_html = format_conjugations_html(conjugations) or ''

        # Get example sentences for this verb
        sentences_html = format_sentences_html(verb_sentences.get(verb_id, [])) or ''

        notes_data.append({
            'fields': [spanish, english, conjugations_html, sentences_html],
            'tags': ['verb'],
        })

    return notes_data


def create_sentence_notes(sentences: list, verbs: dict, model: genanki.Model) -> list:
    """Create Anki notes for sentences. Returns list of field tuples for creating notes."""
    notes_data = []

    for sent in sentences:
        spanish = str(sent.get('spanish', '') or '')
        english = str(sent.get('english', '') or '')
        verb_id = sent.get('verb', '') or ''
        extra_infos = sent.get('extra_infos', []) or []

        # Skip placeholder entries
        if '<placeholder>' in spanish or '<placeholder>' in english:
            continue

        # Get verb info
        verb_info_html = ''
        if verb_id and verb_id in verbs:
            verb_data = verbs[verb_id]
            verb_spanish = str(verb_data.get('spanish', '') or '')
            verb_english = format_english(verb_data.get('english', []))
            conjugations = verb_data.get('conjugations', {}) or {}

            verb_info_html = f'<div class="verb-header">{html.escape(verb_spanish)} - {html.escape(verb_english)}</div>'
            verb_info_html += format_conjugations_html(conjugations) or ''

        # Format extra infos
        extra_info_html = format_extra_infos_html(extra_infos) if extra_infos else ''

        notes_data.append({
            'fields': [spanish, english, verb_info_html, extra_info_html],
            'tags': ['sentence'],
        })

    return notes_data


def add_notes_to_deck(deck: genanki.Deck, notes_data: list, model: genanki.Model):
    """Create fresh note instances and add them to a deck."""
    for data in notes_data:
        note = genanki.Note(
            model=model,
            fields=data['fields'],
            tags=data['tags'],
        )
        deck.add_note(note)


def main():
    """Main function to generate Anki decks."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate Anki decks from Spanish vocabulary YAML files.')
    parser.add_argument('--seed', '-s', type=int, default=None,
                        help='Random seed for reproducible randomization')
    args = parser.parse_args()

    # Paths
    words_dir = Path(__file__).parent.parent / 'words'
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Load data
    print("Loading YAML files...")
    common = load_yaml(words_dir / 'common.yaml')
    verbs = load_yaml(words_dir / 'verbs.yaml')
    sentences_data = load_yaml(words_dir / 'sentences.yaml')
    extras_data = load_yaml(words_dir / 'extras.yaml')

    # Extract sentences and extras lists
    sentences = sentences_data.get('sentences', [])
    extras = extras_data.get('extras', [])

    # Remove comment keys from common and verbs
    common = {k: v for k, v in common.items() if isinstance(v, dict)}
    verbs = {k: v for k, v in verbs.items() if isinstance(v, dict)}

    print(f"Loaded {len(common)} words, {len(verbs)} verbs, {len(sentences)} sentences, {len(extras)} extras")

    # Combine sentences and extras for processing
    all_sentences = sentences + extras

    # Build sentence indexes
    word_sentences, verb_sentences = build_sentence_index(all_sentences)

    # Create models
    word_model = create_word_model()
    verb_model = create_verb_model()
    sentence_model = create_sentence_model()

    # Create notes data (not actual note objects yet)
    print("Creating notes data...")
    word_notes_data = create_word_notes(common, word_sentences, word_model)
    verb_notes_data = create_verb_notes(verbs, verb_sentences, verb_model)
    sentence_notes_data = create_sentence_notes(all_sentences, verbs, sentence_model)

    print(f"Created {len(word_notes_data)} word notes, {len(verb_notes_data)} verb notes, {len(sentence_notes_data)} sentence notes")

    # --- Create ordered decks ---
    print("Creating ordered decks...")

    # Words & Verbs deck (ordered)
    words_verbs_deck = genanki.Deck(
        WORDS_VERBS_DECK_ID,
        'Spanish - Words & Verbs'
    )
    add_notes_to_deck(words_verbs_deck, word_notes_data, word_model)
    add_notes_to_deck(words_verbs_deck, verb_notes_data, verb_model)

    # Complete deck (ordered)
    complete_deck = genanki.Deck(
        COMPLETE_DECK_ID,
        'Spanish - Complete (Words, Verbs, Sentences)'
    )
    add_notes_to_deck(complete_deck, word_notes_data, word_model)
    add_notes_to_deck(complete_deck, verb_notes_data, verb_model)
    add_notes_to_deck(complete_deck, sentence_notes_data, sentence_model)

    # Sentences only deck (ordered)
    SENTENCES_DECK_ID = COMPLETE_DECK_ID + 10
    sentences_deck = genanki.Deck(
        SENTENCES_DECK_ID,
        'Spanish - Sentences Only'
    )
    add_notes_to_deck(sentences_deck, sentence_notes_data, sentence_model)

    # --- Create randomized decks ---
    print("Creating randomized decks...")

    # Use different deck IDs for random versions
    WORDS_VERBS_RANDOM_DECK_ID = WORDS_VERBS_DECK_ID + 1
    COMPLETE_RANDOM_DECK_ID = COMPLETE_DECK_ID + 1
    SENTENCES_RANDOM_DECK_ID = SENTENCES_DECK_ID + 1

    # Words & Verbs deck (random)
    words_verbs_random_deck = genanki.Deck(
        WORDS_VERBS_RANDOM_DECK_ID,
        'Spanish - Words & Verbs (Random)'
    )
    words_verbs_combined = [(data, word_model) for data in word_notes_data] + \
                           [(data, verb_model) for data in verb_notes_data]
    random.shuffle(words_verbs_combined)
    for data, model in words_verbs_combined:
        note = genanki.Note(model=model, fields=data['fields'], tags=data['tags'])
        words_verbs_random_deck.add_note(note)

    # Complete deck (random)
    complete_random_deck = genanki.Deck(
        COMPLETE_RANDOM_DECK_ID,
        'Spanish - Complete (Random)'
    )
    complete_combined = [(data, word_model) for data in word_notes_data] + \
                        [(data, verb_model) for data in verb_notes_data] + \
                        [(data, sentence_model) for data in sentence_notes_data]
    random.shuffle(complete_combined)
    for data, model in complete_combined:
        note = genanki.Note(model=model, fields=data['fields'], tags=data['tags'])
        complete_random_deck.add_note(note)

    # Sentences only deck (random)
    sentences_random_deck = genanki.Deck(
        SENTENCES_RANDOM_DECK_ID,
        'Spanish - Sentences Only (Random)'
    )
    sentence_notes_shuffled = sentence_notes_data.copy()
    random.shuffle(sentence_notes_shuffled)
    add_notes_to_deck(sentences_random_deck, sentence_notes_shuffled, sentence_model)

    # Save all decks
    print("Saving decks...")

    words_verbs_package = genanki.Package(words_verbs_deck)
    words_verbs_package.write_to_file(output_dir / 'spanish_words_verbs.apkg')

    complete_package = genanki.Package(complete_deck)
    complete_package.write_to_file(output_dir / 'spanish_complete.apkg')

    words_verbs_random_package = genanki.Package(words_verbs_random_deck)
    words_verbs_random_package.write_to_file(output_dir / 'spanish_words_verbs_random.apkg')

    complete_random_package = genanki.Package(complete_random_deck)
    complete_random_package.write_to_file(output_dir / 'spanish_complete_random.apkg')

    sentences_package = genanki.Package(sentences_deck)
    sentences_package.write_to_file(output_dir / 'spanish_sentences.apkg')

    sentences_random_package = genanki.Package(sentences_random_deck)
    sentences_random_package.write_to_file(output_dir / 'spanish_sentences_random.apkg')

    words_verbs_count = len(word_notes_data) + len(verb_notes_data)
    complete_count = words_verbs_count + len(sentence_notes_data)
    sentences_count = len(sentence_notes_data)

    print(f"\nDecks saved to {output_dir}:")
    print(f"  - spanish_words_verbs.apkg ({words_verbs_count} notes, {words_verbs_count * 2} cards)")
    print(f"  - spanish_words_verbs_random.apkg ({words_verbs_count} notes, {words_verbs_count * 2} cards)")
    print(f"  - spanish_complete.apkg ({complete_count} notes, {complete_count * 2} cards)")
    print(f"  - spanish_complete_random.apkg ({complete_count} notes, {complete_count * 2} cards)")
    print(f"  - spanish_sentences.apkg ({sentences_count} notes, {sentences_count * 2} cards)")
    print(f"  - spanish_sentences_random.apkg ({sentences_count} notes, {sentences_count * 2} cards)")


if __name__ == '__main__':
    main()
