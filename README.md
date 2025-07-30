# CivicBridge (Web App v2): AI‑Powered, Privacy‑First Policy Explainer

CivicBridge is a **full‑stack web application** that helps people understand how government policies affect them, find their elected representatives, and get plain‑English answers powered by AI. It combines **live government data** with the **Google Gemini API** to translate complex policy language into clear explanations.

> **Privacy first:** CivicBridge does **not** use login/registration. We avoid storing sensitive personal data to reduce risk for the communities we serve.

---

## Why No Login? (Privacy‑First Rationale)
- Many users we serve (immigrants, mixed‑status families, low‑income households) face **real risks** from account‑linked data.
- In an era of frequent **security breaches** and **low institutional trust**, collecting the minimum data necessary is the safest path.
- No accounts = less data retained, smaller attack surface, easier compliance.
- We only request lightweight, **contextual inputs** (e.g., ZIP code, role) to personalize answers during a session.

---

## Problem
- Policies are written in dense legal language; most people struggle to parse impact.
- It’s hard to know **which** policies apply to you locally.
- Finding and understanding **representative activity** (sponsored/cosponsored bills, votes) is fragmented.
- General AI tools can explain text, but they often **lack live data**, civic focus, and personal context.

---

## Our Solution (Web App v2)
**Four core experiences:**

- **Home** — Enter ZIP, role, and context to get **personalized policy explanations**.
- **Policies** — Browse by topic to see **real federal & congressional items** with plain‑English summaries and links to sources.
- **Representatives** — Enter ZIP to see **who represents you**, how to contact them, and a snapshot of **legislative activity**.
- **Chatbot** — Ask questions and get **concise, AI‑powered** answers in real time.

---

## Features
### Representatives Hub
- Lookup by **ZIP code** (Geocodio → district)  
- Contact details and **legislative activity** (sponsored / cosponsored) via Congress API

### Policy Explorer
- Browse policies by **topic**
- Pulls recent policy items from **Federal Register** and **Congress** sources
- Plain‑English summaries with links to official sources

### AI Assistant
- Powered by **Google Gemini API**
- Explains bills, policies, and civic processes in **simple language**
- Can tailor answers to user context (ZIP, role, etc.)

### Privacy & Safety
- **No login** and minimal data retention
- Simple session state for chat; no sensitive PII stored

---

## Tech Stack
**Frontend**
- React (**Create React App**)
- TailwindCSS + ShadCN UI

**Backend**
- Python **Flask**
- **SQLite** (lightweight cache / chat history)
- REST/JSON endpoints + CORS

**APIs**
- **Google Gemini API** (policy & chat explanations)
- **Congress.gov API** (bills, members, activity)
- **Federal Register API** (regulations & notices)
- **Geocodio API** (ZIP → district/representatives)

---

## Architecture (High‑Level)
```
Client (CRA/React)  ──►  Flask API  ──►  Gemini (AI)
       │                     │        └─►  Congress.gov / Federal Register / Geocodio
       └────────────── CORS ─┘
```
- Client collects lightweight context → sends to Flask  
- Flask fetches **live data**, builds a compact prompt, calls **Gemini**  
- Response rendered as **plain‑English** summaries and chat answers

---

## Getting Started

### 1) Prerequisites
- Python **3.10+**
- Node **18+** / npm **9+**

### 2) Clone
```bash
git clone <your-repo-url>
cd civicbridge
```

### 3) Backend Setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# .env (create in backend/)
GOOGLE_GENAI_API_KEY=your_gemini_api_key
CONGRESS_API_KEY=your_congress_api_key
GEOCODIO_API_KEY=your_geocodio_api_key
# Optional: FEDERAL_REGISTER_BASE=https://www.federalregister.gov/api/v1
FLASK_ENV=development
```

Run the server:
```bash
python server.py   # or: flask run (port 5000 by default)
```

### 4) Frontend Setup
```bash
cd ../client
npm install

# .env (create in client/)
REACT_APP_BACKEND_URL=http://localhost:5000
```

Run the client:
```bash
npm start   # CRA dev server (port 3000 by default)
```

The app should now be available at **http://localhost:3000** and talk to Flask on **http://localhost:5000**.

---

## Environment Variables (Summary)

| Location  | Variable                    | Description                                  |
|---------- |-----------------------------|----------------------------------------------|
| backend   | `GOOGLE_GENAI_API_KEY`      | Google Gemini API key                         |
| backend   | `CONGRESS_API_KEY`          | Congress.gov API key                          |
| backend   | `GEOCODIO_API_KEY`          | Geocodio API key                              |
| client    | `REACT_APP_BACKEND_URL`     | Base URL of the Flask server                  |

> Federal Register API is public; no key required for basic endpoints.

---

## Usage Notes

- Keep inputs **short and specific** when asking about policies.  
- For chat, CivicBridge focuses on **education** and **non‑partisan** explanations.  
- Use **Representatives** to quickly contact your members of Congress.

---

## Troubleshooting

### 429 / Rate‑Limit (Gemini)
If you see an error like:
```
You exceeded your current quota … GenerateRequestsPerMinutePerProjectPerModel-FreeTier
```
This means you exceeded the **free‑tier RPM**. Options:
- Add a small **debounce** (disable the send button briefly) and **throttle** requests.
- Implement **retry with backoff** and honor the server’s suggested `retry_delay`.
- Cache identical prompts or reduce duplicate calls per UI action.
- Consider enabling **billing** or using a lighter model variant for higher throughput.

### Slow responses
- Trim very long policy text before sending to Gemini.  
- Limit chat history to the last 6–8 turns.  
- Use **streaming** to show partial output for better perceived speed.  

### CORS
- Ensure the backend sets appropriate CORS headers for the client origin.

---

## Roadmap
- **Search by topic/policy** with filters (e.g., “healthcare” + income/job)  
- **Action features:** contact reps, sign petitions, join campaigns  
- **Interactive map + chatbot** for local context  
- **Multilingual** explanations

---

## Team
Built by Aayah Osman, Cristian Castellanos, Amen Divine Ikamba
