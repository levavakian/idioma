#!/usr/bin/env python3
"""
Script to generate sentences.yaml with word/verb combinations for sentence practice.

This script creates entries that pair words from common.yaml with verbs from verbs.yaml,
ensuring each word and each verb+tense combination is used at least once.
"""

import yaml
import random
from pathlib import Path
from itertools import cycle

# =============================================================================
# SPANISH TENSES, MOODS, AND CONSTRUCTIONS
# =============================================================================

# Basic tenses available in verbs.yaml conjugations
BASIC_TENSES = [
    "present",
    "preterite",
    "imperfect",
    "future",
]

# Additional elements - more complex tenses, moods, and constructions
# These will be randomly added to sentences for more advanced practice
ADDITIONAL_ELEMENTS = [
    # Subjunctive moods
    "present_subjunctive",      # que yo hable
    "imperfect_subjunctive",    # que yo hablara/hablase

    # Conditional
    "conditional",              # yo hablaría

    # Imperative
    "imperative_affirmative",   # ¡habla!
    "imperative_negative",      # ¡no hables!

    # Perfect tenses (haber + past participle)
    "present_perfect",          # he hablado
    "past_perfect",             # había hablado
    "future_perfect",           # habré hablado
    "conditional_perfect",      # habría hablado
    "present_perfect_subjunctive",  # que haya hablado
    "past_perfect_subjunctive",     # que hubiera hablado

    # Progressive tenses (estar + gerund)
    "present_progressive",      # estoy hablando
    "past_progressive",         # estaba hablando

    # Modal constructions
    "deber_infinitive",         # debo hablar (obligation)
    "poder_infinitive",         # puedo hablar (ability)
    "querer_infinitive",        # quiero hablar (desire)
    "tener_que_infinitive",     # tengo que hablar (necessity)
    "necesitar_infinitive",     # necesito hablar (need)

    # Near future
    "ir_a_infinitive",          # voy a hablar

    # Passive constructions
    "passive_ser",              # es hablado
    "passive_estar",            # está hablado (resultant state)

    # Reflexive emphasis
    "reflexive",                # hablarse
]

# =============================================================================
# HELPER VERB CONJUGATIONS FOR ADDITIONAL ELEMENTS
# =============================================================================
# These provide the conjugations needed when using compound tenses or modal verbs.
# Each entry maps an additional element to a list of {spanish, english} pairs.

HELPER_CONJUGATIONS = {
    # Perfect tenses use "haber"
    "present_perfect": [
        {"spanish": "he", "english": "I have"},
        {"spanish": "has", "english": "you have"},
        {"spanish": "ha", "english": "he/she has"},
        {"spanish": "hemos", "english": "we have"},
        {"spanish": "habéis", "english": "you all have"},
        {"spanish": "han", "english": "they have"},
    ],
    "past_perfect": [
        {"spanish": "había", "english": "I had"},
        {"spanish": "habías", "english": "you had"},
        {"spanish": "había", "english": "he/she had"},
        {"spanish": "habíamos", "english": "we had"},
        {"spanish": "habíais", "english": "you all had"},
        {"spanish": "habían", "english": "they had"},
    ],
    "future_perfect": [
        {"spanish": "habré", "english": "I will have"},
        {"spanish": "habrás", "english": "you will have"},
        {"spanish": "habrá", "english": "he/she will have"},
        {"spanish": "habremos", "english": "we will have"},
        {"spanish": "habréis", "english": "you all will have"},
        {"spanish": "habrán", "english": "they will have"},
    ],
    "conditional_perfect": [
        {"spanish": "habría", "english": "I would have"},
        {"spanish": "habrías", "english": "you would have"},
        {"spanish": "habría", "english": "he/she would have"},
        {"spanish": "habríamos", "english": "we would have"},
        {"spanish": "habríais", "english": "you all would have"},
        {"spanish": "habrían", "english": "they would have"},
    ],
    "present_perfect_subjunctive": [
        {"spanish": "haya", "english": "I have (subj.)"},
        {"spanish": "hayas", "english": "you have (subj.)"},
        {"spanish": "haya", "english": "he/she has (subj.)"},
        {"spanish": "hayamos", "english": "we have (subj.)"},
        {"spanish": "hayáis", "english": "you all have (subj.)"},
        {"spanish": "hayan", "english": "they have (subj.)"},
    ],
    "past_perfect_subjunctive": [
        {"spanish": "hubiera", "english": "I had (subj.)"},
        {"spanish": "hubieras", "english": "you had (subj.)"},
        {"spanish": "hubiera", "english": "he/she had (subj.)"},
        {"spanish": "hubiéramos", "english": "we had (subj.)"},
        {"spanish": "hubierais", "english": "you all had (subj.)"},
        {"spanish": "hubieran", "english": "they had (subj.)"},
    ],

    # Progressive tenses use "estar"
    "present_progressive": [
        {"spanish": "estoy", "english": "I am"},
        {"spanish": "estás", "english": "you are"},
        {"spanish": "está", "english": "he/she is"},
        {"spanish": "estamos", "english": "we are"},
        {"spanish": "estáis", "english": "you all are"},
        {"spanish": "están", "english": "they are"},
    ],
    "past_progressive": [
        {"spanish": "estaba", "english": "I was"},
        {"spanish": "estabas", "english": "you were"},
        {"spanish": "estaba", "english": "he/she was"},
        {"spanish": "estábamos", "english": "we were"},
        {"spanish": "estabais", "english": "you all were"},
        {"spanish": "estaban", "english": "they were"},
    ],

    # Modal constructions
    "deber_infinitive": [
        {"spanish": "debo", "english": "I must/should"},
        {"spanish": "debes", "english": "you must/should"},
        {"spanish": "debe", "english": "he/she must/should"},
        {"spanish": "debemos", "english": "we must/should"},
        {"spanish": "debéis", "english": "you all must/should"},
        {"spanish": "deben", "english": "they must/should"},
    ],
    "poder_infinitive": [
        {"spanish": "puedo", "english": "I can"},
        {"spanish": "puedes", "english": "you can"},
        {"spanish": "puede", "english": "he/she can"},
        {"spanish": "podemos", "english": "we can"},
        {"spanish": "podéis", "english": "you all can"},
        {"spanish": "pueden", "english": "they can"},
    ],
    "querer_infinitive": [
        {"spanish": "quiero", "english": "I want"},
        {"spanish": "quieres", "english": "you want"},
        {"spanish": "quiere", "english": "he/she wants"},
        {"spanish": "queremos", "english": "we want"},
        {"spanish": "queréis", "english": "you all want"},
        {"spanish": "quieren", "english": "they want"},
    ],
    "tener_que_infinitive": [
        {"spanish": "tengo que", "english": "I have to"},
        {"spanish": "tienes que", "english": "you have to"},
        {"spanish": "tiene que", "english": "he/she has to"},
        {"spanish": "tenemos que", "english": "we have to"},
        {"spanish": "tenéis que", "english": "you all have to"},
        {"spanish": "tienen que", "english": "they have to"},
    ],
    "necesitar_infinitive": [
        {"spanish": "necesito", "english": "I need to"},
        {"spanish": "necesitas", "english": "you need to"},
        {"spanish": "necesita", "english": "he/she needs to"},
        {"spanish": "necesitamos", "english": "we need to"},
        {"spanish": "necesitáis", "english": "you all need to"},
        {"spanish": "necesitan", "english": "they need to"},
    ],
    "ir_a_infinitive": [
        {"spanish": "voy a", "english": "I am going to"},
        {"spanish": "vas a", "english": "you are going to"},
        {"spanish": "va a", "english": "he/she is going to"},
        {"spanish": "vamos a", "english": "we are going to"},
        {"spanish": "vais a", "english": "you all are going to"},
        {"spanish": "van a", "english": "they are going to"},
    ],

    # Passive with "ser"
    "passive_ser": [
        {"spanish": "soy", "english": "I am"},
        {"spanish": "eres", "english": "you are"},
        {"spanish": "es", "english": "he/she is"},
        {"spanish": "somos", "english": "we are"},
        {"spanish": "sois", "english": "you all are"},
        {"spanish": "son", "english": "they are"},
    ],
    "passive_estar": [
        {"spanish": "estoy", "english": "I am"},
        {"spanish": "estás", "english": "you are"},
        {"spanish": "está", "english": "he/she is"},
        {"spanish": "estamos", "english": "we are"},
        {"spanish": "estáis", "english": "you all are"},
        {"spanish": "están", "english": "they are"},
    ],

    # Reflexive pronouns
    "reflexive": [
        {"spanish": "me", "english": "myself"},
        {"spanish": "te", "english": "yourself"},
        {"spanish": "se", "english": "himself/herself"},
        {"spanish": "nos", "english": "ourselves"},
        {"spanish": "os", "english": "yourselves"},
        {"spanish": "se", "english": "themselves"},
    ],

    # These don't need helper conjugations - they modify the main verb directly
    # "present_subjunctive": None,
    # "imperfect_subjunctive": None,
    # "conditional": None,
    # "imperative_affirmative": None,
    # "imperative_negative": None,
}


def get_extra_infos(additional_elements: list) -> list:
    """Get extra_infos for the given additional elements."""
    extra_infos = []
    for element in additional_elements:
        if element in HELPER_CONJUGATIONS:
            extra_infos.extend(HELPER_CONJUGATIONS[element])
    return extra_infos

# =============================================================================
# YAML HEADER/README
# =============================================================================

YAML_HEADER = """# =============================================================================
# SENTENCES.YAML - Spanish Sentence Generation Practice
# =============================================================================
#
# PURPOSE:
# This file contains word/verb combinations for generating Spanish sentences.
# Each entry provides the building blocks for creating practice sentences.
#
# HOW TO USE:
# 1. For each entry, construct a Spanish sentence that:
#    - Uses the specified word (noun/adjective/etc from common.yaml)
#    - Uses the specified verb conjugated in the specified basic tense
#    - Incorporates the additional_elements in a natural way
#
# 2. IMPORTANT: Generate the Spanish sentence FIRST, then translate to English.
#    This ensures natural Spanish construction rather than literal translation.
#
# 3. IMPORTANT: The sentence must include BOTH:
#    - The main verb conjugated in the basic tense (present/preterite/imperfect/future)
#    - AND the additional_elements constructions (if any)
#    The additional_elements should NOT replace the basic verb+tense usage.
#    For example, if verb=comer, tense=present, additional=deber_infinitive:
#    CORRECT: "Debo comer más verduras, pero como muy rápido." (uses both debo+inf AND como)
#    WRONG: "Debo comer más verduras." (only uses deber+infinitive, missing present tense)
#
# 4. The additional_elements list contains advanced grammatical constructions
#    that should be woven into the sentence. For example:
#    - "present_perfect" -> use "haber + past participle" (he comido)
#    - "deber_infinitive" -> use "deber + infinitive" (debo comer)
#    - "present_subjunctive" -> use subjunctive mood (que coma)
#
# FIELDS:
# - word: Key referencing an entry in common.yaml
# - verb: Key referencing an entry in verbs.yaml
# - tense: One of the basic tenses (present, preterite, imperfect, future)
# - additional_elements: List of advanced constructions to incorporate
# - extra_infos: Optional list of {spanish, english} pairs providing helper verb
#   conjugations needed for the additional_elements (e.g., "puedo/I can" for poder)
# - spanish: "<placeholder>" - Replace with generated Spanish sentence
# - english: "<placeholder>" - Replace with English translation
#
# =============================================================================

"""


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_sentence_entries(word_keys: list, verb_keys: list, basic_tenses: list) -> list:
    """
    Generate sentence entries ensuring each word and each verb+tense combo is used at least once.

    Args:
        word_keys: List of keys from common.yaml
        verb_keys: List of keys from verbs.yaml
        basic_tenses: List of basic tenses to use

    Returns:
        List of sentence entry dictionaries
    """
    # Create all verb+tense combinations
    verb_tense_combos = [(verb, tense) for verb in verb_keys for tense in basic_tenses]

    # Shuffle both lists for randomness
    words_shuffled = word_keys.copy()
    random.shuffle(words_shuffled)

    combos_shuffled = verb_tense_combos.copy()
    random.shuffle(combos_shuffled)

    entries = []

    # Determine how many entries we need (at least enough to cover both lists)
    num_entries = max(len(words_shuffled), len(combos_shuffled))

    # Create cycling iterators for the shorter list
    if len(words_shuffled) < len(combos_shuffled):
        words_iter = cycle(words_shuffled)
        combos_iter = iter(combos_shuffled)
    else:
        words_iter = iter(words_shuffled)
        combos_iter = cycle(combos_shuffled)

    for i in range(num_entries):
        word_key = next(words_iter)
        verb_key, tense = next(combos_iter)

        # Randomly select 0-2 additional elements
        num_additional = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
        additional = random.sample(ADDITIONAL_ELEMENTS, min(num_additional, len(ADDITIONAL_ELEMENTS)))

        # Get extra_infos for additional elements that need helper conjugations
        extra_infos = get_extra_infos(additional)

        entry = {
            'word': word_key,
            'verb': verb_key,
            'tense': tense,
            'additional_elements': additional,
            'extra_infos': extra_infos if extra_infos else None,
            'spanish': '<placeholder>',
            'english': '<placeholder>',
        }
        entries.append(entry)

    return entries


class NoAliasDumper(yaml.SafeDumper):
    """Custom YAML dumper that doesn't use anchors/aliases for duplicate data."""
    def ignore_aliases(self, data):
        return True


def save_sentences_yaml(entries: list, filepath: Path):
    """Save sentence entries to YAML file with header."""
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write the header/readme
        f.write(YAML_HEADER)

        # Write entries as a YAML list (without anchor/alias references)
        yaml.dump(
            {'sentences': entries},
            f,
            Dumper=NoAliasDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )


def main():
    random.seed(42)  # For reproducibility; remove for true randomness

    words_dir = Path(__file__).parent.parent / "words"
    common_file = words_dir / "common.yaml"
    verbs_file = words_dir / "verbs.yaml"
    sentences_file = words_dir / "sentences.yaml"

    # Load existing word files
    print(f"Loading {common_file}...")
    common_data = load_yaml(common_file)
    word_keys = list(common_data.keys())
    print(f"  Found {len(word_keys)} words")

    print(f"Loading {verbs_file}...")
    verbs_data = load_yaml(verbs_file)
    verb_keys = list(verbs_data.keys())
    print(f"  Found {len(verb_keys)} verbs")

    # Calculate expected entries
    verb_tense_count = len(verb_keys) * len(BASIC_TENSES)
    expected_entries = max(len(word_keys), verb_tense_count)
    print(f"\nGenerating sentences...")
    print(f"  Words: {len(word_keys)}")
    print(f"  Verb+tense combinations: {verb_tense_count}")
    print(f"  Total entries to generate: {expected_entries}")

    # Generate entries
    entries = generate_sentence_entries(word_keys, verb_keys, BASIC_TENSES)

    # Save to file
    print(f"\nSaving to {sentences_file}...")
    save_sentences_yaml(entries, sentences_file)

    # Print summary
    print(f"\nGenerated {len(entries)} sentence entries")
    print(f"  Each word used at least once: {len(set(e['word'] for e in entries)) == len(word_keys)}")

    # Check verb+tense coverage
    used_combos = set((e['verb'], e['tense']) for e in entries)
    expected_combos = set((v, t) for v in verb_keys for t in BASIC_TENSES)
    print(f"  Each verb+tense used at least once: {used_combos == expected_combos}")

    # Additional elements stats
    with_additional = sum(1 for e in entries if e['additional_elements'])
    print(f"  Entries with additional elements: {with_additional} ({100*with_additional/len(entries):.1f}%)")

    print("\nDone!")


if __name__ == "__main__":
    main()
