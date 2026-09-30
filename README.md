# ApplyEasy – Resume to Cover Letter Generator

ApplyEasy reads a candidate's resume (PDF) and, given a job title and
company, generates a tailored cover letter and a short LinkedIn "About"
summary using a Generative AI model — so applicants don't have to write
one from scratch for every job.

## Tech Stack
- Python
- Streamlit (UI)
- Groq API (LLM)
- PyPDF (resume text extraction)
- Prompt Engineering

## Project Structure
```
ApplyEasy/
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Add your Groq API key**
   - Copy `.env.example` to `.env`
   - Get a free API key from https://console.groq.com
   - Replace `your_groq_api_key_here` with your actual key

4. **Run the app**
   ```
   streamlit run app.py
   ```
   Then open http://localhost:8501 in your browser.

## How to Use
1. Upload your resume as a PDF.
2. Enter the job title you're applying for (and optionally the company name).
3. Pick a tone (Professional, Confident, Friendly, Formal).
4. Click **Generate Cover Letter**.
5. View and download both the cover letter and the LinkedIn summary.

## How It Works (for viva/explanation)
```
Resume PDF
    ↓
PyPDF Text Extraction
    ↓
Job Title + Company + Tone
    ↓
Prompt Engineering
    ↓
Groq LLM
    ↓
Cover Letter + LinkedIn Summary
    ↓
Streamlit UI (view + download)
```

The app extracts the resume text, combines it with the job details into a
single structured prompt, and asks the LLM to return two clearly separated
sections (cover letter and LinkedIn summary), which are then parsed and
displayed in the UI.

## Possible Improvements
- Support DOCX resumes in addition to PDF
- Let the user paste a job description for a more targeted letter
- Save generated letters to a history
- Export cover letter directly as a PDF/Word file
