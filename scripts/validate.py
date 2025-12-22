#!/usr/bin/env python3
"""
Script to consolidate gendered words and validate Spanish word files.
"""

import yaml
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Optional
import re

from generate_sentences import ADDITIONAL_ELEMENTS, BASIC_TENSES


class WordEntry(BaseModel):
    """Model for a single word/phrase entry.
    
    Can be a single word, or an idiomatic phrase that encodes one indivisible concept (e.g. "ya que meaning since, but not being able to be decomposed into ya and que")"""
    spanish: str | list[str]  # Can be single word or list for gendered forms
    english: list[str] # Should contain at least one translation, but may contain multiple if the spanish word has multiple distinct translations
    form: str # "noun", "adjective", "pronoun", "verb", "adverb", "preposition", "conjunction", "interjection"

    @field_validator('english')
    @classmethod
    def english_not_empty(cls, v):
        if not v:
            raise ValueError('english translations cannot be empty')
        return v


class VerbConjugations(BaseModel):
    """Model for verb conjugations in a single tense."""
    yo: str
    tú: str
    él: str
    nosotros: str
    vosotros: str
    ellos: str


# Required tenses for verb conjugations (imported from generate_sentences.py)
REQUIRED_TENSES = set(BASIC_TENSES)

# Valid additional elements for sentence entries (imported from generate_sentences.py)
VALID_ADDITIONAL_ELEMENTS = set(ADDITIONAL_ELEMENTS)


class VerbEntry(BaseModel):
    """Model for a verb entry with conjugations."""
    spanish: str
    english: list[str] # Should contain at least one translation, but may contain multiple if the spanish word has multiple distinct translations
    conjugations: dict[str, VerbConjugations]

    @field_validator('english')
    @classmethod
    def english_not_empty(cls, v):
        if not v:
            raise ValueError('english translations cannot be empty')
        return v

    @field_validator('conjugations')
    @classmethod
    def has_all_tenses(cls, v):
        missing = REQUIRED_TENSES - set(v.keys())
        if missing:
            raise ValueError(f'missing required tenses: {", ".join(sorted(missing))}')
        return v


class ExtraInfo(BaseModel):
    """Model for extra info entries (helper verb conjugations)."""
    spanish: str
    english: str


class SentenceEntry(BaseModel):
    """Model for a sentence practice entry."""
    word: str  # Key referencing common.yaml
    verb: str  # Key referencing verbs.yaml
    tense: str  # One of the basic tenses
    additional_elements: list[str]  # List of advanced constructions
    extra_infos: Optional[list[ExtraInfo]]  # Helper conjugations for additional elements
    spanish: str  # The Spanish sentence (or placeholder)
    english: str  # The English translation (or placeholder)

    @field_validator('tense')
    @classmethod
    def valid_tense(cls, v):
        if v not in REQUIRED_TENSES:
            raise ValueError(f'invalid tense "{v}", must be one of: {", ".join(sorted(REQUIRED_TENSES))}')
        return v

    @field_validator('additional_elements')
    @classmethod
    def valid_additional_elements(cls, v):
        invalid = set(v) - VALID_ADDITIONAL_ELEMENTS
        if invalid:
            raise ValueError(f'invalid additional elements: {", ".join(sorted(invalid))}')
        return v


class SentenceEntryComplete(SentenceEntry):
    """Model for a completed sentence entry (no placeholders allowed)."""

    @field_validator('spanish')
    @classmethod
    def spanish_not_placeholder(cls, v):
        if '<placeholder>' in v.lower():
            raise ValueError('spanish field still contains placeholder')
        return v

    @field_validator('english')
    @classmethod
    def english_not_placeholder(cls, v):
        if '<placeholder>' in v.lower():
            raise ValueError('english field still contains placeholder')
        return v


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


class QuotedString(str):
    """A string that will be quoted in YAML output."""
    pass


def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')


yaml.add_representer(QuotedString, quoted_str_representer)


def quote_problematic_values(data: dict) -> dict:
    """Quote values that YAML might misinterpret as booleans."""
    problematic = {'true', 'false', 'yes', 'no', 'on', 'off', 'null'}

    def process_value(v):
        if isinstance(v, str) and v.lower() in problematic:
            return QuotedString(v)
        elif isinstance(v, list):
            return [process_value(item) for item in v]
        elif isinstance(v, dict):
            return {k: process_value(val) for k, val in v.items()}
        return v

    return {k: process_value(v) for k, v in data.items()}


def save_yaml(data: dict, filepath: Path):
    """Save data to a YAML file."""
    # Quote problematic values before saving
    quoted_data = quote_problematic_values(data)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(quoted_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def validate_common_words(data: dict, expected_count: int = 1000) -> tuple[bool, list[str]]:
    """Validate common words file."""
    errors = []

    # Check count
    actual_count = len(data)
    if actual_count != expected_count:
        errors.append(f"Expected {expected_count} entries, found {actual_count}")

    # Validate each entry
    for key, value in data.items():
        try:
            WordEntry(**value)
        except Exception as e:
            errors.append(f"Entry '{key}': {e}")

    return len(errors) == 0, errors


def validate_verbs(data: dict, expected_count: int = 300) -> tuple[bool, list[str]]:
    """Validate verbs file."""
    errors = []

    # Check count
    actual_count = len(data)
    if actual_count != expected_count:
        errors.append(f"Expected {expected_count} entries, found {actual_count}")

    # Validate each entry
    for key, value in data.items():
        try:
            VerbEntry(**value)
        except Exception as e:
            errors.append(f"Entry '{key}': {e}")

    return len(errors) == 0, errors


def validate_sentences(
    data: dict,
    word_keys: set[str],
    verb_keys: set[str],
    check_complete: bool = False,
) -> tuple[bool, list[str]]:
    """Validate sentences file.

    Args:
        data: The sentences data dict
        word_keys: Set of valid word keys from common.yaml
        verb_keys: Set of valid verb keys from verbs.yaml
        check_complete: If True, also verify no placeholders remain in spanish/english fields
    """
    errors = []

    sentences = data.get('sentences', [])
    if not sentences:
        errors.append("No sentences found in file")
        return False, errors

    # Choose the appropriate model based on check_complete
    EntryModel = SentenceEntryComplete if check_complete else SentenceEntry

    # Track coverage
    used_words = set()
    used_verb_tenses = set()

    for i, entry in enumerate(sentences):
        try:
            EntryModel(**entry)

            # Check that word key exists in common.yaml
            if entry['word'] not in word_keys:
                errors.append(f"Entry {i}: word '{entry['word']}' not found in common.yaml")

            # Check that verb key exists in verbs.yaml
            if entry['verb'] not in verb_keys:
                errors.append(f"Entry {i}: verb '{entry['verb']}' not found in verbs.yaml")

            used_words.add(entry['word'])
            used_verb_tenses.add((entry['verb'], entry['tense']))

        except Exception as e:
            errors.append(f"Entry {i}: {e}")

    # Check coverage
    missing_words = word_keys - used_words
    if missing_words:
        errors.append(f"Words not used in any sentence: {len(missing_words)} words missing")

    expected_verb_tenses = {(v, t) for v in verb_keys for t in REQUIRED_TENSES}
    missing_verb_tenses = expected_verb_tenses - used_verb_tenses
    if missing_verb_tenses:
        errors.append(f"Verb+tense combos not used: {len(missing_verb_tenses)} missing")

    return len(errors) == 0, errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate Spanish word files")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow placeholders in spanish/english fields (by default, placeholders are not allowed)",
    )
    args = parser.parse_args()

    words_dir = Path(__file__).parent.parent / "words"
    common_file = words_dir / "common.yaml"
    verbs_file = words_dir / "verbs.yaml"
    sentences_file = words_dir / "sentences.yaml"

    word_keys = set()
    verb_keys = set()

    # Load and validate common words
    if common_file.exists():
        print(f"Loading {common_file}...")
        data = load_yaml(common_file)
        word_keys = set(data.keys())

        print(f"Current entry count: {len(data)}")

        # make sure we have exactly 1000 entries
        assert len(data) == 1000

        # Validate
        is_valid, errors = validate_common_words(data)
        if is_valid:
            print("✓ Common words file is valid!")
        else:
            print("✗ Validation errors:")
            for error in errors[:20]:  # Show first 20 errors
                print(f"  - {error}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors")

    # Validate verbs file if it exists
    if verbs_file.exists():
        print(f"\nLoading {verbs_file}...")
        verbs_data = load_yaml(verbs_file)
        verb_keys = set(verbs_data.keys())
        assert len(verbs_data) == 300

        is_valid, errors = validate_verbs(verbs_data)
        if is_valid:
            print("✓ Verbs file is valid!")
        else:
            print("✗ Validation errors:")
            for error in errors[:20]:
                print(f"  - {error}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors")
    else:
        print(f"\nVerbs file not found: {verbs_file}")

    # Validate sentences file if it exists
    if sentences_file.exists():
        print(f"\nLoading {sentences_file}...")
        sentences_data = load_yaml(sentences_file)
        num_sentences = len(sentences_data.get('sentences', []))
        print(f"Current entry count: {num_sentences}")

        if args.allow_incomplete:
            print("(Allowing incomplete sentences - placeholders permitted)")

        is_valid, errors = validate_sentences(
            sentences_data, word_keys, verb_keys, check_complete=not args.allow_incomplete
        )
        if is_valid:
            print("✓ Sentences file is valid!")
        else:
            print("✗ Validation errors:")
            for error in errors[:20]:
                print(f"  - {error}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors")
    else:
        print(f"\nSentences file not found: {sentences_file}")


if __name__ == "__main__":
    main()
