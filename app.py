import os
import re
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

# ============================================================
# CONFIGURATION
# ============================================================
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="ApplyEasy - Resume to Cover Letter",
    page_icon="📄",
    layout="wide"
)

if not API_KEY:
    st.error(
        "GROQ_API_KEY is missing. Please add it to your .env file. "
        "Get a free key from https://console.groq.com"
    )
    st.stop()

client = Groq(api_key=API_KEY)
MODEL = "openai/gpt-oss-120b"

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 17px;
        color: #888;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">ApplyEasy 📄</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Turn your resume into a tailored cover letter and '
    'LinkedIn summary in seconds.</div>',
    unsafe_allow_html=True
)

# ============================================================
# HELPERS
# ============================================================
def extract_resume_text(uploaded_file):
    """Extract raw text from an uploaded PDF resume."""
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def clean_text(text):
    """Collapse extra whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def generate_application_content(resume_text, job_title, company_name, tone):
    """Ask the LLM for a cover letter and a LinkedIn 'About' summary."""
    company_line = f"Company: {company_name}" if company_name.strip() else "Company: (not specified)"

    prompt = f"""
You are an expert career coach helping a candidate apply for a job.

Candidate resume (extracted text):
{resume_text}

Job title applying for: {job_title}
{company_line}
Desired tone: {tone}

Write two things clearly separated:

1. COVER LETTER:
   - 3-4 short paragraphs.
   - Personalized using real details from the resume (skills, projects, experience).
   - Written in a {tone.lower()} tone.
   - Do not invent experience that isn't in the resume.
   - End with a professional closing line.

2. LINKEDIN SUMMARY:
   - A short "About" section for LinkedIn, 4-6 sentences.
   - First person, engaging, highlights key skills and career goal.

Format your response exactly like this, with these headers and nothing else before/after:

===COVER LETTER===
<cover letter text here>

===LINKEDIN SUMMARY===
<linkedin summary text here>
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional career coach and writing assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6
    )
    return response.choices[0].message.content


def parse_output(raw_text):
    """Split the model's response into cover letter and LinkedIn summary."""
    cover_letter = ""
    linkedin_summary = ""

    cover_match = re.search(
        r"===COVER LETTER===(.*?)(===LINKEDIN SUMMARY===|$)",
        raw_text,
        re.DOTALL
    )
    linkedin_match = re.search(
        r"===LINKEDIN SUMMARY===(.*)",
        raw_text,
        re.DOTALL
    )

    if cover_match:
        cover_letter = cover_match.group(1).strip()
    if linkedin_match:
        linkedin_summary = linkedin_match.group(1).strip()

    # Fallback: if parsing fails, just show the raw text as the cover letter
    if not cover_letter and not linkedin_summary:
        cover_letter = raw_text.strip()

    return cover_letter, linkedin_summary


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("About")
    st.write(
        "ApplyEasy reads your resume and generates a tailored cover letter "
        "and LinkedIn summary using Generative AI, so you don't have to "
        "write one from scratch every time you apply."
    )
    st.divider()
    st.subheader("Tech Stack")
    st.write("Python\nStreamlit\nGroq LLM\nPyPDF\nPrompt Engineering")

# ============================================================
# MAIN INPUTS
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

with col2:
    st.subheader("2. Job Details")
    job_title = st.text_input("Job title you're applying for", placeholder="e.g. Trainee Software Engineer")
    company_name = st.text_input("Company name (optional)", placeholder="e.g. Infosys")
    tone = st.selectbox("Tone", ["Professional", "Confident", "Friendly", "Formal"])

st.divider()
generate_button = st.button("Generate Cover Letter", type="primary", use_container_width=True)

# ============================================================
# PROCESS
# ============================================================
if generate_button:
    if uploaded_file is None:
        st.warning("Please upload your resume PDF.")
        st.stop()
    if not job_title.strip():
        st.warning("Please enter the job title you're applying for.")
        st.stop()

    with st.spinner("Reading your resume and writing your cover letter..."):
        try:
            resume_text = extract_resume_text(uploaded_file)
            resume_text = clean_text(resume_text)

            if len(resume_text) < 50:
                st.error("Very little text could be read from this PDF. Please upload a text-based resume PDF.")
                st.stop()

            raw_output = generate_application_content(resume_text, job_title, company_name, tone)
            cover_letter, linkedin_summary = parse_output(raw_output)

            st.session_state["cover_letter"] = cover_letter
            st.session_state["linkedin_summary"] = linkedin_summary
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

# ============================================================
# DISPLAY RESULTS
# ============================================================
if "cover_letter" in st.session_state:
    st.divider()
    st.header("Your Generated Application Content")

    tab1, tab2 = st.tabs(["📝 Cover Letter", "💼 LinkedIn Summary"])

    with tab1:
        st.text_area("Cover Letter", st.session_state["cover_letter"], height=350)
        st.download_button(
            "Download Cover Letter (.txt)",
            st.session_state["cover_letter"],
            file_name="cover_letter.txt",
            mime="text/plain"
        )

    with tab2:
        st.text_area("LinkedIn About Summary", st.session_state["linkedin_summary"], height=200)
        st.download_button(
            "Download LinkedIn Summary (.txt)",
            st.session_state["linkedin_summary"],
            file_name="linkedin_summary.txt",
            mime="text/plain"
        )

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("ApplyEasy | Python + Streamlit + Groq")
