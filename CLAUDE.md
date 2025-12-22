# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Idioma is a Python project (MIT Licensed). The repository is in early development with no source code yet.

## Development Setup

This project uses uv for Python package management. **Always use native uv commands** - never use `uv pip install` or other pip-compatibility commands. Use `uv add`, `uv sync`, `uv run`, etc. instead.

When the project has code, update this file with:
- Build/install commands
- How to run tests
- Linting/formatting commands
- Architecture overview

# Details

`common.yaml` should contain the top 1000 most common non-verb words in Spanish. Check `scripts/validate.py` to see the format they should be saved in. The words in `common.yaml` should be the top 1000 most common used spanish non-verbs to be used for studying spanish. These top 1000 words should be drawn from sources, rather than from the model's internal feeling of what the top 1000 words are. When asked to generate `common.yaml`, first read `scripts/validate.py` to confirm the format of the output.

`verbs.yaml` should contain the top 300 most common spanish verbs, along with their conjugations. Check `scripts/validate.py` to see the format they should be saved in. These top 300 verbs should be drawn from sources, rather than from the model's internal feeling of what the top 300 verbs are. When asked to generate `verbs.yaml`, first read `scripts/validate.py` to confirm the format of the output.

When generating the top 1000 or top 300, the words should be added in batches of 50, rather than the model attempting to add all of them all at once, as it will exceed the output token limit.
Yaml strings should all be quoted as some spanish words may overlap yaml keywords.
