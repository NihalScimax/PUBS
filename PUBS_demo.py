import streamlit as st
import requests
from PyPDF2 import PdfReader
from fpdf import FPDF
import io

# **Mistral 7B API Endpoint (Replace with your AWS URL)**
MISTRAL_API_URL = "https://arin.scimaxmi.com/api/input/evaluate"

# **Streamlit Page Configuration**
st.set_page_config(page_title="AI PDF Extractor", page_icon="📄", layout="wide")

# **Custom Styling for Font and Layout**
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: #FFFFFF;
        font-size: 16px;
        border-radius: 8px;
    }
    .stFileUploader label {
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
    }
    .big-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 30px;
    }
    .small-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 10px;
        font-size: 12px;
        text-align: left;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# **Title Section**
st.markdown("<h1 class='big-title'>📄 AI-Powered PDF Extractor</h1>", unsafe_allow_html=True)
st.write("### 🚀 Upload a PDF file and enter a custom prompt to extract relevant information.")

# **Layout**
col1, col2 = st.columns([3, 1], gap="large")

with col1:
    uploaded_file = st.file_uploader("📤 Upload your PDF", type="pdf")
    user_prompt = st.text_input("✏️ Enter your query (e.g., 'Extract details about XYZ')", "")

with col2:
    st.markdown("<div class='small-box'>", unsafe_allow_html=True)
    st.markdown("### 🔍 How It Works")
    st.write("1️⃣ Upload a **PDF file**.")
    st.write("2️⃣ Enter a **specific question or topic**.")
    st.write("3️⃣ AI extracts **only the relevant information**.")
    st.write("4️⃣ Download your **customized PDF**.")
    st.markdown("</div>", unsafe_allow_html=True)

TOKEN_LIMIT = 1000  # Adjust based on Mistral’s max token limit

def extract_text_from_pdf(pdf_stream):
    """Extract text from a PDF file and return as chunks."""
    reader = PdfReader(pdf_stream)
    chunks = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            for i in range(0, len(text), TOKEN_LIMIT):
                chunk_content = text[i:i + TOKEN_LIMIT].strip()
                if chunk_content:
                    chunks.append({"page_number": page_number + 1, "content": chunk_content})

    return chunks

def request_mistral(text, query):
    """Send text to Mistral API for processing with a custom prompt."""
    prompt = f"<s>Text:{text} [INST]{query}[/INST]</s>"
    payload = {
        "prompt": prompt,
        "temperature": 0.5,
        "top_p": 0.7,
        "top_k": 50,
        "no_repeat_ngram_size": 2
    }

    try:
        response = requests.post(MISTRAL_API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No text generated")
        else:
            return f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def extract_relevant_text(chunks, query):
    """Extract relevant text from PDF using the LLM based on user query."""
    relevant_text = []
    progress_bar = st.progress(0)

    for i, chunk in enumerate(chunks):
        extracted_content = request_mistral(chunk['content'], query)
        relevant_text.append({"page_number": chunk['page_number'], "content": extracted_content})

        # Update progress bar
        progress = (i + 1) / len(chunks)
        progress_bar.progress(progress)

    return relevant_text

def generate_pdf(pages):
    """Generate a PDF with extracted text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    for page in pages:
        pdf.add_page()
        pdf.multi_cell(0, 8, page['content'])

    output_buffer = io.BytesIO()
    
    # ✅ FIX: Correctly write PDF output to BytesIO
    pdf_content = pdf.output(dest="S").encode("latin1")  # Convert to byte stream
    output_buffer.write(pdf_content)
    output_buffer.seek(0)

    return output_buffer

# **Streamlit Workflow**
if uploaded_file is not None:
    if user_prompt.strip() == "":
        st.warning("⚠️ Please enter a query to extract specific information.")
    else:
        st.markdown("### ⏳ Processing your PDF... Please wait.")

        with st.spinner("Extracting text..."):
            text_chunks = extract_text_from_pdf(uploaded_file)

        with st.spinner("Extracting relevant details using AI..."):
            relevant_text = extract_relevant_text(text_chunks, user_prompt)

        with st.spinner("Generating the final PDF..."):
            final_pdf = generate_pdf(relevant_text)

        # **Provide Download Link**
        st.success("✅ Extraction Complete! 🎉")
        st.download_button("📥 Download Your Extracted PDF", final_pdf, "extracted.pdf", "application/pdf")

else:
    st.info("📂 Please upload a PDF file to begin.")
