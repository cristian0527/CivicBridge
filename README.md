# CivicBridge: AI-Powered Policy Explainer (CLI MVP)

CivicBridge is a command-line Python tool that helps users understand how government policies affect them. By combining public policy input, basic user context, and AI-powered language generation, CivicBridge generates personalized, plain-English explanations of complex policies.

This is a simplified MVP built to meet the Week 2 project requirements.

## Problem

- Government policies are often written in complex legal language.
- Citizens don’t know which policies actually affect them.
- News is overwhelming and lacks personal relevance.

## Solution

CivicBridge asks users for basic info (zip code, role) and a policy title or summary. It then uses the Google GenAI API to generate a personalized explanation of how that policy might affect them — all through a command-line interface.

## Features

- Collects user profile and policy input via CLI
- Uses Google GenAI API to translate policy text into simple summaries
- Stores user profiles and generated responses in a SQLite database
- Includes unit tests and GitHub Actions for continuous integration
- Follows PEP8 code style standards

## How It Works

1. User runs the tool and inputs:
   - Zip code
   - Occupation or role
   - A policy summary or title
2. SQLite stores the user's profile and query
3. Google GenAI is prompted with the user + policy context
4. The simplified explanation is returned and saved
5. Output is printed in the CLI and stored in the database

## Tech Stack

- Backend: Python + Flask
- Database: SQLite
- AI Integration: Google GenAI (text summarization)
- External APIs:
  - GovInfo
  - Federal Register
  - Congress.gov
  - Census API
  - BLS API
- CI/CD: GitHub Actions (PEP8 + Unit Tests)

## Risks

- Potential misinterpretation of legal or policy text by the AI model
- User-policy matching logic may not capture nuance in all edge cases

## Success Metrics

- Accurate outputs for 10 or more sample policies

## Team

- Aayah Osman
- Amen Divine Ikamba