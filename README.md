# CivicBridge: AI-Powered Civic Education Platform  

CivicBridge is a full-stack web application that helps citizens understand government policies, connect with their representatives, and engage with the democratic process. By combining real-time government data with AI-powered explanations, it makes complex federal legislation and policies accessible to everyone.  

---

## Problem  

- Government policy is often written in complex legal or bureaucratic language  
- Citizens don't know which policies affect them or how to contact their representatives  
- There's a lack of accessible, personalized civic information for everyday citizens  
- Finding relevant legislation and understanding representative voting records is difficult  

---

## Solution  

CivicBridge provides an intuitive web platform where users can:  

- Find their representatives by ZIP code and view their legislative activity  
- Explore federal policies by category with AI-powered explanations  
- Chat with an AI assistant that explains bills, policies, and civic processes  
- Get personalized explanations based on their role and circumstances  

---

## Features  

### 🏛️ Representatives Hub  
- Find congressional representatives and senators by ZIP code  
- View detailed profiles with contact information and recent activity  
- Browse sponsored and cosponsored legislation with status updates  
- Access voting records and legislative positions  

### 📜 Policy Explorer  
- Browse federal policies by category (Healthcare, Education, Housing, etc.)  
- Search for specific legislation or regulations  
- View recent policies from Federal Register and Congress  
- Get summaries and links to official government sources  

### 🤖 AI-Powered Chat Assistant  
- Ask questions about specific bills (e.g., "What is HR 142?")  
- Get explanations tailored to your role (student, parent, veteran, etc.)  
- Generate professional emails to representatives  
- Understand how policies affect your personal circumstances  
- Chat history preserved during sessions  

### 🎯 Smart Data Integration  
- Real-time data from Congress.gov API  
- Federal Register API for current regulations  
- Geocodio API for representative lookup  
- AI explanations in simple, 8th-grade language  

---

## Tech Stack  

### Frontend  
- **React** - Component-based UI framework  
- **Tailwind CSS** - Utility-first styling  
- **React Router** - Client-side routing  

### Backend  
- **Flask** - Python web framework  
- **SQLite** - Local database for chat history and caching  
- **RESTful API** - Clean endpoint design  

### AI & APIs  
- **Google Gemini AI** - Policy explanations and chat responses  
- **Congress.gov API** - Bill data and representative information  
- **Federal Register API** - Federal policies and regulations  
- **Geocodio API** - ZIP code to congressional district mapping  

### Development  
- **Python** - Backend logic and API integrations  
- **JavaScript/JSX** - Frontend components and interactions  
- **CORS** - Cross-origin resource sharing for API calls  

---

## How It Works  

### Representatives Flow  
1. User enters ZIP code on Representatives page  
2. System calls Geocodio API to find congressional district  
3. Displays representative cards with photos and basic info  
4. User clicks on representative to view detailed legislative activity  
5. Congress API provides recent sponsored/cosponsored bills  

### Policy Flow  
1. User navigates to Policies page  
2. Selects a category (Healthcare, Education, etc.) from dropdown  
3. System queries Federal Register and Congress APIs for relevant policies  
4. Results displayed sorted by date (most recent first)  
5. User can search for specific terms or browse categories  

### Chat Flow  
1. User opens chat interface (available on all pages)  
2. AI detects intent (bill inquiry, representative question, etc.)  
3. System fetches relevant government data if needed  
4. AI generates personalized explanation in simple language  
5. Chat history preserved during session  

---
## Installation & Setup  

### Clone the repository  

```bash
git clone [repository-url]
cd civicbridge

cd backend
pip install -r requirements.txt

cd client
npm install

# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend  
cd client
npm start
```
### Set up environment variables
### Add your API keys to .env file
#### GOOGLE_GENAI_API_KEY=your_gemini_api_key  
#### CONGRESS_API_KEY=your_congress_api_key  
#### GEOCODIO_API_KEY=your_geocodio_api_key 





