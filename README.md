# DocuBridge Excel Assistant

## What the App Does and Why It Matters

DocuBridge is an AI-powered assistant that lets you chat with your Excel files. It allows users to upload Excel spreadsheets, ask questions in simple English, and get instant insights, summaries, formulas, and step-by-step instructions. This makes data analysis accessible to everyone, even without advanced Excel skills, and saves time for professionals who want quick answers from their data.

## Technologies Used

- **Flask** — Python web framework for the backend and routing
- **Pandas** — For reading, summarizing, and displaying Excel data
- **Google Gemini API** (or OpenAI, depending on configuration) — For generating AI responses
- **openpyxl** — For reading Excel files
- **Markdown** — For rendering AI responses with formatting
- **HTML/CSS/JavaScript** — For the interactive chat UI
- **Replit** — For beta testing

## How to Install and Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your environment variables:**
   - Create a `.env` file in the root directory.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
4. **Run the app:**
   ```bash
   python backend.py
   ```
5. **Open your browser:**
   - Go to `http://localhost:5000`

## Sample Questions a User Might Ask

- "What are the top 5 countries with the highest vaccination rates in 2023?"
- "Show me the trend for vaccine coverage in Bangladesh from 2017 to 2023."
- "How do I calculate the average value for column E in Excel?"
