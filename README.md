# CivicBridge: AI-Powered Policy Explainer (CLI MVP)

CivicBridge is a command-line tool that helps users understand how U.S. government policies affect them personally. By combining basic user context with real-time policy data and generative AI, it produces tailored, plain-language explanations of complex federal rules and legislation.

This MVP was developed for the Meta U Capstone Week 2 deliverable.

## Problem

- Government policy is often written in complex legal or bureaucratic language.
- Most people do not know which policies apply to them or how.
- News coverage is overwhelming and rarely personalized.

## Solution

CivicBridge asks users for basic demographic context and a policy of interest. It then uses generative AI to produce a simplified, user-specific explanation. The result is printed to the terminal and saved in a local database for future reference.

## Features

- Interactive command-line interface
- Accepts user profile via prompt or command-line flags
- Users can enter a policy, browse by topic, view recent rules, or search
- Integrates with Google Generative AI for summarization
- Pulls live data from the Federal Register API
- Saves users, queries, and responses to a local SQLite database
- Includes unit tests with coverage for core logic
- Uses GitHub Actions for automated style and test checks

## How It Works

1. The user runs the program via `python3 civicbridge.py` or with flags such as `--explain` or `--history`
2. The program collects user details including zip code, role, age, income, housing status, and healthcare access
3. The user selects or provides a policy title or summary
4. A personalized explanation is generated using the Google GenAI SDK
5. The explanation is printed and stored in the database
6. The user can view a history of responses using the `--history` or `--all` flags

## Tech Stack

- AI Integration: Google Generative AI SDK (text summarization and explanation)
- Database: SQLite (accessed via Python’s sqlite3 module)
- External API:
  - Federal Register (via REST API)
- Testing: Python unittest and unittest.mock
- CI/CD: GitHub Actions (automated linting and unit tests)

## Risks

- Potential misinterpretation of legal or policy text by the AI model
- User-policy matching logic may not capture nuance in all edge cases

## Success Metrics

- Complete functionality for at least 10 policy examples
- Unit tests for core modules pass reliably
- Codebase passes pycodestyle with no PEP8 errors
- GitHub Actions CI passes on push

## Team

- Aayah Osman
- Amen Divine Ikamba
